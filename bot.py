from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from config import BOT_TOKEN, LOG_GROUP_ID
from services.logger import log_to_group

# ---------- DATA ----------
STATES = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
    "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka",
    "Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram",
    "Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu",
    "Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal"
]

GENDERS = ["Male", "Female", "Transgender"]

# In-memory user state (later MongoDB replace pannalam)
USER_DATA = {}

# ---------- HELPERS ----------
def chunk_buttons(items, prefix, cols=3):
    keyboard = []
    row = []
    for i, item in enumerate(items, 1):
        row.append(InlineKeyboardButton(item, callback_data=f"{prefix}:{item}"))
        if i % cols == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return keyboard

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    if uid not in USER_DATA:
        USER_DATA[uid] = {"step": "STATE"}

        await log_to_group(
            context,
            f"🟢 NEW USER START\n👤 {user.first_name}\n🆔 {uid}"
        )

    keyboard = chunk_buttons(STATES, "STATE")
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✨ *Welcome to Premium Dating* 💖\n\n"
        "📍 *Select your State*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ---------- CALLBACK HANDLER ----------
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    data = query.data

    # -------- STATE SELECT --------
    if data.startswith("STATE:"):
        state = data.split(":")[1]
        USER_DATA[uid]["state"] = state
        USER_DATA[uid]["step"] = "GENDER"

        keyboard = [
            [
                InlineKeyboardButton("👨 Male", callback_data="GENDER:Male"),
                InlineKeyboardButton("👩 Female", callback_data="GENDER:Female"),
                InlineKeyboardButton("⚧ Transgender", callback_data="GENDER:Transgender")
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="BACK:STATE")]
        ]

        await query.edit_message_text(
            f"📍 State: *{state}*\n\n"
            "🧬 *Select your Gender*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    # -------- GENDER SELECT --------
    elif data.startswith("GENDER:"):
        gender = data.split(":")[1]
        USER_DATA[uid]["gender"] = gender
        USER_DATA[uid]["step"] = "AGE"

        ages = [str(i) for i in range(11, 71)]
        keyboard = chunk_buttons(ages, "AGE")
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="BACK:GENDER")])

        await query.edit_message_text(
            f"🧬 Gender: *{gender}*\n\n"
            "🎂 *Select your Age*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    # -------- AGE SELECT --------
    elif data.startswith("AGE:"):
        age = data.split(":")[1]
        USER_DATA[uid]["age"] = age
        USER_DATA[uid]["step"] = "DONE"

        user = query.from_user
        data_log = USER_DATA[uid]

        await log_to_group(
            context,
            f"✅ REGISTRATION COMPLETED\n"
            f"👤 {user.first_name}\n"
            f"🆔 {uid}\n"
            f"📍 {data_log['state']}\n"
            f"🧬 {data_log['gender']}\n"
            f"🎂 {age}"
        )

        keyboard = [
            [
                InlineKeyboardButton("🤍 Human", callback_data="CHAT:HUMAN"),
                InlineKeyboardButton("🤖 AI", callback_data="CHAT:AI")
            ]
        ]

        await query.edit_message_text(
            "🎉 *Registration Completed!* 💎\n\n"
            "💬 *Who do you want to chat with?*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    # -------- BACK BUTTONS --------
    elif data.startswith("BACK:STATE"):
        keyboard = chunk_buttons(STATES, "STATE")
        await query.edit_message_text(
            "📍 *Select your State*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("BACK:GENDER"):
        keyboard = [
            [
                InlineKeyboardButton("👨 Male", callback_data="GENDER:Male"),
                InlineKeyboardButton("👩 Female", callback_data="GENDER:Female"),
                InlineKeyboardButton("⚧ Transgender", callback_data="GENDER:Transgender")
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="BACK:STATE")]
        ]

        await query.edit_message_text(
            "🧬 *Select your Gender*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.bot_data["LOG_GROUP_ID"] = LOG_GROUP_ID

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("🚀 Bot running (Polling mode)")
    app.run_polling()

if __name__ == "__main__":
    main()
