FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps firefox

COPY . .

CMD ["python", "py.py"]
