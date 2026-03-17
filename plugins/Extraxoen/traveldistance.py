from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bs4 import BeautifulSoup

def convert_units(km):
    miles = round(km * 0.621371, 2)
    knots = round(km * 0.539957, 2)
    return miles, knots

def get_distance(query):
    try:
        url = f"https://www.google.com/search?q=distance+from+{query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # Try multiple possible classes
        possible_classes = [
            "BNeawe deIvCb AP7Wnd",         # Primary result block
            "BNeawe iBp4i AP7Wnd",          # Fallback class
            "BNeawe tAd8D AP7Wnd",          # Alternate short answers
            "BNeawe s3v9rd AP7Wnd",         # General text results
        ]

        for cls in possible_classes:
            result = soup.find("div", class_=cls)
            if result and any(unit in result.text.lower() for unit in ["km", "miles"]):
                distance_text = result.text.split(" ")[0].replace(",", "")
                unit = "km" if "km" in result.text.lower() else "miles"
                distance = float(distance_text)

                if unit == "miles":
                    km = round(distance / 0.621371, 2)
                else:
                    km = distance

                miles, knots = convert_units(km)
                return f"🌍 **Distance Details:**\n\n📍 *Query:* `{query}`\n🚗 *Distance:* `{km} KM`\n🛣️ *Miles:* `{miles} MPH`\n🚢 *Knots:* `{knots} knots`"

        return "❌ Could not find the distance. Try a more specific query like `City A to City B`."
    except Exception as e:
        return f"⚠️ Error: {e}"
