from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bs4 import BeautifulSoup

# Full list of supported languages
LANGUAGES = {
    "English": "en",
    "Malayalam": "ml",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Russian": "ru",
    "Arabic": "ar",
    "Italian": "it",
    "Chinese": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur",
    "Turkish": "tr"
}

DEFAULT_LANGUAGES = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Russian", "Arabic"]

@Client.on_message(filters.command("translate") & filters.private)
async def translate_handler(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("❌ Usage:\n\n`/translate <text>`\n\nExample: `/translate Hello world!`")

    original_text = args[1]

    # Default few languages + All languages button
    buttons = [
        [InlineKeyboardButton(lang, callback_data=f"tr_{LANGUAGES[lang]}|{original_text}")]
        for lang in DEFAULT_LANGUAGES
    ]
    buttons.append([InlineKeyboardButton("🔁 All Languages ➕", callback_data=f"tr_all|{original_text}")])

    await message.reply(
        f"🌍 Select a language to translate:\n\n**{original_text}**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"tr_all\|(.+)"))
async def all_languages_callback(client, callback_query):
    text = callback_query.data.split("|", 1)[1]

    # Show all languages in rows of 2
    lang_buttons = []
    lang_items = list(LANGUAGES.items())
    for i in range(0, len(lang_items), 2):
        row = []
        for name, code in lang_items[i:i+2]:
            row.append(InlineKeyboardButton(name, callback_data=f"tr_{code}|{text}"))
        lang_buttons.append(row)

    await callback_query.message.edit_text(
        f"🌐 **All Languages:**\n\n**{text}**",
        reply_markup=InlineKeyboardMarkup(lang_buttons)
    )

@Client.on_callback_query(filters.regex(r"tr_(.+?)\|(.+)"))
async def callback_translate(client, callback_query):
    lang_code, text = callback_query.data[3:].split("|", 1)
    translated = await fetch_translation(text, lang_code)
    await callback_query.message.edit_text(
        f"✅ **Translated to `{lang_code}`**:\n\n{translated}",
        reply_markup=None
    )

async def fetch_translation(text, target_lang):
    url = "https://translate.google.com/m"
    params = {
        "sl": "auto",
        "tl": target_lang,
        "q": text
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        result = soup.find("div", class_="result-container")
        if result and result.text.strip():
            return result.text.strip()
        else:
            return "❌ Translation not found. Google page layout may have changed."
    except Exception as e:
        return f"⚠️ Error during translation: {e}"
