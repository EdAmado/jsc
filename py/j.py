import argparse
import scrapy
import os
import json
import subprocess
from scrapy.crawler import CrawlerProcess

class JscSpider(scrapy.Spider):
    name = "jsc"

    def __init__(self, url=None, *args, **kwargs):
        super(JscSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]

    def parse(self, response):
        vals = {}
        specialN = False

        for table in response.css("div.betMiddle"):

            key = "numbers" if not specialN else "special"
            vals[key] = {}

            for row in table.css("ul"):
                li = row.css("li::text").getall()
                
                num = li[0].strip()

                try:
                    ns = int(li[1].strip())
                    ps = round(float(li[2].strip().replace(",", ".")), 3)
                    na = int(li[5].strip())
                except ValueError:
                    print("Error, couldnt translate values into ints/floats")

                vals[key][num] = {
                    "nsaidas": ns,
                    "percsaidas": ps,
                    "nausencias": na
                }

            specialN = True

        page_key = response.url.rstrip("/").split("/")[-1]

        cns = [] 
        
        if "totoloto" in page_key: cns = [5, 1]
        elif "euromilhoes" in page_key: cns = [5, 2]
        elif "EuroDreams" in page_key: cns = [6, 1]

        k1, k2 = cns

        data_dict = vals['numbers']
        sorted_numbers = sorted(data_dict.keys(), key=int)

        total = len(sorted_numbers)
        base = total // k1
        remainder = total % k1

        chunks = []
        start = 0
        for i in range(k1):
            size = base + (1 if i >= (k1 - remainder) else 0)
            chunk = sorted_numbers[start:start+size]
            chunks.append(chunk)
            start += size

        print(chunks)
        results = {"n": [], "s": []}

        best_num = max(sorted_numbers, key=lambda n: data_dict[n]["nausencias"])
        results["n"].append(best_num)

        visited_chunks = set()
        for i, chunk in enumerate(chunks):
            if best_num in chunk:
                visited_chunks.add(i)
                break

        chunk_avgs = []
        for i, chunk in enumerate(chunks):
            if i in visited_chunks:
                continue
            avg = sum(data_dict[n]["percsaidas"] for n in chunk) / len(chunk)
            chunk_avgs.append((i, avg))

        chunk_avgs.sort(key=lambda x: x[1])
        m = len(chunk_avgs)

        low = chunk_avgs[:m//2]
        high = chunk_avgs[m//2:]

        if m % 2 == 1:
            middle = high.pop(0)
            mid_idx = middle[0]
            mid_chunk = chunks[mid_idx]
            best_mid = max(mid_chunk, key=lambda n: data_dict[n]["nausencias"])
            results["n"].append(best_mid)

        for idx, avg in low:
            chunk = chunks[idx]
            candidates = [n for n in chunk if data_dict[n]["percsaidas"] > avg]
            if candidates:
                best = max(candidates, key=lambda n: data_dict[n]["nausencias"])
                results["n"].append(best)

        for idx, avg in high:
            chunk = chunks[idx]
            candidates = [n for n in chunk if data_dict[n]["percsaidas"] < avg]
            if candidates:
                best = max(candidates, key=lambda n: data_dict[n]["nausencias"])
                results["n"].append(best)

        results["n"] = sorted(results["n"])[:k1]

        s_dict = vals["special"]
        s_sorted = sorted(s_dict.items(), key=lambda x: x[1]["nausencias"], reverse=True)

        results["s"] = [int(num) for num, _ in s_sorted[:k2]]

        yield results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="The URL to crawl")
    args = parser.parse_args()

    process = CrawlerProcess(settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "FEEDS": {f"/data/{args.url}.json": {"format": "json", "overwrite": True}},
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "WARNING"
    })

    prefix = "Statistics" if "EuroDreams" in args.url else "SCEstatisticas"
    urlToAccess = f"https://www.jogossantacasa.pt/web/{prefix}/{args.url}"

    process.crawl(JscSpider, url=urlToAccess)
    process.start()

    with open(f"/data/{args.url}.json") as f:
        data = json.load(f)

        item = data[0]
        arg_str = str([list(map(int, item["n"])), item["s"]])

        creds = [v for k, v in os.environ.items() if k.startswith("AUTO_")]

        for i in range(0, len(creds), 2):
            usern = creds[i]
            passw = creds[i+1]

            if usern and passw:
                subprocess.run(["python", "auto.py", "--username", usern, "--password", passw, "--game", args.url.lower(), "--nums", arg_str])
                print("Everything went as planned")