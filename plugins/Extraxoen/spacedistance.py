import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from num2words import num2words

# Solar system average distances (in KM)
AVERAGE_DISTANCES = {
    ("earth", "mars"): 78340396.84,
    ("mars", "earth"): 78340396.84,
    ("earth", "venus"): 41400000,
    ("venus", "earth"): 41400000,
    ("earth", "jupiter"): 628730000,
    ("jupiter", "earth"): 628730000,
    ("earth", "moon"): 384400,
    ("moon", "earth"): 384400,
    ("earth", "sun"): 149600000,
    ("sun", "earth"): 149600000,
    ("earth", "saturn"): 1275000000,
    ("saturn", "earth"): 1275000000,
    ("earth", "neptune"): 4350000000,
    ("neptune", "earth"): 4350000000,
    ("earth", "mercury"): 91691000,
    ("mercury", "earth"): 91691000,
    ("earth", "uranus"): 2724000000,
    ("uranus", "earth"): 2724000000,
}

# Interstellar distances (in light years)
INTERSTELLAR_DISTANCES = {
    ("earth", "proxima centauri"): 4.2465,
    ("earth", "alpha centauri"): 4.367,
    ("earth", "sirius"): 8.611,
    ("earth", "betelgeuse"): 642.5,
    ("earth", "andromeda"): 2537000,
    ("proxima centauri", "earth"): 4.2465,
    ("alpha centauri", "earth"): 4.367,
    ("sirius", "earth"): 8.611,
    ("betelgeuse", "earth"): 642.5,
    ("andromeda", "earth"): 2537000,
}

# Image URLs
CELESTIAL_IMAGES = {
    "earth": "https://upload.wikimedia.org/wikipedia/commons/9/97/The_Earth_seen_from_Apollo_17.jpg",
    "mars": "https://upload.wikimedia.org/wikipedia/commons/0/02/OSIRIS_Mars_true_color.jpg",
    "venus": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Venus-real_color.jpg",
    "jupiter": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Jupiter.jpg",
    "saturn": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Saturn_during_Equinox.jpg",
    "neptune": "https://upload.wikimedia.org/wikipedia/commons/5/56/Neptune_Full.jpg",
    "uranus": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Uranus2.jpg",
    "mercury": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Mercury_in_true_color.jpg",
    "moon": "https://upload.wikimedia.org/wikipedia/commons/e/e1/FullMoon2010.jpg",
    "sun": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Solar_sys8.jpg",
    "proxima centauri": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Proxima_Centauri_by_ESO.jpg",
    "alpha centauri": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Alpha%2C_Beta_and_Proxima_Centauri_%28cropped%29.jpg",
    "sirius": "https://upload.wikimedia.org/wikipedia/commons/5/54/Sirius_A_and_B_Hubble_photo.jpg",
    "betelgeuse": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Betelgeuse_star.jpg",
    "andromeda": "https://upload.wikimedia.org/wikipedia/commons/8/85/Andromeda_Galaxy_%28with_h-alpha%29.jpg"
}

# Constants
AU_IN_KM = 149597870.7
KM_IN_LIGHT_YEAR = 9.461e+12
LIGHT_SPEED_KMPS = 299792.458

def calculate_space_distance(from_body, to_body):
    from_body = from_body.lower()
    to_body = to_body.lower()
    key = (from_body, to_body)

    if key in AVERAGE_DISTANCES:
        km = AVERAGE_DISTANCES[key]
        au = km / AU_IN_KM
        ly = km / KM_IN_LIGHT_YEAR
        light_seconds = km / LIGHT_SPEED_KMPS
        light_minutes = light_seconds / 60
        light_hours = light_minutes / 60

        return {
            "type": "solar",
            "km": f"{km:,.2f}",
            "au": f"{au:.4f}",
            "ly": f"{ly:.8f}",
            "light_minutes": f"{light_minutes:.2f}",
            "light_hours": f"{light_hours:.2f}"
        }

    elif key in INTERSTELLAR_DISTANCES:
        ly = INTERSTELLAR_DISTANCES[key]
        km = ly * KM_IN_LIGHT_YEAR
        au = km / AU_IN_KM
        light_seconds = km / LIGHT_SPEED_KMPS
        light_minutes = light_seconds / 60
        light_hours = light_minutes / 60

        return {
            "type": "interstellar",
            "km": f"{km:,.2f}",
            "au": f"{au:.2f}",
            "ly": f"{ly:.5f}",
            "light_minutes": f"{light_minutes:.2f}",
            "light_hours": f"{light_hours:.2f}",
        }

    return None

@Client.on_message(filters.command("spacedistance") & filters.private)
async def space_distance_handler(client, message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2 or "to" not in text[1].lower():
        await message.reply("📌 Usage: `/spacedistance Earth to Mars` or `/spacedistance Earth to Proxima Centauri`", quote=True)
        return

    try:
        parts = text[1].lower().split("to")
        from_body = parts[0].strip()
        to_body = parts[1].strip()

        result = calculate_space_distance(from_body, to_body)

        if result is None:
            await message.reply("❌ Invalid celestial bodies or data not available.")
            return

        title = "🌌 Interstellar Distance" if result['type'] == "interstellar" else "🪐 Space Distance"

        # Convert values for word representation
        km_float = float(result['km'].replace(",", ""))
        au_float = float(result['au'].replace(",", ""))
        min_float = float(result['light_minutes'].replace(",", ""))
        hour_float = float(result['light_hours'].replace(",", ""))

        km_words = num2words(km_float, to='cardinal').title()
        au_words = num2words(au_float, to='cardinal').title()
        min_words = num2words(min_float, to='cardinal').title()
        hour_words = num2words(hour_float, to='cardinal').title()

        msg = (
            f"**{title} from {from_body.title()} to {to_body.title()}**\n\n"
            f"🔹 **Kilometers:** {result['km']} km\n"
            f"    ➤ ({km_words} Kilometers)\n"
            f"🔹 **Astronomical Units:** {result['au']} AU\n"
            f"    ➤ ({au_words} AU)\n"
            f"🔹 **Light Years:** {result['ly']} ly\n"
            f"🔹 **Light Speed Travel Time:** {result['light_minutes']} minutes ({result['light_hours']} hours)\n"
            f"    ➤ ({min_words} Minutes / {hour_words} Hours)"
        )

        # Get image or fallback
        from_img = CELESTIAL_IMAGES.get(from_body, None)
        to_img = CELESTIAL_IMAGES.get(to_body, None)
        photo_url = to_img or from_img or None

        # Send as photo + caption (or fallback to text if no image)
        if photo_url:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=photo_url,
                caption=msg,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🌍 NASA Solar System", url="https://solarsystem.nasa.gov")]]
                ),
                parse_mode="Markdown"
            )
        else:
            await message.reply(msg, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🌍 NASA Solar System", url="https://solarsystem.nasa.gov")]]
            ))

    except Exception as e:
        await message.reply(f"❌ Error: {e}")
