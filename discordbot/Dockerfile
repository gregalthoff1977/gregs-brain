# Build context must be the REPO ROOT (this service imports mcp/).
FROM python:3.11-slim-bookworm
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

COPY discordbot/requirements.txt ./discordbot-requirements.txt
RUN pip install --no-cache-dir -r discordbot-requirements.txt

COPY mcp/ /app/mcp/
COPY discordbot/ /app/discordbot/

# mcp/ first so its `config`, `db`, `tools`, `vaultfs` modules resolve,
# then discordbot/ for `settings`, `vault`, `ask`.
ENV PYTHONPATH=/app/mcp:/app/discordbot

EXPOSE 8080
CMD ["python", "/app/discordbot/bot.py"]
