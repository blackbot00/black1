from telegram.ext import ContextTypes

async def log_to_group(context: ContextTypes.DEFAULT_TYPE, text: str):
    await context.bot.send_message(
        chat_id=context.application.bot_data["LOG_GROUP_ID"],
        text=text
    )
