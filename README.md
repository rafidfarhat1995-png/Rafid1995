# Telegram ↔ Claude Integration

A Telegram bot that connects directly to Anthropic's Claude API, letting you chat with Claude inside any Telegram conversation.

## Features

- Full back-and-forth conversation with Claude (per-user history)
- `/start` — greet the bot and reset history
- `/clear` — wipe your conversation and start fresh
- Configurable model and token limit via environment variables

## Requirements

- Python 3.10+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- An Anthropic API key (from [console.anthropic.com](https://console.anthropic.com))

## Setup

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd Rafid1995
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and fill in your TELEGRAM_BOT_TOKEN and ANTHROPIC_API_KEY
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | — | Token from @BotFather |
| `ANTHROPIC_API_KEY` | Yes | — | Key from Anthropic Console |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-6` | Claude model ID to use |
| `MAX_TOKENS` | No | `1024` | Max tokens per response |

## How it works

```
User (Telegram) → bot.py → Anthropic API (Claude) → bot.py → User (Telegram)
```

Each user gets their own conversation history so Claude remembers context within a session. History resets on `/clear` or `/start`.
