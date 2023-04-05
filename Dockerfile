FROM python:3.11-alpine

COPY app /app
COPY .env .

WORKDIR /app

RUN pip install -r requirements.txt

COPY --chown=root entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]