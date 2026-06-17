FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN chmod +x scripts/start-api-railway.sh
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn pydantic python-multipart

CMD ["scripts/start-api-railway.sh"]
