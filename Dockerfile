FROM python:3.11-alpine

COPY app /app
COPY .env .

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/main.py"]
