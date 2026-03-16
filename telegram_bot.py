"""
Telegram bot that connects to Claude via the Anthropic API.

Each user gets their own conversation history, so Claude remembers
context within a session.

Setup:
    1. Copy .env.example to .env and fill in your keys.
    2. pip install -r requirements.txt
    3. python telegram_bot.py

Environment variables:
    TELEGRAM_BOT_TOKEN  - from @BotFather on Telegram
    ANTHROPIC_API_KEY   - from console.anthropic.com
"""

import os
import logging
from collections import defaultdict

import anthropic
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-opus-4-6"
MAX_TOKENS = 1024

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Per-user conversation history: {user_id: [{"role": ..., "content": ...}]}
conversations: dict[int, list[dict]] = defaultdict(list)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — greet the user and clear their history."""
    user_id = update.effective_user.id
    conversations[user_id].clear()
    await update.message.reply_text(
        "Hi! I'm powered by Claude. Send me any message and I'll respond.\n"
        "Use /clear to reset the conversation."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /clear — wipe conversation history for this user."""
    user_id = update.effective_user.id
    conversations[user_id].clear()
    await update.message.reply_text("Conversation cleared. Fresh start!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward every text message to Claude and reply with the response."""
    user_id = update.effective_user.id
    user_text = update.message.text

    # Append the new user turn
    conversations[user_id].append({"role": "user", "content": user_text})

    # Show a typing indicator while waiting for Claude
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        response = claude.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=conversations[user_id],
        )
        assistant_text = next(
            (block.text for block in response.content if block.type == "text"), ""
        )
    except anthropic.APIError as exc:
        logger.error("Claude API error: %s", exc)
        assistant_text = "Sorry, I ran into an error talking to Claude. Please try again."

    # Append Claude's reply to history so the next turn has context
    conversations[user_id].append({"role": "assistant", "content": assistant_text})

    await update.message.reply_text(assistant_text)


def main() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running…")
    app.run_polling()


if __name__ == "__main__":
    main()
