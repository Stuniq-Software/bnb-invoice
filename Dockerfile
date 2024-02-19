FROM python:3.12-alpine
LABEL authors="abhiram.bsn"
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache gcc g++ musl-dev linux-headers nss chromium tesseract-ocr mupdf make

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY . /app

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]