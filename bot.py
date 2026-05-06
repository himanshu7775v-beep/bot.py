from telethon import TelegramClient, events
import asyncio, time, re, json, os

# ========= YOUR DETAILS =========
api_id = 38780710            # 👈 यहाँ अपना API ID डालो
api_hash = "9a488382ad27cda7add5a78e5f1a3528"  # 👈 यहाँ API HASH डालो
session = "your_string_session"  # 👈 यहाँ STRING SESSION डालो

client = TelegramClient(session, api_id, api_hash)

DB = "data.json"

# ========= DATABASE =========
def load():
    if not os.path.exists(DB):
        return {
            "muted": [],
            "ar": {},
            "react": {},
            "notes": {},
            "filters": {}
        }
    return json.load(open(DB))

def save():
    json.dump(data, open(DB, "w"))

data = load()

# ========= GLOBAL =========
last_reply = {}

# ========= HELPERS =========
async def ghost(e):
    try: await e.delete()
    except: pass

async def get_user(e):
    if e.is_reply:
        return (await e.get_reply_message()).sender_id
    args = e.raw_text.split()
    if len(args) > 1:
        try: return int(args[1])
        except:
            try: return (await client.get_entity(args[1])).id
            except: return None
    return None

# ========= PING =========
@client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping(e):
    t = time.time()
    m = await e.reply("...")
    await m.edit(f"⚡ {round((time.time()-t)*1000)} ms")

# ========= MUTE =========
@client.on(events.NewMessage(outgoing=True, pattern=r"\.mute"))
async def mute(e):
    u = await get_user(e)
    if u and u not in data["muted"]:
        data["muted"].append(u)
        save()
    await ghost(e)

@client.on(events.NewMessage(outgoing=True, pattern=r"\.unmute"))
async def unmute(e):
    u = await get_user(e)
    if u in data["muted"]:
        data["muted"].remove(u)
        save()
    await ghost(e)

# ========= AUTOREPLY =========
@client.on(events.NewMessage(outgoing=True, pattern=r"\.ar (.+)"))
async def ar(e):
    u = await get_user(e)
    if u:
        data["ar"][str(u)] = e.pattern_match.group(1)
        save()
    await ghost(e)

# ========= REACT =========
@client.on(events.NewMessage(outgoing=True, pattern=r"\.react (.+)"))
async def react(e):
    emoji = e.pattern_match.group(1)
    u = await get_user(e)
    if u:
        data["react"][str(u)] = emoji
        save()
    await ghost(e)

# ========= NOTES =========
@client.on(events.NewMessage(outgoing=True, pattern=r"\.save (\w+)"))
async def save_note(e):
    name = e.pattern_match.group(1)
    if e.is_reply:
        msg = await e.get_reply_message()
        data["notes"][name] = msg.text
        save()
        await e.reply(f"Saved: {name}")
    await ghost(e)

@client.on(events.NewMessage(outgoing=True, pattern=r"\.get (\w+)"))
async def get_note(e):
    name = e.pattern_match.group(1)
    if name in data["notes"]:
        await e.reply(data["notes"][name])

# ========= FILTER =========
@client.on(events.NewMessage(outgoing=True, pattern=r"\.filter (\w+) (.+)"))
async def add_filter(e):
    key, val = e.pattern_match.groups()
    data["filters"][key] = val
    save()
    await ghost(e)

# ========= MAIN =========
@client.on(events.NewMessage(incoming=True))
async def main(e):
    u = e.sender_id
    txt = e.raw_text.lower()

    if u in data["muted"]:
        try: await e.delete()
        except: pass
        return

    if str(u) in data["ar"]:
        now = time.time()
        if u not in last_reply or now - last_reply[u] > 8:
            await e.reply(data["ar"][str(u)])
            last_reply[u] = now

    for k, v in data["filters"].items():
        if k in txt:
            await e.reply(v)

    if str(u) in data["react"]:
        try: await e.react(data["react"][str(u)])
        except: pass

# ========= RUN =========
client.start()
print("🔥 USERBOT RUNNING")
client.run_until_disconnected()
