import requests
import re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

@Client.on_message(filters.command("weather") & filters.private)
async def weather_handler(bot, message: Message):
    text = message.text.split(maxsplit=1)

    if len(text) != 2:
        return await message.reply(
            "❌ Usage:\n`/weather <city>`\n\nExample: `/weather London`",
            quote=True
        )

    city = text[1]
    basic_url = f"https://wttr.in/{city}?format=3"
    detailed_url = f"https://wttr.in/{city}?m"  # metric & full terminal-style view

    try:
        # Fetch basic weather
        basic_response = requests.get(basic_url, timeout=10)
        if basic_response.status_code != 200 or "Unknown location" in basic_response.text:
            raise ValueError("Invalid city")

        weather_basic = basic_response.text.strip()

        # Fetch full text to extract humidity
        detailed_response = requests.get(detailed_url, timeout=10)
        lines = detailed_response.text.splitlines()

        humidity = "N/A"
        for line in lines:
            if "Humidity" in line:
                match = re.search(r"Humidity:\s*([0-9]+%)", line)
                if match:
                    humidity = match.group(1)
                    break

        # Date & time (local to system, not city — for accurate time by city you'd need API)
        now = datetime.now()
        date_time = now.strftime("%A, %d %B %Y\n🕒 %I:%M %p")

        button = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🌐 View Full Forecast", url=f"https://wttr.in/{city}")
            ]]
        )

        await message.reply(
            f"🌦️ **Weather Report for {city.title()}**\n\n"
            f"📅 **Date & Time:**\n`{date_time}`\n"
            f"🌡️ **Condition:** `{weather_basic}`\n"
            f"💧 **Humidity:** `{humidity}`",
            reply_markup=button,
            quote=True
        )

    except Exception as e:
        await message.reply(
            "⚠️ Failed to fetch weather data. Please check the city name and try again.",
            quote=True
        )
