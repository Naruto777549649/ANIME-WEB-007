from pyrogram import Client, filters
from pyrogram.types import Message
import random, json, asyncio, os

API_ID = 25698862
API_HASH = "7d7739b44f5f8c825d48cc6787889dbc"
BOT_TOKEN = "7567689863:AAGsTCXf1YsS9H8_p1yW5wMUz6BjUJoOJF0"

app = Client("waifu_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DB_FILE = "waifus.json"
GROUP_ID = -1002105592589  # <-- Replace with your actual group ID here
GUESS_TIMEOUT = 60

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"waifus": [], "users": {}, "current_drop": None}, f)

def load_data():
    with open(DB_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply_text("**Konichiwa! I'm your Waifu Guess Bot.**\n\nUse /guess when a waifu appears and build your /harem!")

@app.on_message(filters.command("upload") & filters.user([7019600964]))
async def upload(_, msg: Message):
    try:
        args = msg.text.split(" ", 5)
        if len(args) != 5:
            return await msg.reply("Usage:\n`/upload <image_link> <character_name> <anime_name> <rarity_emoji>`")

        _, image_url, char_name, anime_name, rarity_emoji = args
        rarity_name = {
            "⭐": "ᴄᴏᴍᴍᴏɴ", "🔥": "ʟᴇɢᴇɴᴅᴀʀʏ", "💎": "ᴜʟᴛʀᴀ", "🌈": "ᴅɪᴠɪɴᴇ"
        }.get(rarity_emoji, "ᴜɴᴋɴᴏᴡɴ")

        data = load_data()
        data["waifus"].append({
            "image": image_url,
            "character": char_name.lower(),
            "anime": anime_name,
            "rarity": rarity_emoji,
            "rarity_name": rarity_name
        })
        save_data(data)
        await msg.reply("Waifu uploaded successfully!")
    except Exception as e:
        await msg.reply(f"Error: {e}")

@app.on_message(filters.command("broadcast") & filters.user([7019600964]))
async def broadcast(_, msg: Message):
    text = msg.text.split(" ", 1)
    if len(text) < 2:
        return await msg.reply("Usage: `/broadcast <message>`")
    data = load_data()
    failed = 0
    for user_id in data["users"]:
        try:
            await app.send_message(int(user_id), text[1])
        except:
            failed += 1
    await msg.reply(f"Broadcast done. Failed: {failed}")

@app.on_message(filters.command("guess"))
async def guess(_, msg: Message):
    data = load_data()
    user_id = str(msg.from_user.id)
    if not data.get("current_drop"):
        return await msg.reply("No waifu to guess!")
    waifu = data["current_drop"]

    guessed = msg.text.split(" ", 1)
    if len(guessed) != 2:
        return await msg.reply("Usage: `/guess <waifu_name>`")

    if guessed[1].lower() == waifu["character"]:
        data["users"].setdefault(user_id, []).append(waifu)
        data["current_drop"] = None
        save_data(data)
        await msg.reply(f"Correct! You added {waifu['character'].title()} to your harem.")
    else:
        await msg.reply("Wrong name!")

@app.on_message(filters.command("harem"))
async def harem(_, msg: Message):
    data = load_data()
    user_id = str(msg.from_user.id)
    user_waifus = data["users"].get(user_id, [])
    if not user_waifus:
        return await msg.reply("You don't have any waifus in your harem.")
    text = "**Your Harem:**\n"
    for i, w in enumerate(user_waifus, 1):
        text += f"{i}. {w['rarity']} {w['character'].title()} ({w['anime']})\n"
    await msg.reply(text)

@app.on_message(filters.command("mywaifu"))
async def mywaifu(_, msg: Message):
    data = load_data()
    user_id = str(msg.from_user.id)
    user_waifus = data["users"].get(user_id, [])
    if not user_waifus:
        return await msg.reply("You don't have any waifus.")
    w = random.choice(user_waifus)
    await msg.reply_photo(w["image"], caption=f"{w['rarity']} {w['character'].title()} from *{w['anime']}*")

@app.on_message(filters.command("force_drop") & filters.user([7019600964]))
async def manual_drop(_, msg: Message):
    data = load_data()
    if not data["waifus"]:
        return await msg.reply("No waifus available to drop.")

    waifu = random.choice(data["waifus"])
    data["current_drop"] = waifu
    save_data(data)

    try:
        await app.send_photo(
            GROUP_ID,
            waifu["image"],
            caption=f"{waifu['rarity']} ᴀ {waifu['rarity_name']} ᴡᴀɪғᴜ ʜᴀs ᴀᴘᴘᴇᴀʀᴇᴅ!\n"
                    f"ǫᴜɪᴄᴋ! ᴜsᴇ /guess ɴᴀᴍᴇ ᴛᴏ ᴀᴅᴅ ʜᴇʀ ᴛᴏ ʏᴏᴜʀ ʜᴀʀᴇᴍ!"
        )
        await msg.reply("✅ Force drop successful!")
    except Exception as e:
        await msg.reply(f"❌ Force drop failed.\nError: `{e}`")

@app.on_message(filters.private)
async def collect_users(_, msg: Message):
    data = load_data()
    uid = str(msg.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = []
        save_data(data)

# Background auto-drop function
async def drop_waifu():
    await app.wait_until_ready()
    while True:
        await asyncio.sleep(300)
        data = load_data()
        if not data["waifus"]:
            continue
        waifu = random.choice(data["waifus"])
        data["current_drop"] = waifu
        save_data(data)
        try:
            await app.send_photo(
                GROUP_ID,
                waifu["image"],
                caption=f"{waifu['rarity']} ᴀ {waifu['rarity_name']} ᴡᴀɪғᴜ ʜᴀs ᴀᴘᴘᴇᴀʀᴇᴅ!\n"
                        f"ǫᴜɪᴄᴋ! ᴜsᴇ /guess ɴᴀᴍᴇ ᴛᴏ ᴀᴅᴅ ʜᴇʀ ᴛᴏ ʏᴏᴜʀ ʜᴀʀᴇᴍ!"
            )
        except Exception as e:
            print(f"[Drop Error] {e}")

# Run the bot
if __name__ == "__main__":
    async def main():
        await app.start()
        asyncio.create_task(drop_waifu())
        print("Waifu Bot Running...")

    asyncio.run(main())