from playwright_stealth import Stealth
from playwright.async_api import async_playwright
from enum import Enum
import sys
import argparse
import ast
import asyncio

class Games(Enum):
    EUROMILHOES = ("euromilhoes", "Euromilhoes", "2.50", "stars_0_")
    TOTOLOTO = ("totoloton", "Totoloto", "1.00", "luckynumbers_")
    EURODREAMS = ("eurodreams", "EuroDreams", "2.50", "extras_0_")

    def __init__(self, display_name, url_name, play_value, special_keyword):
        self.n = display_name
        self.u = url_name
        self.v = play_value
        self.k = special_keyword
        
    def getUrlValue(self):
        return self.u

    def getPlayValue(self):
        return self.v

    def getSpecialNumberKeyword(self):
        return self.k

async def run(username, password, game, nums):
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://www.jogossantacasa.pt/web/login/view")

        await page.fill("input#user", username)
        for char in list(password):
            await page.locator(f"input[name='{char}']").click()
        await page.get_by_role("button", name="Seguinte").click()
        
        balance_text = await page.locator("a.accountBalance strong").inner_text()
        balance_value = float(balance_text.replace(",", '.').replace("€", "").strip())

        if balance_value < float(Games[game].getPlayValue()):
            print(f"Oops no money. You have {balance_value}€")
            await page.locator("a.linkLogout").click()
            await page.waitForTimeout(500)
            sys.exit(1)

        await page.goto(f"https://www.jogossantacasa.pt/web/Jogar{Games[game].getUrlValue()}/")
        await page.waitForTimeout(500)
        specialKeyword = Games[game].getSpecialNumberKeyword()

        [numbers, specials] = parse_nums(nums)

        for n in numbers:
            await page.locator(f"li#numbers_0_{n - 1}").click()

        for s in specials:
            await page.locator(f"li#{specialKeyword}{s - 1}").click()

        await page.locator("input[value='apostar já']").click()
        await page.get_by_role("button", name="Prosseguir com pagamento").click()
        await page.locator("input#declarationStep3").click()
        await page.get_by_role("button", name="Prosseguir com pagamento").click()

        await page.goto("https://www.jogossantacasa.pt/")
        await page.locator("a.linkLogout").click()
        await page.waitForTimeout(500)

        print("Game set")

        await browser.close()

def parse_nums(value: str):
    try:
        data = ast.literal_eval(value)
    except Exception:
        raise argparse.ArgumentTypeError("e.g. [[1,2,3,4,5],[6,7]]")

    if (
        not isinstance(data, list) or
        len(data) != 2 or
        not all(isinstance(x, list) for x in data) or
        not all(isinstance(n, int) for n in data[0]) or
        not all(isinstance(s, int) for s in data[1])
    ):
        raise argparse.ArgumentTypeError("e.g. [[1,2,3,4,5],[6,7]]")
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Playwright test runner")
    parser.add_argument("--username", type=str, required=True, help="Account username")
    parser.add_argument("--password", type=str, required=True, help="Account password")
    parser.add_argument(
        "--game",
        type=str,
        choices=["euromilhoes", "totoloton", "eurodreams"],
        required=True,
        help="Game to play"
    )
    parser.add_argument(
        "--nums",
        type=str,
        required=True,
        help="Numbers array in the form [numbers, specials], e.g. '[[1,2,3,4,5],[6,7]]'"
    )

    args = parser.parse_args()

    asyncio.run(run(args.username, args.password, args.game, args.nums))