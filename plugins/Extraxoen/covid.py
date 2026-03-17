import requests
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("covid"))
async def covid_stats(client, message: Message):
    try:
        text = message.text.split()
        country = "world" if len(text) < 2 else text[1]

        if country.lower() == "world":
            url = "https://disease.sh/v3/covid-19/all"
        else:
            url = f"https://disease.sh/v3/covid-19/countries/{country}"

        res = requests.get(url)
        data = res.json()

        if "message" in data:
            await message.reply("❌ Invalid country name. Try something like:\n`/covid Brazil`")
            return

        reply_text = (
            f"🌍 COVID-19 Stats for {data.get('country', 'World')}\n\n"
            f"🦠 Cases: {data['cases']}\n"
            f"💀 Deaths: {data['deaths']}\n"
            f"💚 Recovered: {data['recovered']}\n"
            f"😷 Active: {data['active']}\n"
            f"🧪 Tests: {data['tests']}\n"
        )

        await message.reply(reply_text)

    except Exception as e:
        print(e)
        await message.reply("⚠️ Failed to fetch data. Try again later.")
