# discordbot — Discord interface to the brain

A third Railway service in this repo. Imports the MCP tool layer directly
(`WriteHandler`, `SearchHandler`, `ReadHandler`, `PostgresVaultFS`) so Discord
capture and retrieval behave identically to Claude over MCP — same RLS, same
frontmatter, same reference syncing.

## Channels
- `#brain-inbox` — every message saved to `/wiki/inbox/` (✅ on success)
- `#brain-ask` — every message answered from the wiki via an Anthropic tool loop
- `#brain-digest` — optional bot-only channel fed by `POST /notify`

## Env vars
| Var | Notes |
|---|---|
| `DISCORD_BOT_TOKEN` | From the Discord developer portal (enable Message Content intent) |
| `ANTHROPIC_API_KEY` | For the ask loop |
| `BRAIN_USER_ID` | Your Supabase auth user id |
| `KB_SLUG` | Knowledge base slug to target |
| `INBOX_CHANNEL_ID` / `ASK_CHANNEL_ID` | Discord channel ids |
| `DIGEST_CHANNEL_ID` | Optional |
| `DATABASE_URL` | Same Postgres as the api/mcp services |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `S3_BUCKET` / `AWS_REGION` | Same as mcp service (read paths may touch S3) |
| `APP_URL` | Web app URL, used for deep links in write confirmations |

## Railway setup
New Service → same GitHub repo → **Root Directory: `/` (repo root)** →
Config file path: `discordbot/railway.toml`. Build context must be repo root
because the Dockerfile copies `mcp/`.
