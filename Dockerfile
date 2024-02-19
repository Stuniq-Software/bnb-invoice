FROM python:3.12-slim
LABEL authors="abhiram.bsn"
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y gcc tesseract-ocr git libffi-dev

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY . /app

RUN playwright install chromium && playwright install-deps

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]