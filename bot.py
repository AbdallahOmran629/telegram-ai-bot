import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from rembg import remove
from PIL import Image
from io import BytesIO

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv ('8006683736:AAEUb1C0jdQV1DCTmzUn_Y16ik8MMlNPVyc')
GROQ_API_KEY = os.getenv ('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')
MODEL = 'llama3-70b-8192'

def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    print("Groq status code:", response.status_code)
    print("Groq response:", response.text)

    try:
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ Could not get AI response: {e}\n\nRaw response: {response.text}"

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action='typing')
    await update.message.reply_text("Welcome to AI Code Bot!\nUse /explain, /debug, or /generate followed by your code or question. You can also send an image to remove its background in just 30 sec.")

async def handle_explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    prompt = f"Explain this code in detail:\n{text}"
    answer = ask_groq(prompt)
    await update.message.reply_text(answer)

async def handle_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    prompt = f"Find and fix bugs in the following code:\n{text}"
    answer = ask_groq(prompt)
    await update.message.reply_text(answer)

async def handle_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    prompt = f"Generate code for the following task:\n{text}"
    answer = ask_groq(prompt)
    await update.message.reply_text(answer)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    answer = ask_groq(user_input)
    await update.message.reply_text(answer)

async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Please send an image to remove its background.")
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = await file.download_to_drive()

    input_image = Image.open(file_path).convert("RGBA")
    output_image = remove(input_image)

    bio = BytesIO()
    output_image.save(bio, format='PNG')
    bio.seek(0)

    await update.message.reply_photo(photo=bio, filename="no_bg.png")

# === MAIN ===
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("explain", handle_explain))
app.add_handler(CommandHandler("debug", handle_debug))
app.add_handler(CommandHandler("generate", handle_generate))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, remove_bg))

app.run_polling()
