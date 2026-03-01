import os
import logging
from dotenv import load_dotenv
import anthropic
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Per-user conversation history: {user_id: [{"role": ..., "content": ...}]}
conversation_history: dict[int, list[dict]] = {}


def get_claude_response(user_id: int, user_message: str) -> str:
    history = conversation_history.setdefault(user_id, [])
    history.append({"role": "user", "content": user_message})

    response = claude_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=(
            "You are a helpful assistant connected via Telegram. "
            "Be concise, friendly, and accurate."
        ),
        messages=history,
    )

    assistant_text = response.content[0].text
    history.append({"role": "assistant", "content": assistant_text})
    return assistant_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    conversation_history.pop(user.id, None)
    await update.message.reply_text(
        f"Hello, {user.first_name}! I'm powered by Claude.\n"
        "Send me any message and I'll respond.\n"
        "Use /clear to reset the conversation."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conversation_history.pop(user_id, None)
    await update.message.reply_text("Conversation cleared. Start fresh!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        reply = get_claude_response(user_id, user_text)
    except anthropic.APIError as e:
        logger.error("Anthropic API error: %s", e)
        reply = "Sorry, I encountered an error reaching Claude. Please try again."

    await update.message.reply_text(reply)


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment.")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set in environment.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
