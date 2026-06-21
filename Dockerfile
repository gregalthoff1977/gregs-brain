FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN chmod +x scripts/start-api-railway.sh

RUN pip install --upgrade pip

RUN if [ -f api/requirements.txt ]; then pip install -r api/requirements.txt; fi

RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

RUN pip install pyjwt

RUN apt-get update \
  && apt-get install -y --no-install-recommends nodejs npm \
  && npm install -g @anthropic-ai/claude-code \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

CMD ["scripts/start-api-railway.sh"]
