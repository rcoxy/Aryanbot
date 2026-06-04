#!/usr/bin/env python3
import os
import asyncio
import json
import random
import time
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions,
    ChatMemberUpdated,
    Message,
)
from pyrogram.enums import ChatMemberStatus
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import fadein, fadeout
from yt_dlp import YoutubeDL
from gtts import gTTS
from deep_translator import GoogleTranslator

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, WELCOME_NAME, REPO_URL, OWNER_USERNAME, SONG_PATH

TMP = os.path.join(os.getcwd(), "tmp")
os.makedirs(TMP, exist_ok=True)

# ─── yt-dlp options ───────────────────────────────────────────────────────────

ydl_audio_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "outtmpl": os.path.join(TMP, "%(title).80s.%(ext)s"),
    "postprocessors": [
        {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
    ],
}

ydl_insta_opts = {
    "quiet": True,
    "outtmpl": os.path.join(TMP, "insta_%(id)s.%(ext)s"),
}

app = Client("rajan_baby_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ─── Queue ────────────────────────────────────────────────────────────────────

QUEUE: list[str] = []

# ─── Texts ────────────────────────────────────────────────────────────────────

HELP_TEXT = """💗💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 𝑶𝑷 𝑩𝒐𝒕 — 𝑨𝒍𝒍 𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒔 💗💗

🎧 𝑴𝒖𝒔𝒊𝒄 𝒁𝒐𝒏𝒆
• /play <song> — quality buttons se MP3
• /song <name> — direct MP3 download
• /video <name> — quality buttons se video
• /spotify <name> — Spotify style search
• /music — random vibe suggestion

📸 𝑰𝒏𝒔𝒕𝒂𝒈𝒓𝒂𝒎
• /ig <link> — Reel/Post download
• Auto detect — bas link bhejo!

💘 𝑳𝒐𝒗𝒆 𝒁𝒐𝒏𝒆
• /love • /kiss • /hug • /shayari • /shyri
• /lovecal • /compat • /lovemeter (reply)
• /proposal (reply) • /shaadi (reply)
• /divorce (reply) • /baby (reply) • /couple

😂 𝑭𝒖𝒏 𝒁𝒐𝒏𝒆
• /fun • /joke • /fight • /wins • /rate • /pick
• /roast • /insult (reply) • /clown (reply)
• /character (reply) • /raap • /rap (reply)
• /dhanda • /networth (reply) • /petpet (reply)
• /breakup (reply)

🔮 𝑷𝒓𝒆𝒅𝒊𝒄𝒕𝒊𝒐𝒏𝒔
• /kismat (reply) — daily fortune
• /iq • /iqtest (reply) — IQ test
• /death (reply) — death prediction
• /horoscope <sign> — daily horoscope
• /quote — inspirational quote

🤖 𝑨𝑰 & 𝑻𝒐𝒐𝒍𝒔
• /ai <text> — AI chat
• /tts <text> — text → voice 🎙
• /tr <lang> <text> — translate (en, hi, etc.)
• /lyrics <song> — lyrics finder
• /weather <city> — mausam
• /imagine <prompt> — AI image generate
• /wallpaper [theme] — HD wallpaper
• /sticker — reply photo OR text sticker
• /fakecall <name> — fake incoming call
• /news — top 10 news

🎮 𝑮𝒂𝒎𝒆𝒔 & 𝑬𝒄𝒐𝒏𝒐𝒎𝒚
• /coins — balance check
• /daily — free 100-500 coins
• /dice <bet> — 🎲 ≥4 wins
• /slots <bet> — 🎰 jackpot 10x
• /quiz — random GK
• /truth • /dare 😈
• /rps (reply) — rock paper scissors
• /race — emoji racing
• /spin — bottle spin (group)

📊 𝑮𝒓𝒐𝒖𝒑 𝑺𝒕𝒂𝒕𝒔
• /top • /leaderboard — top 10 active
• /mystats • /level • /stats — your XP
• /tagall <msg> — tag all (admin only)
• /king — king of the day

🌅 𝑫𝒂𝒊𝒍𝒚 𝑽𝒊𝒃𝒆𝒔
• /gm • /goodmorning — morning shayari
• /gn • /goodnight — night shayari

🛡 𝑨𝒅𝒎𝒊𝒏 𝑷𝒓𝒐
• /kick • /ban • /mute • /unmute
• /promote • /demote
• /warn (reply) — 3 = auto ban
• /warns (reply) — check warns
• /resetwarns (reply) — reset

👑 𝑶𝒘𝒏𝒆𝒓 & 𝑻𝒐𝒐𝒍𝒔
• /owner — boss intro song 😎
• /logo <text> — stylish logo
• /id • /info • /ping • /about

🤖 𝑪𝒍𝒐𝒏𝒆 𝑩𝒐𝒕
• /clone <token> — apna bot clone karo
• /myclone — clone status
• /delclone — clone band karo

💗 Powered by 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 — @replyraid 💗"""

SHAYARI_LIST = [
    "💌 Tum bin jeena nahi,\nTum ho toh zindagi hai.\n— Rajan Baby 💗",
    "🌹 Aankhon mein teri,\nSapne mere rehte hain.\n— Rajan Baby 💗",
    "💞 Dil diya hai,\nJaan bhi denge,\nAe wafa ke liye.\n— Rajan Baby 💗",
    "🌙 Raat ko chand dekha,\nTumhari yaad aayi,\nDil ne kaha — sirf tum.\n— Rajan Baby 💗",
    "🌸 Teri muskaan pe,\nNisaar ho gaya hun main,\nBas tujhse mohabbat hai.\n— Rajan Baby 💗",
]

AI_REPLIES = [
    "💗 Rajan Baby tumse pyaar karta hai 😘",
    "😏 Baby tum bahut cute ho!",
    "🔥 Aaj mood romantic hai kya? 💗",
    "💗 Tum bolo, main sunu 🥰",
    "👑 Rajan Baby always with you!",
    "🧠 Analysis complete: Tum duniya ke sabse pyaare ho 😍",
    "🤖 AI says: Rajan Baby + Tum = Perfect match! 💞",
    "💡 Processing... Output: Tum bohot zyada awesome ho! 🔥",
]

MUSIC_SUGGESTIONS = [
    "🎵 Kesariya — https://youtu.be/3Y7r4WkZ0c8",
    "🎵 Tum Hi Ho — https://youtu.be/IJq0xyQVnOk",
    "🎵 Raataan Lambiyan — https://youtu.be/pKWrCVhXNLM",
    "🎵 Tera Ban Jaunga — https://youtu.be/I7YEzxeBLW4",
    "🎵 Hawayein — https://youtu.be/TXMqVBBYMg4",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def sanitize(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in " ._-()").strip()


def stylish(s: str) -> str:
    out = []
    for c in s:
        o = ord(c)
        if 0x41 <= o <= 0x5A:
            out.append(chr(0x1D468 + o - 0x41))
        elif 0x61 <= o <= 0x7A:
            out.append(chr(0x1D482 + o - 0x61))
        else:
            out.append(c)
    return "".join(out)


def cleanup(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def download_audio_sync(query):
    try:
        with YoutubeDL(ydl_audio_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if isinstance(info, dict) and "entries" in info:
                info = info["entries"][0]
            title = info.get("title", "audio")
            for ext in ("mp3", "m4a", "webm", "opus"):
                candidate = os.path.join(TMP, sanitize(title) + "." + ext)
                if os.path.exists(candidate):
                    return candidate, title
            files = sorted(
                [os.path.join(TMP, f) for f in os.listdir(TMP)],
                key=os.path.getmtime, reverse=True,
            )
            return (files[0], title) if files else (None, None)
    except Exception as e:
        print("audio error", e)
    return None, None


def download_quality_video_sync(query, res):
    try:
        opts = {
            "format": f"bestvideo[ext=mp4][height<={res}]+bestaudio[ext=m4a]/best[ext=mp4][height<={res}]/best",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "outtmpl": os.path.join(TMP, "%(title).80s.%(ext)s"),
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if isinstance(info, dict) and "entries" in info:
                info = info["entries"][0]
            title = info.get("title", "video")
            for ext in ("mp4", "mkv", "webm"):
                candidate = os.path.join(TMP, sanitize(title) + "." + ext)
                if os.path.exists(candidate):
                    return candidate, title
            files = sorted(
                [os.path.join(TMP, f) for f in os.listdir(TMP)],
                key=os.path.getmtime, reverse=True,
            )
            return (files[0], title) if files else (None, None)
    except Exception as e:
        print("video quality error", e)
    return None, None


def download_insta_sync(url):
    try:
        with YoutubeDL(ydl_insta_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if isinstance(info, dict) and "entries" in info:
                info = info["entries"][0]
            title = info.get("title", "Instagram")
            filename = ydl.prepare_filename(info)
            if os.path.exists(filename):
                return filename, title
            files = sorted(
                [os.path.join(TMP, f) for f in os.listdir(TMP)],
                key=os.path.getmtime, reverse=True,
            )
            return (files[0], title) if files else (None, None)
    except Exception as e:
        print("insta error", e)
    return None, None


async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


def player_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data="pause"),
            InlineKeyboardButton("▶️ Resume", callback_data="resume"),
        ],
        [
            InlineKeyboardButton("⏭ Skip", callback_data="skip"),
            InlineKeyboardButton("⏹ Stop", callback_data="stop"),
        ],
    ])


def quality_buttons(query):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1080p 🎬", callback_data=f"vid|1080|{query}"),
            InlineKeyboardButton("720p 🎥", callback_data=f"vid|720|{query}"),
        ],
        [
            InlineKeyboardButton("360p 📱", callback_data=f"vid|360|{query}"),
            InlineKeyboardButton("MP3 🎧", callback_data=f"mp3|0|{query}"),
        ],
    ])


# ─── Start / Help ─────────────────────────────────────────────────────────────

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(_, m):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Help 💗", callback_data="help"),
         InlineKeyboardButton("Music 🎧", callback_data="music_menu")],
        [InlineKeyboardButton("Love 💘", callback_data="love_menu"),
         InlineKeyboardButton("Fun 😂", callback_data="fun_menu")],
    ])
    await m.reply_text(
        f"👋 Welcome to 💗💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 𝑶𝑷 𝑩𝒐𝒕 💗💗\n\nHello {m.from_user.first_name}! 😍\nMain hun tera bot, har waqt ready! 💗",
        reply_markup=kb,
    )


@app.on_message(filters.command("help"))
async def help_cmd(_, m):
    await m.reply_text(HELP_TEXT)


# ─── Callback Handler ─────────────────────────────────────────────────────────

@app.on_callback_query()
async def cb(client, q):
    data = q.data
    back_btn = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]

    # ── Menu ────────────────────────────────────────────────────
    if data == "help":
        await q.message.edit_text(HELP_TEXT, reply_markup=InlineKeyboardMarkup(back_btn))

    elif data == "music_menu":
        await q.message.edit_text(
            "🎧 Music Zone:\n• /play <song> — quality buttons\n• /song <song> — direct MP3\n• /video <name> — quality buttons\n• /spotify <song> — Spotify style\n• /ig <link> — Instagram\n• /music — random vibe",
            reply_markup=InlineKeyboardMarkup(back_btn),
        )

    elif data == "love_menu":
        await q.message.edit_text(
            "💘 Love Zone:\n• /love\n• /kiss\n• /hug\n• /shayari",
            reply_markup=InlineKeyboardMarkup(back_btn),
        )

    elif data == "fun_menu":
        await q.message.edit_text(
            "😂 Fun Zone:\n• /joke\n• /fight\n• /wins\n• /roast\n• /rate\n• /pick",
            reply_markup=InlineKeyboardMarkup(back_btn),
        )

    elif data == "play_owner_song":
        await q.answer("🎵 Playing Rajan Baby's song...", show_alert=False)
        await q.message.reply_audio(OWNER_CMD_SONG, caption="🎶 Rajan Baby Owner Song 💗")

    elif data == "back":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Help 💗", callback_data="help"),
             InlineKeyboardButton("Music 🎧", callback_data="music_menu")],
            [InlineKeyboardButton("Love 💘", callback_data="love_menu"),
             InlineKeyboardButton("Fun 😂", callback_data="fun_menu")],
        ])
        await q.message.edit_text(
            "💗💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 𝑶𝑷 𝑩𝒐𝒕 💗💗\n\nChoose a menu baby 😘",
            reply_markup=kb,
        )

    # ── Player controls ──────────────────────────────────────────
    elif data == "pause":
        await q.answer("⏸ Paused baby 💗", show_alert=False)

    elif data == "resume":
        await q.answer("▶️ Resumed baby 💗", show_alert=False)

    elif data == "skip":
        if QUEUE:
            QUEUE.pop(0)
        if QUEUE:
            next_song = QUEUE[0]
            await q.message.reply_text(
                f"⏭ Skipped!\n\n💗 Next Playing 🎧\n👉 **{next_song}**",
                reply_markup=player_buttons(),
            )
        else:
            await q.message.reply_text("💔 Queue khatam baby\n\n/play se naya song lao!")
        await q.answer()

    elif data == "stop":
        QUEUE.clear()
        await q.message.reply_text("⏹ Music stopped baby 💔\n\n/play se fir shuru karo!")
        await q.answer()

    # ── Music download ───────────────────────────────────────────
    elif data.startswith("mp3|") or data.startswith("vid|"):
        parts = data.split("|", 2)
        kind = parts[0]
        quality = parts[1]
        query = parts[2]
        await q.message.edit_text("💗 Processing baby... please wait ⏳")
        search = query if ("youtube.com" in query or "youtu.be" in query) else f"ytsearch1:{query}"

        if kind == "mp3":
            path, title = await asyncio.get_event_loop().run_in_executor(
                None, download_audio_sync, search
            )
            if not path:
                return await q.message.edit_text("❌ Song nahi mila 😢 Koi aur try karo!")
            try:
                await q.message.reply_audio(
                    path,
                    caption=f"🎧 {title}\n💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚",
                )
                await q.message.delete()
            except Exception as e:
                await q.message.edit_text(f"❌ Upload failed: {e}")
            finally:
                cleanup(path)

        else:
            path, title = await asyncio.get_event_loop().run_in_executor(
                None, download_quality_video_sync, search, quality
            )
            if not path:
                return await q.message.edit_text("❌ Video nahi mila 😢")
            try:
                await q.message.reply_video(
                    path,
                    caption=f"🎬 {title}\n📺 Quality: {quality}p\n💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚",
                    supports_streaming=True,
                )
                await q.message.delete()
            except Exception as e:
                await q.message.edit_text(f"❌ Upload failed: {e}")
            finally:
                cleanup(path)


# ─── Info ─────────────────────────────────────────────────────────────────────

@app.on_message(filters.command("ping"))
async def ping_cmd(client, m):
    start = time.time()
    temp = await m.reply_text("⏳ Calculating ping...")
    ping_ms = int((time.time() - start) * 1000)

    ping_bg = os.path.join(TMP, "ping_bg.png")
    video_path = os.path.join(TMP, "ping_cinematic.mp4")

    try:
        # Dark blue gradient background
        bg = Image.new("RGB", (800, 400))
        for y in range(400):
            r = int(10 * (1 - y / 400))
            g = int(10 + 20 * (y / 400))
            b = int(40 + 80 * (y / 400))
            bg.paste(Image.new("RGB", (800, 1), (r, g, b)), (0, y))
        bg.save(ping_bg)

        clip = ImageClip(ping_bg).set_duration(5)

        ping_text = (
            TextClip(
                f"Rajan Baby\nPong!  {ping_ms} ms",
                fontsize=70, font="Helvetica-Bold",
                color="cyan", stroke_color="magenta", stroke_width=3,
            )
            .set_position("center").set_duration(5).fadein(0.5).fadeout(0.5)
        )
        sparkle = (
            TextClip("*", fontsize=40, color="yellow")
            .set_position((720, 30)).set_duration(5)
        )

        final = CompositeVideoClip([clip, ping_text, sparkle])
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: final.write_videofile(
                video_path, fps=24, codec="libx264", audio=False, logger=None
            ),
        )

        await client.send_video(
            m.chat.id,
            video=video_path,
            caption=f"💖 Stylish Ping!\n🏓 Pong! ⚡ {ping_ms} ms",
        )
        await temp.delete()

    except Exception as e:
        print("Cinematic ping error:", e)
        await temp.edit_text(f"🏓 Pong! ⚡ {ping_ms} ms")

    finally:
        cleanup(ping_bg)
        cleanup(video_path)


@app.on_message(filters.command("id"))
async def id_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    await m.reply_text(f"📌 ID of {target.first_name}: `{target.id}`")


@app.on_message(filters.command("info"))
async def info_cmd(_, m):
    u = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    await m.reply_text(
        f"📋 User Info:\n\n"
        f"👤 Name: {u.first_name} {u.last_name or ''}\n"
        f"🆔 ID: `{u.id}`\n"
        f"👤 Username: @{u.username if u.username else 'None'}\n"
        f"🤖 Bot: {'Yes' if u.is_bot else 'No'}"
    )


@app.on_message(filters.command("about"))
async def about_cmd(_, m):
    await m.reply_text(
        f"🤖 💗💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 𝑶𝑷 𝑩𝒐𝒕 💗💗\n"
        f"👑 Owner ID: `{OWNER_ID}`\n"
        f"🔥 Version: 3.0\n"
        f"💗 Powered by Rajan Baby"
    )


OWNER_CMD_SONG = "CQACAgUAAxkBAAICumnGqupva40S7kBQyqyQrFNGbUL1AAJSIAACvI05VhM_SyBpRV4MHgQ"
OWNER_TAG_USERNAME = "replyraid"
_last_owner_play: dict[int, float] = {}


def make_owner_thumb():
    img = Image.new("RGB", (1280, 720), (30, 0, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except Exception:
        font = ImageFont.load_default()
    draw.text((150, 280), "💥 RAJAN BABY ALWAYS WINS 💥", fill=(255, 255, 255), font=font)
    path = os.path.join(TMP, "owner_thumb.png")
    img.save(path)
    return path


@app.on_message(filters.command("owner"))
async def owner_cmd(_, m):
    chat_id = m.chat.id
    now = asyncio.get_event_loop().time()
    if chat_id in _last_owner_play and now - _last_owner_play[chat_id] < 10:
        return
    _last_owner_play[chat_id] = now

    thumb_path = make_owner_thumb()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💖 Follow Owner", url=f"https://t.me/{OWNER_TAG_USERNAME}")],
        [InlineKeyboardButton("🎵 Play Song", callback_data="play_owner_song")],
    ])
    try:
        await m.reply_photo(
            thumb_path,
            caption=(
                "💥 𝗥𝗔𝗝𝗔𝗡 𝗕𝗔𝗕𝗬 𝗔𝗟𝗪𝗔𝗬𝗦 𝗪𝗜𝗡𝗦 💥\n\n"
                f"👑 Follow owner: @{OWNER_TAG_USERNAME}\n"
                "💖 Mast vibe with Rajan Baby 💗"
            ),
            reply_markup=buttons,
        )
        await m.reply_audio(OWNER_CMD_SONG, caption="🎶 Rajan Baby Owner Song 💗")
    finally:
        cleanup(thumb_path)


@app.on_message(filters.command("repo"))
async def repo_cmd(_, m):
    await m.reply_text(f"📦 Repo: {REPO_URL}" if REPO_URL else "📦 Repo not configured.")


# ─── Music ────────────────────────────────────────────────────────────────────

@app.on_message(filters.command("play") & (filters.private | filters.group))
async def play_cmd(_, m):
    query = " ".join(m.command[1:])
    if not query:
        return await m.reply_text("💗 Baby song ya link do 😘\n\nUsage: /play <song name or link>")

    QUEUE.append(query)
    position = len(QUEUE)

    if position == 1:
        await m.reply_text(
            f"💗 Now Playing 🎧\n👉 **{query}**",
            reply_markup=player_buttons(),
        )
    else:
        await m.reply_text(
            f"💗 Added to Queue 😘\n👉 **{query}**\n\n📋 Position: #{position}",
            reply_markup=player_buttons(),
        )


@app.on_message(filters.command("song") & (filters.private | filters.group))
async def song_cmd(_, m):
    query = " ".join(m.command[1:])
    if not query:
        return await m.reply_text("🎧 Usage: /song <song name or YouTube link>")
    status = await m.reply_text("🔎 Searching song...")
    search = query if ("youtube.com" in query or "youtu.be" in query) else f"ytsearch1:{query}"
    path, title = await asyncio.get_event_loop().run_in_executor(None, download_audio_sync, search)
    if not path:
        return await status.edit_text("❌ Song nahi mila 😢 Koi aur try karo!")
    try:
        await status.edit_text("📤 Uploading...")
        await m.reply_audio(path, caption=f"🎧 {title}\n💗 Requested by: {m.from_user.mention}")
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ Upload failed: {e}")
    finally:
        cleanup(path)


@app.on_message(filters.command("video") & (filters.private | filters.group))
async def video_cmd(_, m):
    query = " ".join(m.command[1:])
    if not query:
        return await m.reply_text("💗 Baby song ya link do 😘\n\nUsage: /video <name or link>")
    await m.reply_text(
        f"💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 Video Mode 🎬\n\n👉 **{query}**\n\nChoose quality baby 😘",
        reply_markup=quality_buttons(query),
    )


@app.on_message(filters.command("spotify") & (filters.private | filters.group))
async def spotify_cmd(_, m):
    query = " ".join(m.command[1:])
    if not query:
        return await m.reply_text("🎧 Song name do baby 😘\n\nUsage: /spotify <song name>")
    await m.reply_text(
        f"🎧 Spotify style search:\n\n👉 **{query}**\n\n💗 Searching on YouTube...\nChoose quality 👇",
        reply_markup=quality_buttons(query),
    )


@app.on_message(filters.command("music"))
async def music_cmd(_, m):
    await m.reply_text(f"🎧 Aaj ki vibe:\n{random.choice(MUSIC_SUGGESTIONS)}")


@app.on_message(filters.command("stop"))
async def stop_cmd(_, m):
    QUEUE.clear()
    await m.reply_text("😢 Music stopped... Fir se /play karo 💗")


# ─── Instagram ────────────────────────────────────────────────────────────────

async def _send_insta(m, url):
    status = await m.reply_text("💗 Downloading from Instagram... ⏳")
    path, title = await asyncio.get_event_loop().run_in_executor(None, download_insta_sync, url)
    if not path:
        return await status.edit_text("❌ Download failed 😢\nCheck the link baby!")
    try:
        if path.endswith((".mp4", ".mkv", ".webm", ".mov")):
            await m.reply_video(
                path,
                caption=f"💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 Instagram Reel 🎬",
                supports_streaming=True,
            )
        else:
            await m.reply_photo(
                path,
                caption=f"💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 Instagram Post 📸",
            )
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ Upload failed: {e}")
    finally:
        cleanup(path)


@app.on_message(filters.command("ig") & (filters.private | filters.group))
async def ig_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text("💗 Baby Instagram link do 😘\n\nUsage: /ig <instagram link>")
    await _send_insta(m, m.command[1])


@app.on_message(filters.text & filters.regex(r"instagram\.com") & (filters.private | filters.group))
async def auto_ig(_, m):
    url = m.text.strip()
    await _send_insta(m, url)


# ─── Love Zone ────────────────────────────────────────────────────────────────

@app.on_message(filters.command("love"))
async def love_cmd(_, m):
    score = random.randint(1, 100)
    hearts = "❤️" * (score // 20)
    await m.reply_text(
        f"💗 Love Meter for {m.from_user.mention}:\n\n{hearts}\n\n❤️ Love: **{score}%** 😍"
    )


@app.on_message(filters.command("kiss"))
async def kiss_cmd(_, m):
    target = m.reply_to_message.from_user.mention if m.reply_to_message else "everyone 💋"
    await m.reply_text(f"😘 {m.from_user.mention} ne {target} ko kiss bheja 💋\n\nMuah! 💗")


@app.on_message(filters.command("hug"))
async def hug_cmd(_, m):
    target = m.reply_to_message.from_user.mention if m.reply_to_message else "everyone 💞"
    await m.reply_text(f"🤗 {m.from_user.mention} ne {target} ko hug diya 💞\n\nAwww! 💗")


@app.on_message(filters.command("shayari"))
async def shayari_cmd(_, m):
    await m.reply_text(random.choice(SHAYARI_LIST))


# ─── Fun Zone ─────────────────────────────────────────────────────────────────

@app.on_message(filters.command("fun"))
async def fun_cmd(_, m):
    await m.reply_text("😂 Fun Zone:\n/joke /roast /rate /pick /fight /wins")


@app.on_message(filters.command("joke"))
async def joke_cmd(_, m):
    jokes = [
        "Why did the programmer quit? Because he didn't get arrays! 😂",
        "I told my computer I needed a break — it froze! 🥶",
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "A SQL query walks into a bar... 'Can I join you?' 😂",
        "Why was the JS developer sad? He didn't know how to 'null' his feelings! 😢",
    ]
    await m.reply_text(f"🤣 {random.choice(jokes)}")


@app.on_message(filters.command("fight"))
async def fight_cmd(_, m):
    await m.reply_text(
        "⚔️ Fight Result:\n\n🥊 Rajan Baby VS Enemy\n\n"
        "💥 Round 1 — Rajan Baby WINS!\n"
        "💥 Round 2 — Rajan Baby WINS!\n"
        "💥 Round 3 — Rajan Baby WINS!\n\n"
        "🏆 RAJAN BABY IS UNDEFEATED! 👑"
    )


@app.on_message(filters.command("wins"))
async def wins_cmd(_, m):
    await m.reply_text(
        "💥 𝗥𝗔𝗝𝗔𝗡 𝗔𝗟𝗪𝗔𝗬𝗦 𝗪𝗜𝗡𝗦 💥\n\n"
        "👑 King of Bots • 🔥 Unstoppable • 💗 Pure Vibes"
    )


@app.on_message(filters.command("roast"))
async def roast_cmd(_, m):
    roasts = [
        "🔥 You're so slow, even dial-up internet feels sorry for you!",
        "🔥 Your Wi-Fi password is probably 'password123' isn't it? 😂",
        "🔥 Even Google can't find your talent! 😂",
        "🔥 You're hot but your code crashes! 💀",
    ]
    target = m.reply_to_message.from_user.mention if m.reply_to_message else m.from_user.mention
    await m.reply_text(f"🔥 {target}: {random.choice(roasts)}")


@app.on_message(filters.command("rate"))
async def rate_cmd(_, m):
    score = random.randint(1, 10)
    await m.reply_text(f"{'⭐' * score}\n\n⭐ Rating: {score}/10")


@app.on_message(filters.command("pick"))
async def pick_cmd(_, m):
    text = " ".join(m.command[1:])
    if " or " in text.lower():
        a, b = text.split(" or ", 1)
        choice = random.choice([a.strip(), b.strip()])
        await m.reply_text(f"🤔 Main choose karta hun:\n\n👉 **{choice}** 💗")
    else:
        await m.reply_text("Usage: /pick option1 or option2")


# ─── AI & Logo ────────────────────────────────────────────────────────────────

@app.on_message(filters.command("ai"))
async def ai_cmd(_, m):
    query = " ".join(m.command[1:])
    reply = random.choice(AI_REPLIES)
    if query:
        await m.reply_text(f"🤖 AI Baby:\n\n💭 You asked: \"{query}\"\n\n💡 {reply}")
    else:
        await m.reply_text(f"🤖 AI Baby:\n\n{reply}")


@app.on_message(filters.command("logo"))
async def logo_cmd(_, m):
    text = " ".join(m.command[1:])
    if not text:
        return await m.reply_text("💗 Baby naam likho 😘\n\nUsage: /logo <your text>")

    logo_path = os.path.join(TMP, "logo.png")
    try:
        img = Image.new("RGB", (800, 300), color=(15, 15, 30))
        draw = ImageDraw.Draw(img)

        # gradient background
        for y in range(300):
            r = int(180 * (y / 300))
            g = int(0 + 20 * (y / 300))
            b = int(100 + 100 * (y / 300))
            draw.line([(0, y), (800, y)], fill=(r, g, b))

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        except Exception:
            font = ImageFont.load_default()

        # shadow
        draw.text((104, 104), text, font=font, fill=(0, 0, 0, 128))
        # main text
        draw.text((100, 100), text, font=font, fill=(255, 220, 240))

        # border
        draw.rectangle([(5, 5), (795, 295)], outline=(255, 100, 180), width=3)

        img.save(logo_path)
        await m.reply_photo(logo_path, caption=f"🎨 **{text}**\n💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 Logo")
    except Exception as e:
        await m.reply_text(f"❌ Logo error: {e}")
    finally:
        cleanup(logo_path)


# ─── Admin Zone ───────────────────────────────────────────────────────────────

@app.on_message(filters.command("kick") & filters.group)
async def kick_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin kar sakte hain yeh! 😘")
    if not m.reply_to_message:
        return await m.reply_text("💗 Kisi user ko reply karo pehle!")
    u = m.reply_to_message.from_user
    try:
        await client.ban_chat_member(m.chat.id, u.id)
        await client.unban_chat_member(m.chat.id, u.id)
        await m.reply_text(f"👢 {u.mention} ko kick kar diya! 💔\n\nBye bye~")
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")


@app.on_message(filters.command("ban") & filters.group)
async def ban_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin kar sakte hain yeh! 😘")
    if not m.reply_to_message:
        return await m.reply_text("💗 Kisi user ko reply karo pehle!")
    u = m.reply_to_message.from_user
    try:
        await client.ban_chat_member(m.chat.id, u.id)
        await m.reply_text(f"🔨 {u.mention} permanently banned! 💔")
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")


@app.on_message(filters.command("mute") & filters.group)
async def mute_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin kar sakte hain yeh! 😘")
    if not m.reply_to_message:
        return await m.reply_text("💗 Kisi user ko reply karo pehle!")
    u = m.reply_to_message.from_user
    try:
        await client.restrict_chat_member(m.chat.id, u.id, ChatPermissions())
        await m.reply_text(f"🤫 {u.mention} muted! 💗")
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")


@app.on_message(filters.command("unmute") & filters.group)
async def unmute_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin kar sakte hain yeh! 😘")
    if not m.reply_to_message:
        return await m.reply_text("💗 Kisi user ko reply karo pehle!")
    u = m.reply_to_message.from_user
    try:
        await client.restrict_chat_member(
            m.chat.id, u.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        await m.reply_text(f"🔊 {u.mention} unmuted! 😍")
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")


@app.on_message(filters.command("promote") & filters.group)
async def promote_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin kar sakte hain yeh! 😘")
    if not m.reply_to_message:
        return await m.reply_text("💗 Kisi user ko reply karo pehle!")
    u = m.reply_to_message.from_user
    try:
        await client.promote_chat_member(
            m.chat.id, u.id,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
        )
        await m.reply_text(f"👑 {u.mention} ko admin bana diya! 🔥")
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")


@app.on_message(filters.command("demote") & filters.group)
async def demote_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin kar sakte hain yeh! 😘")
    if not m.reply_to_message:
        return await m.reply_text("💗 Kisi user ko reply karo pehle!")
    u = m.reply_to_message.from_user
    try:
        await client.promote_chat_member(
            m.chat.id, u.id,
            can_delete_messages=False,
            can_restrict_members=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        await m.reply_text(f"😏 {u.mention} ka admin hata diya! 💔")
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")


# ─── File ID Helper ───────────────────────────────────────────────────────────

@app.on_message(filters.audio)
async def get_file_id(_, message):
    file_id = message.audio.file_id
    await message.reply_text(f"📎 FILE ID:\n`{file_id}`")


# ─── Welcome Video ────────────────────────────────────────────────────────────

welcome_status: dict[int, bool] = {}

WELCOME_AUDIO_FILE_ID = "CQACAgIAAxkBAAIBHmm6ErvJEZZHf93Cpc3ySSAhSj48AAJwXAACJWHZSaqkOllDtVTrHgQ"


@app.on_message(filters.command(["welcome", "welcome_on", "welcome_off"]) & filters.group)
async def welcome_toggle(_, message: Message):
    chat_id = message.chat.id
    if "off" in message.text.lower():
        welcome_status[chat_id] = False
        await message.reply_text("❌ Welcome video has been disabled for this group.")
    else:
        welcome_status[chat_id] = True
        await message.reply_text("✅ Welcome video is now enabled for this group.")


@app.on_chat_member_updated()
async def welcome_video(client, event: ChatMemberUpdated):
    chat_id = event.chat.id

    if not welcome_status.get(chat_id, True):
        return

    if not event.new_chat_member or event.new_chat_member.status != ChatMemberStatus.MEMBER:
        return

    user = event.new_chat_member.user
    name = user.first_name or "Member"
    username = user.username if user.username else "No Username"
    user_id = user.id

    photo_path = None
    try:
        if user.photo:
            photo_path = await client.download_media(user.photo.big_file_id)
    except Exception:
        pass

    bg_path = os.path.join(TMP, f"bg_{user_id}.png")
    video_path = os.path.join(TMP, f"welcome_{user_id}.mp4")
    audio_path = None

    try:
        # Profile pic (circular)
        if photo_path and os.path.exists(photo_path):
            profile_img = Image.open(photo_path).convert("RGBA").resize((400, 400))
        else:
            profile_img = Image.new("RGBA", (400, 400), (180, 0, 180, 255))
        mask = Image.new("L", (400, 400), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 400, 400), fill=255)
        profile_img.putalpha(mask)

        # Gradient background (row-by-row, fast)
        bg = Image.new("RGB", (800, 800))
        for y in range(800):
            r = int(255 * (y / 800))
            g = int(50 + 50 * (y / 800))
            b = int(255 * (1 - y / 800))
            bg.paste(Image.new("RGB", (800, 1), (r, g, b)), (0, y))
        bg = bg.convert("RGBA")
        bg.paste(profile_img, (200, 100), profile_img)
        bg.convert("RGB").save(bg_path)

        # 20-second video clip
        clip = ImageClip(bg_path).set_duration(20)

        # Neon text overlays
        welcome_text = (
            TextClip("Welcome!", fontsize=70, font="Helvetica-Bold",
                     color="cyan", stroke_color="magenta", stroke_width=3)
            .set_position(("center", 500)).set_duration(20).fadein(1).fadeout(1)
        )
        name_text = (
            TextClip(name, fontsize=55, font="Helvetica-Bold",
                     color="yellow", stroke_color="red", stroke_width=2)
            .set_position(("center", 575)).set_duration(20).fadein(1).fadeout(1)
        )
        id_text = (
            TextClip(f"ID: {user_id}", fontsize=50, font="Helvetica-Bold",
                     color="white", stroke_color="blue", stroke_width=1)
            .set_position(("center", 645)).set_duration(20).fadein(1).fadeout(1)
        )
        username_text = (
            TextClip(f"@{username}", fontsize=50, font="Helvetica-Bold",
                     color="lime", stroke_color="green", stroke_width=1)
            .set_position(("center", 715)).set_duration(20).fadein(1).fadeout(1)
        )

        # Audio
        audio_path = await client.download_media(
            WELCOME_AUDIO_FILE_ID,
            file_name=os.path.join(TMP, f"welcome_audio_{user_id}.mp3"),
        )
        audio = AudioFileClip(audio_path).subclip(0, min(20, AudioFileClip(audio_path).duration))

        # Render
        final_video = CompositeVideoClip(
            [clip, welcome_text, name_text, id_text, username_text]
        ).set_audio(audio)
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: final_video.write_videofile(
                video_path, fps=24, codec="libx264", audio_codec="aac", logger=None
            ),
        )

        await client.send_video(
            chat_id,
            video=video_path,
            caption=f"💗 Welcome {name} to the group! 💗",
        )

    except Exception as e:
        print("Welcome video error:", e)
        try:
            await client.send_message(chat_id, f"💗 Welcome {name}! 😘")
        except Exception:
            pass

    finally:
        for p in [bg_path, video_path, audio_path, photo_path]:
            cleanup(p)


# ─── Spam / GC Tools (Owner Only) ────────────────────────────────────────────

RAJAN_TEXTS = [
    "💖 RAJAN BABY 💖", "💘 RAJAN BABY 💘", "🔥 RAJAN BABY 🔥",
    "😈 RAJAN BABY 😈", "🫷 RAJAN BABY 🫷", "💞 RAJAN BABY 💞",
]

SUDO_FILE = "sudo.json"
SUDO_USERS: set[int] = {OWNER_ID}

if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r", encoding="utf-8") as _f:
            SUDO_USERS = set(int(x) for x in json.load(_f))
    except Exception:
        pass


def _save_sudo():
    with open(SUDO_FILE, "w", encoding="utf-8") as _f:
        json.dump(list(SUDO_USERS), _f)


SPAM_DELAY = 0.01

_group_tasks:  dict[int, asyncio.Task] = {}
_spam_tasks:   dict[int, asyncio.Task] = {}
_emospam_tasks: dict[int, asyncio.Task] = {}

owner_only = filters.user(OWNER_ID)
sudo_only  = filters.user(list(SUDO_USERS))


async def _gc_loop(chat_id: int):
    while True:
        try:
            await app.set_chat_title(chat_id, random.choice(RAJAN_TEXTS))
            await asyncio.sleep(SPAM_DELAY)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.001)


async def _spam_loop(chat_id: int, text: str):
    while True:
        try:
            await app.send_message(chat_id, random.choice(RAJAN_TEXTS) if not text else text)
            await asyncio.sleep(SPAM_DELAY)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.001)


async def _emospam_loop(chat_id: int, text: str):
    while True:
        try:
            await app.send_message(chat_id, random.choice(RAJAN_TEXTS) if not text else text)
            await asyncio.sleep(SPAM_DELAY)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.001)


@app.on_message(filters.command("gcnc") & owner_only)
async def gcnc_cmd(_, m):
    chat_id = m.chat.id
    if chat_id in _group_tasks:
        _group_tasks[chat_id].cancel()
    _group_tasks[chat_id] = asyncio.create_task(_gc_loop(chat_id))
    await m.reply_text("🔄 RAJAN BABY loop started")


@app.on_message(filters.command("stopgcnc") & owner_only)
async def stopgcnc_cmd(_, m):
    chat_id = m.chat.id
    if chat_id in _group_tasks:
        _group_tasks[chat_id].cancel()
        del _group_tasks[chat_id]
    await m.reply_text("⏹ Name loop stopped")


@app.on_message(filters.command("spamloop") & owner_only)
async def spamloop_cmd(_, m):
    chat_id = m.chat.id
    text = " ".join(m.command[1:]) if len(m.command) > 1 else ""
    if chat_id in _spam_tasks:
        _spam_tasks[chat_id].cancel()
    _spam_tasks[chat_id] = asyncio.create_task(_spam_loop(chat_id, text))
    await m.reply_text("🔄 Spam started")


@app.on_message(filters.command(["spam", "stopspam"]) & owner_only)
async def spam_cmd(_, m):
    chat_id = m.chat.id
    if m.command[0] == "stopspam":
        if chat_id in _spam_tasks:
            _spam_tasks[chat_id].cancel()
            del _spam_tasks[chat_id]
        return await m.reply_text("🛑 Spam stopped")
    if chat_id in _spam_tasks:
        _spam_tasks[chat_id].cancel()
    _spam_tasks[chat_id] = asyncio.create_task(_spam_loop(chat_id, ""))
    await m.reply_text("💣 RAJAN WINS SPAM STARTED")


@app.on_message(filters.command("emospam") & owner_only)
async def emospam_cmd(_, m):
    chat_id = m.chat.id
    text = " ".join(m.command[1:]) if len(m.command) > 1 else ""
    if chat_id in _emospam_tasks:
        _emospam_tasks[chat_id].cancel()
    _emospam_tasks[chat_id] = asyncio.create_task(_emospam_loop(chat_id, text))
    await m.reply_text("🔄 Emoji spam started")


@app.on_message(filters.command("stopemospam") & owner_only)
async def stopemospam_cmd(_, m):
    chat_id = m.chat.id
    if chat_id in _emospam_tasks:
        _emospam_tasks[chat_id].cancel()
        del _emospam_tasks[chat_id]
    await m.reply_text("🛑 Emoji spam stopped")


# ─── Owner Tag Song ───────────────────────────────────────────────────────────

OWNER_SONG_FILE_ID = "CQACAgUAAxkBAAIBF2m6DIl9bcZ8lG-s8EMM8hRdDd7fAAJgHgACp23QVQlMqMCvBhsKHgQ"


@app.on_message(filters.group & filters.text)
async def owner_song(_, message):
    if message.text and "@replyraid" in message.text:
        caption = (
            "💗 𝑶𝒚𝒆𝒆 😘 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 𝑶𝑷 💗\n\n"
            "👀 𝑲𝒐𝒊 𝒐𝒘𝒏𝒆𝒓 𝒌𝒐 𝒕𝒂𝒈 𝒌𝒂𝒓 𝒓𝒂𝒉𝒂 𝒉𝒂𝒊 😏\n"
            "💘 𝑳𝒂𝒈𝒕𝒂 𝒉𝒂𝒊 𝒅𝒊𝒍 𝒂𝒂 𝒈𝒚𝒂 💕\n\n"
            "🎧 𝑺𝒐𝒏𝒈 𝒕𝒖𝒓𝒂𝒏𝒕 𝒂𝒂 𝒓𝒂𝒉𝒂 𝒉𝒂𝒊 🔥\n"
            "😘 𝑬𝒏𝒋𝒐𝒚 𝒎𝒚 𝒃𝒂𝒃𝒚 💗"
        )
        try:
            await message.reply_audio(audio=OWNER_SONG_FILE_ID, caption=caption)
        except Exception:
            try:
                await message.reply_text(caption)
            except Exception:
                pass


# ─── 🎙 TTS / Voice ───────────────────────────────────────────────────────────

def _tts_sync(text, lang, out_path):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(out_path)
    return out_path


@app.on_message(filters.command("tts"))
async def tts_cmd(_, m):
    text = " ".join(m.command[1:])
    if not text and m.reply_to_message and m.reply_to_message.text:
        text = m.reply_to_message.text
    if not text:
        return await m.reply_text("🎙 Usage: /tts <text>\n\nYa kisi text par reply karke /tts likho")
    if len(text) > 500:
        text = text[:500]
    lang = "hi"
    if any(c.isascii() and c.isalpha() for c in text) and not any(ord(c) > 127 for c in text):
        lang = "en"
    out = os.path.join(TMP, f"tts_{m.from_user.id}_{int(time.time())}.mp3")
    status = await m.reply_text("🎙 Voice bana rahi hu baby... 💗")
    try:
        await asyncio.get_event_loop().run_in_executor(None, _tts_sync, text, lang, out)
        await m.reply_voice(out, caption="🎙 💗 Rajan Baby Voice 💗")
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ TTS error: {e}")
    finally:
        cleanup(out)


# ─── 🌐 Translate ─────────────────────────────────────────────────────────────

@app.on_message(filters.command(["tr", "translate"]))
async def translate_cmd(_, m):
    if len(m.command) < 2:
        return await m.reply_text(
            "🌐 Usage: /tr <lang_code> <text>\n\n"
            "Eg: /tr en namaste\n"
            "Codes: en, hi, ur, bn, ta, te, mr, gu, fr, es, ar, zh, ja, ko, ru"
        )
    lang = m.command[1].lower()
    text = " ".join(m.command[2:])
    if not text and m.reply_to_message and m.reply_to_message.text:
        text = m.reply_to_message.text
    if not text:
        return await m.reply_text("💗 Text bhi do baby! Usage: /tr en <text>")
    try:
        translated = await asyncio.get_event_loop().run_in_executor(
            None, lambda: GoogleTranslator(source="auto", target=lang).translate(text)
        )
        await m.reply_text(f"🌐 Translation:\n\n{translated}\n\n💗 Rajan Baby")
    except Exception as e:
        await m.reply_text(f"❌ Translate error: {e}\n\nLang code check karo!")


# ─── 🎤 Lyrics ────────────────────────────────────────────────────────────────

def _fetch_lyrics(query):
    try:
        if " - " in query:
            artist, title = query.split(" - ", 1)
        else:
            parts = query.rsplit(" ", 1)
            artist, title = (parts[1], parts[0]) if len(parts) == 2 else ("", query)
        url = f"https://api.lyrics.ovh/v1/{urllib.parse.quote(artist.strip())}/{urllib.parse.quote(title.strip())}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("lyrics", "").strip()
    except Exception:
        pass
    return None


@app.on_message(filters.command("lyrics"))
async def lyrics_cmd(_, m):
    query = " ".join(m.command[1:])
    if not query:
        return await m.reply_text("🎤 Usage: /lyrics <artist - song>\n\nEg: /lyrics arijit singh - tum hi ho")
    status = await m.reply_text("🎤 Lyrics dhundh rahi hu baby... 💗")
    lyrics = await asyncio.get_event_loop().run_in_executor(None, _fetch_lyrics, query)
    if not lyrics:
        return await status.edit_text("❌ Lyrics nahi mile 😢\nFormat: /lyrics <artist> - <song>")
    if len(lyrics) > 3500:
        lyrics = lyrics[:3500] + "\n\n... (truncated) 💗"
    await status.edit_text(f"🎤 **{query}**\n\n{lyrics}\n\n💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚")


# ─── 🌤 Weather ───────────────────────────────────────────────────────────────

def _fetch_weather(city):
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        r = requests.get(url, timeout=10, headers={"User-Agent": "curl"})
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@app.on_message(filters.command("weather"))
async def weather_cmd(_, m):
    city = " ".join(m.command[1:])
    if not city:
        return await m.reply_text("🌤 Usage: /weather <city>\n\nEg: /weather Delhi")
    status = await m.reply_text(f"🌤 {city} ka mausam check kar rahi hu... 💗")
    data = await asyncio.get_event_loop().run_in_executor(None, _fetch_weather, city)
    if not data:
        return await status.edit_text("❌ Weather nahi mila 😢")
    try:
        cur = data["current_condition"][0]
        area = data["nearest_area"][0]
        await status.edit_text(
            f"🌤 **{area['areaName'][0]['value']}, {area['country'][0]['value']}**\n\n"
            f"🌡 Temp: {cur['temp_C']}°C ({cur['temp_F']}°F)\n"
            f"🤔 Feels: {cur['FeelsLikeC']}°C\n"
            f"☁️ Sky: {cur['weatherDesc'][0]['value']}\n"
            f"💧 Humidity: {cur['humidity']}%\n"
            f"💨 Wind: {cur['windspeedKmph']} km/h\n"
            f"👁 Visibility: {cur['visibility']} km\n\n"
            f"💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 Weather"
        )
    except Exception as e:
        await status.edit_text(f"❌ Parse error: {e}")


# ─── 🎨 AI Image (Pollinations) ───────────────────────────────────────────────

@app.on_message(filters.command("imagine"))
async def imagine_cmd(_, m):
    prompt = " ".join(m.command[1:])
    if not prompt:
        return await m.reply_text("🎨 Usage: /imagine <prompt>\n\nEg: /imagine cute cat in space")
    status = await m.reply_text("🎨 AI image bana rahi hu baby... ⏳")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=768&height=768&nologo=true"
        await m.reply_photo(url, caption=f"🎨 **{prompt}**\n💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚 AI Art")
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ Image error: {e}")


# ─── 🖼 Wallpaper ─────────────────────────────────────────────────────────────

@app.on_message(filters.command("wallpaper"))
async def wallpaper_cmd(_, m):
    cat = " ".join(m.command[1:]) or "nature"
    try:
        url = f"https://source.unsplash.com/1080x1920/?{urllib.parse.quote(cat)}"
        await m.reply_photo(url, caption=f"🖼 **{cat}** wallpaper\n💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚")
    except Exception as e:
        await m.reply_text(f"❌ Wall error: {e}")


# ─── 💗 Text Sticker ──────────────────────────────────────────────────────────

@app.on_message(filters.command("sticker"))
async def sticker_cmd(client, m):
    out = os.path.join(TMP, f"sticker_{int(time.time())}.webp")
    src = None

    # Photo reply mode
    if m.reply_to_message and (m.reply_to_message.photo or m.reply_to_message.sticker):
        try:
            src = await m.reply_to_message.download(
                file_name=os.path.join(TMP, f"src_{int(time.time())}.png")
            )
            img = Image.open(src).convert("RGBA")
            img.thumbnail((512, 512), Image.LANCZOS)
            new = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            offset = ((512 - img.width) // 2, (512 - img.height) // 2)
            new.paste(img, offset, img if img.mode == "RGBA" else None)
            new.save(out, "WEBP")
            await m.reply_sticker(out)
            return
        except Exception as e:
            await m.reply_text(f"❌ Photo sticker error: {e}")
            return
        finally:
            cleanup(src); cleanup(out)

    # Text mode
    text = " ".join(m.command[1:])
    if not text:
        return await m.reply_text(
            "💗 Usage:\n• Photo pe reply karke /sticker — photo → sticker\n• /sticker <text> — text sticker"
        )
    try:
        img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except Exception:
            font = ImageFont.load_default()
        words = text.split()
        lines, line = [], ""
        for w in words:
            if len(line + w) > 12:
                lines.append(line.strip()); line = w + " "
            else:
                line += w + " "
        if line: lines.append(line.strip())
        y = 256 - (len(lines) * 70 // 2)
        for ln in lines:
            bbox = draw.textbbox((0, 0), ln, font=font)
            w = bbox[2] - bbox[0]
            x = (512 - w) // 2
            draw.text((x+3, y+3), ln, font=font, fill=(0, 0, 0, 200))
            draw.text((x, y), ln, font=font, fill=(255, 100, 200, 255))
            y += 70
        img.save(out, "WEBP")
        await m.reply_sticker(out)
    except Exception as e:
        await m.reply_text(f"❌ Sticker error: {e}")
    finally:
        cleanup(out)


# ─── 📞 Fake Call ─────────────────────────────────────────────────────────────

@app.on_message(filters.command("fakecall"))
async def fakecall_cmd(_, m):
    name = " ".join(m.command[1:]) or "Rajan Baby 💗"
    out = os.path.join(TMP, f"call_{int(time.time())}.png")
    try:
        img = Image.new("RGB", (720, 1280), (10, 10, 30))
        draw = ImageDraw.Draw(img)
        for y in range(1280):
            v = int(40 + (y / 1280) * 30)
            draw.line([(0, y), (720, y)], fill=(v // 3, 0, v))
        try:
            big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except Exception:
            big = small = ImageFont.load_default()
        draw.ellipse((260, 280, 460, 480), fill=(255, 100, 200))
        draw.text((310, 350), "💗", font=big, fill="white")
        draw.text((360 - len(name)*15, 540), name, font=big, fill="white")
        draw.text((250, 620), "Incoming call...", font=small, fill=(200, 200, 200))
        draw.ellipse((100, 1050, 250, 1200), fill=(220, 30, 30))
        draw.ellipse((470, 1050, 620, 1200), fill=(30, 200, 30))
        draw.text((150, 1100), "❌", font=big, fill="white")
        draw.text((520, 1100), "✅", font=big, fill="white")
        img.save(out)
        await m.reply_photo(out, caption=f"📞 Incoming call from **{name}** 💗")
    except Exception as e:
        await m.reply_text(f"❌ Call error: {e}")
    finally:
        cleanup(out)


# ─── 💰 Coins / Economy ───────────────────────────────────────────────────────

COINS_FILE = "coins.json"
COINS: dict[str, dict] = {}
if os.path.exists(COINS_FILE):
    try:
        with open(COINS_FILE, "r") as _f: COINS = json.load(_f)
    except Exception: pass


def _save_coins():
    with open(COINS_FILE, "w") as _f: json.dump(COINS, _f)


def _user(uid):
    s = str(uid)
    if s not in COINS:
        COINS[s] = {"coins": 100, "last_daily": 0}
    return COINS[s]


@app.on_message(filters.command("coins"))
async def coins_cmd(_, m):
    u = _user(m.from_user.id)
    await m.reply_text(f"💰 {m.from_user.mention} ke coins:\n\n💗 **{u['coins']}** coins\n\n/daily se free coins lo!")


@app.on_message(filters.command("daily"))
async def daily_cmd(_, m):
    u = _user(m.from_user.id)
    now = int(time.time())
    if now - u.get("last_daily", 0) < 86400:
        rem = 86400 - (now - u["last_daily"])
        return await m.reply_text(f"⏰ Already claimed! Wait {rem//3600}h {(rem%3600)//60}m 💗")
    bonus = random.randint(100, 500)
    u["coins"] += bonus
    u["last_daily"] = now
    _save_coins()
    await m.reply_text(f"🎁 Daily bonus claimed!\n\n💰 +{bonus} coins\n💗 Total: {u['coins']}")


@app.on_message(filters.command("dice"))
async def dice_cmd(_, m):
    bet = 10
    if len(m.command) > 1:
        try: bet = max(1, int(m.command[1]))
        except: pass
    u = _user(m.from_user.id)
    if u["coins"] < bet:
        return await m.reply_text(f"💔 Coins kam hain! Tumhare paas: {u['coins']}")
    roll = random.randint(1, 6)
    if roll >= 4:
        u["coins"] += bet
        msg = f"🎲 Rolled **{roll}** — YOU WIN! +{bet} 💗\nBalance: {u['coins']}"
    else:
        u["coins"] -= bet
        msg = f"🎲 Rolled **{roll}** — You lose! -{bet} 💔\nBalance: {u['coins']}"
    _save_coins()
    await m.reply_text(msg)


@app.on_message(filters.command("slots"))
async def slots_cmd(_, m):
    bet = 20
    if len(m.command) > 1:
        try: bet = max(1, int(m.command[1]))
        except: pass
    u = _user(m.from_user.id)
    if u["coins"] < bet:
        return await m.reply_text(f"💔 Coins kam hain! Tumhare paas: {u['coins']}")
    syms = ["🍒","🍋","🍇","💗","⭐","7️⃣"]
    a, b, c = random.choice(syms), random.choice(syms), random.choice(syms)
    if a == b == c:
        win = bet * 10
        u["coins"] += win
        msg = f"🎰 [ {a} | {b} | {c} ]\n\n🎉 JACKPOT! +{win} 💗"
    elif a == b or b == c:
        win = bet * 2
        u["coins"] += win
        msg = f"🎰 [ {a} | {b} | {c} ]\n\n💗 Pair win! +{win}"
    else:
        u["coins"] -= bet
        msg = f"🎰 [ {a} | {b} | {c} ]\n\n💔 Loss! -{bet}"
    _save_coins()
    await m.reply_text(msg + f"\nBalance: {u['coins']}")


# ─── 🧠 Quiz / Truth / Dare / Quote / Horoscope / Breakup ────────────────────

QUIZ_LIST = [
    ("Capital of India?", "delhi"),
    ("Kaun banega crorepati ka host?", "amitabh"),
    ("Largest planet?", "jupiter"),
    ("Tum hi ho — singer?", "arijit"),
    ("World's tallest mountain?", "everest"),
    ("Kabaddi mein kitne players?", "7"),
    ("National bird of India?", "peacock"),
    ("Bitcoin creator (alias)?", "satoshi"),
    ("Speed of light (km/s, approx)?", "300000"),
    ("Apple ka founder?", "steve jobs"),
]
TRUTH_LIST = [
    "Sabse pehla crush kaun tha? 😏",
    "Last time kab jhooth bola tha? 🤥",
    "Phone mein sabse embarrassing photo? 📸",
    "Worst habit tumhari? 😅",
    "Ek raaz jo ghar wale nahi jaante? 🤫",
    "Crush ka naam yahaan likho! 💗",
    "Sabse zyada kispe pyaar aata hai? 😘",
]
DARE_LIST = [
    "Apna pet name yahaan likho! 😂",
    "Ek pickup line bolo crush ke liye 💘",
    "Singing emoji se ek song gaao 🎤",
    "Apni sabse purani photo bhejo 📸",
    "Aapas mein 5 baar 'Rajan Baby OP' likho 💗",
    "Last bheji story ka screenshot bhejo 🤳",
    "10 second tak mute raho! 🤐",
]
QUOTE_LIST = [
    "💗 Zindagi ek safar hai suhana — har mod pe Rajan Baby ke saath!",
    "🌟 Sapne dekho, bade dekho, par RAJAN style mein!",
    "🔥 Haar wahan hoti hai jahaan koshish nahi hoti.",
    "💞 Pyaar wahi sachha hai jo bina shart ho.",
    "👑 Khud pe yakeen rakho — duniya jhuk jayegi!",
]
BREAKUP_LIST = [
    "💔 Tum ghee ho main toast, tumhe khaya bahut, ab break-up ka boast!",
    "💔 Tumhari yaadein WiFi ki tarah hain — kabhi connect, kabhi disconnect.",
    "💔 Tum 4G ho, main 5G — humara match nahi banta!",
    "💔 Block list ki shayari: 'Tum ho, par ab dikhte nahi.'",
]
HORO = {
    "aries": "🐏 Aaj koi naya plan banao — luck saath hai!",
    "taurus": "🐂 Paisa kamane ka mood? Try kar lo!",
    "gemini": "👯 Dosti mein twist aane wala hai 💗",
    "cancer": "🦀 Family time ka din — enjoy karo!",
    "leo": "🦁 King vibes — sab kuch tumhare pakshe!",
    "virgo": "🌾 Detail pe dhyaan do, success milegi.",
    "libra": "⚖️ Balance maintain karo — pyaar mein bhi.",
    "scorpio": "🦂 Intense mood, koi raaz khulega!",
    "sagittarius": "🏹 Travel ki vibes aa rahi hain!",
    "capricorn": "🐐 Mehnat ka phal milne wala hai 💰",
    "aquarius": "🏺 Naye ideas explode honge dimaag mein!",
    "pisces": "🐟 Romantic vibes — partner ko surprise do 💗",
}


@app.on_message(filters.command("quiz"))
async def quiz_cmd(_, m):
    q, a = random.choice(QUIZ_LIST)
    await m.reply_text(f"🧠 Quiz:\n\n❓ {q}\n\n💡 Answer reply karo!\n\n*Correct: ||{a}||*")


@app.on_message(filters.command("truth"))
async def truth_cmd(_, m):
    await m.reply_text(f"😈 **TRUTH:**\n\n{random.choice(TRUTH_LIST)}")


@app.on_message(filters.command("dare"))
async def dare_cmd(_, m):
    await m.reply_text(f"🔥 **DARE:**\n\n{random.choice(DARE_LIST)}")


@app.on_message(filters.command("quote"))
async def quote_cmd(_, m):
    await m.reply_text(f"💭 {random.choice(QUOTE_LIST)}")


@app.on_message(filters.command("breakup"))
async def breakup_cmd(_, m):
    target = m.reply_to_message.from_user.mention if m.reply_to_message else "Ex 💔"
    await m.reply_text(f"💔 To {target}:\n\n{random.choice(BREAKUP_LIST)}\n\n— 💗 Rajan Baby")


@app.on_message(filters.command(["horoscope", "horo"]))
async def horo_cmd(_, m):
    sign = (m.command[1].lower() if len(m.command) > 1 else random.choice(list(HORO))).strip()
    msg = HORO.get(sign, "❌ Sign nahi mila.\nUse: aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces")
    await m.reply_text(f"🔮 **{sign.title()}** Horoscope:\n\n{msg}\n\n💗 Rajan Baby")


# ─── 📰 News ──────────────────────────────────────────────────────────────────

def _fetch_news():
    try:
        r = requests.get("https://hnrss.org/frontpage", timeout=10)
        if r.status_code == 200:
            import re
            titles = re.findall(r"<title>(.*?)</title>", r.text)[1:11]
            return titles
    except Exception:
        pass
    return None


@app.on_message(filters.command("news"))
async def news_cmd(_, m):
    status = await m.reply_text("📰 News la rahi hu... 💗")
    titles = await asyncio.get_event_loop().run_in_executor(None, _fetch_news)
    if not titles:
        return await status.edit_text("❌ News nahi aayi 😢")
    text = "📰 **Top Tech News:**\n\n"
    for i, t in enumerate(titles, 1):
        text += f"**{i}.** {t}\n\n"
    text += "💗 𝑹𝒂𝒋𝒂𝒏 𝑩𝒂𝒃𝒚"
    await status.edit_text(text[:4000])


# ─── 🚨 Warn System ───────────────────────────────────────────────────────────

WARNS_FILE = "warns.json"
WARNS: dict[str, dict[str, int]] = {}
if os.path.exists(WARNS_FILE):
    try:
        with open(WARNS_FILE, "r") as _f: WARNS = json.load(_f)
    except Exception: pass


def _save_warns():
    with open(WARNS_FILE, "w") as _f: json.dump(WARNS, _f)


@app.on_message(filters.command("warn") & filters.group)
async def warn_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin warn de sakta hai!")
    if not m.reply_to_message:
        return await m.reply_text("💗 Reply karo user ko warn dene ke liye!")
    u = m.reply_to_message.from_user
    cid, uid = str(m.chat.id), str(u.id)
    WARNS.setdefault(cid, {})
    WARNS[cid][uid] = WARNS[cid].get(uid, 0) + 1
    cnt = WARNS[cid][uid]
    _save_warns()
    if cnt >= 3:
        try:
            await client.ban_chat_member(m.chat.id, u.id)
            WARNS[cid][uid] = 0
            _save_warns()
            await m.reply_text(f"🔨 {u.mention} 3 warns reach! BANNED 💔")
        except Exception as e:
            await m.reply_text(f"⚠️ Warn {cnt}/3 (ban failed: {e})")
    else:
        await m.reply_text(f"⚠️ {u.mention} warned!\n\n📊 Warns: **{cnt}/3**\n3 hone pe BAN!")


@app.on_message(filters.command("warns") & filters.group)
async def warns_cmd(_, m):
    u = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    cid, uid = str(m.chat.id), str(u.id)
    cnt = WARNS.get(cid, {}).get(uid, 0)
    await m.reply_text(f"📊 {u.mention} ke warns: **{cnt}/3**")


@app.on_message(filters.command("resetwarns") & filters.group)
async def resetwarns_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin!")
    if not m.reply_to_message:
        return await m.reply_text("💗 Reply karo!")
    u = m.reply_to_message.from_user
    cid, uid = str(m.chat.id), str(u.id)
    if cid in WARNS and uid in WARNS[cid]:
        WARNS[cid][uid] = 0
        _save_warns()
    await m.reply_text(f"✅ {u.mention} ke warns reset!")


# ─── 💗 GROUP FUN PRO (A-Z) 💗 ───────────────────────────────────────────────

STATS_FILE = "stats.json"
STATS: dict = {}
if os.path.exists(STATS_FILE):
    try:
        with open(STATS_FILE, "r") as _f:
            STATS = json.load(_f)
    except Exception:
        STATS = {}

_stats_dirty = False


def _save_stats_now():
    try:
        with open(STATS_FILE, "w") as _f:
            json.dump(STATS, _f)
    except Exception:
        pass


async def _stats_saver():
    global _stats_dirty
    while True:
        await asyncio.sleep(30)
        if _stats_dirty:
            _save_stats_now()
            _stats_dirty = False


@app.on_message(filters.group & ~filters.bot, group=99)
async def _msg_counter(_, m):
    global _stats_dirty
    if not m.from_user:
        return
    cid, uid = str(m.chat.id), str(m.from_user.id)
    STATS.setdefault(cid, {})
    STATS[cid][uid] = STATS[cid].get(uid, 0) + 1
    _stats_dirty = True


# 🏆 TOP 10
@app.on_message(filters.command(["top", "leaderboard"]) & filters.group)
async def top_cmd(client, m):
    cid = str(m.chat.id)
    if cid not in STATS or not STATS[cid]:
        return await m.reply_text("📊 Abhi koi stats nahi — thoda chat karo phir try!")
    top10 = sorted(STATS[cid].items(), key=lambda x: -x[1])[:10]
    medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
    text = f"🏆 **{stylish('TOP 10 ACTIVE MEMBERS')}** 💗\n\n"
    for i, (uid, count) in enumerate(top10):
        try:
            user = await client.get_users(int(uid))
            name = user.first_name or "User"
        except Exception:
            name = f"User {uid[-4:]}"
        text += f"{medals[i]} {name} — **{count}** msgs\n"
    text += f"\n💗 — {stylish('Rajan Baby')}"
    await m.reply_text(text)


# 📊 MY STATS / LEVEL
@app.on_message(filters.command(["mystats", "level", "stats"]) & filters.group)
async def mystats_cmd(_, m):
    u = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    cid, uid = str(m.chat.id), str(u.id)
    count = STATS.get(cid, {}).get(uid, 0)
    level = count // 100
    progress = count - level * 100
    bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
    title = (
        "👑 King" if level >= 50 else
        "🌟 Star" if level >= 20 else
        "💗 Active" if level >= 10 else
        "🌱 Newbie"
    )
    await m.reply_text(
        f"📊 **{u.first_name}** {stylish('Stats')}\n\n"
        f"💬 Messages: **{count}**\n"
        f"📈 Level: **{level}**\n"
        f"🎖 Title: {title}\n"
        f"📊 [{bar}] {progress}/100\n\n"
        f"💗 — {stylish('Rajan Baby')}"
    )


# 📢 TAG ALL (admin)
@app.on_message(filters.command(["tagall", "all"]) & filters.group)
async def tagall_cmd(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return await m.reply_text("❌ Sirf admin tagall kar sakte hain!")
    msg = " ".join(m.command[1:]) or "💗 Sab attention please!"
    await m.reply_text(f"📢 **{stylish('TAG ALL')}** 💗\n\n{msg}")
    mentions, count = [], 0
    try:
        async for member in client.get_chat_members(m.chat.id):
            if member.user.is_bot or member.user.is_deleted:
                continue
            mentions.append(member.user.mention)
            count += 1
            if len(mentions) >= 5:
                try:
                    await client.send_message(m.chat.id, " ".join(mentions))
                except Exception:
                    pass
                mentions = []
                await asyncio.sleep(2)
            if count >= 50:
                break
    except Exception as e:
        return await m.reply_text(f"❌ Tag error: {e}")
    if mentions:
        try:
            await client.send_message(m.chat.id, " ".join(mentions))
        except Exception:
            pass
    await m.reply_text(f"✅ Tagged **{count}** members 💗")


# 💕 COUPLE OF THE DAY
@app.on_message(filters.command("couple") & filters.group)
async def couple_cmd(client, m):
    cid = str(m.chat.id)
    active = list(STATS.get(cid, {}).keys())
    if len(active) < 2:
        return await m.reply_text("💔 Group mein kam log hain couple ke liye!")
    a, b = random.sample(active, 2)
    try:
        ua = await client.get_users(int(a))
        ub = await client.get_users(int(b))
        love = random.randint(60, 99)
        hearts = "❤️" * (love // 20)
        await m.reply_text(
            f"💕 **{stylish('COUPLE OF THE DAY')}** 💕\n\n"
            f"❤️ {ua.mention}\n💗 {ub.mention}\n\n"
            f"{hearts}\n💘 Love: **{love}%**\n\n"
            f"💗 — {stylish('Rajan Baby Cupid')}"
        )
    except Exception:
        await m.reply_text("❌ Couple banane mein dikkat 😢")


# 👑 KING OF THE DAY
@app.on_message(filters.command("king") & filters.group)
async def king_cmd(client, m):
    cid = str(m.chat.id)
    active = list(STATS.get(cid, {}).keys())
    if not active:
        return await m.reply_text("👑 Koi active user nahi mila!")
    try:
        u = await client.get_users(int(random.choice(active)))
        await m.reply_text(
            f"👑 **{stylish('KING OF THE DAY')}** 👑\n\n"
            f"🌟 {u.mention}\n\n"
            f"Aaj sab uske aage jhuke! 💗\n\n"
            f"💗 — {stylish('Rajan Baby')}"
        )
    except Exception:
        await m.reply_text("👑 King select nahi hua 😅")


# 🍾 SPIN THE BOTTLE
@app.on_message(filters.command("spin") & filters.group)
async def spin_cmd(client, m):
    cid = str(m.chat.id)
    active = list(STATS.get(cid, {}).keys())
    if not active:
        return await m.reply_text("🍾 Koi active user nahi mila!")
    try:
        u = await client.get_users(int(random.choice(active)))
        await m.reply_text(
            f"🍾 Bottle ghoom rahi hai...\n\n"
            f"🎯 Bottle rukgayi: {u.mention} pe! 💗\n\n"
            f"💗 — {stylish('Rajan Baby')}"
        )
    except Exception:
        await m.reply_text("🍾 Bottle gum ho gayi 😅")


# 💍 SHAADI
@app.on_message(filters.command("shaadi"))
async def shaadi_cmd(_, m):
    if not m.reply_to_message:
        return await m.reply_text("💍 Reply karo us user ko jisse shaadi karwani hai!")
    a, b = m.from_user, m.reply_to_message.from_user
    await m.reply_text(
        f"💒 **{stylish('SHAADI CEREMONY')}** 💒\n\n"
        f"💍 {a.mention}\n❤️ {b.mention}\n\n"
        f"🎉 Mubarak ho! Aaj se tum dono pati-patni ho!\n"
        f"🎊 Pheray ho gaye, kasam khao!\n\n"
        f"💗 — {stylish('Rajan Baby Pandit')}"
    )


# 💔 DIVORCE
@app.on_message(filters.command("divorce"))
async def divorce_cmd(_, m):
    target = m.reply_to_message.from_user.mention if m.reply_to_message else "ex 💔"
    await m.reply_text(
        f"💔 **{stylish('DIVORCE FINALIZED')}** 💔\n\n"
        f"{m.from_user.mention} ne {target} se divorce le liya!\n\n"
        f"😭 Ab dono free hain — naye crush dhoondo!\n\n"
        f"💗 — {stylish('Rajan Baby Court')}"
    )


# 💘 LOVE COMPATIBILITY
@app.on_message(filters.command(["lovecal", "compat", "lovemeter"]))
async def compat_cmd(_, m):
    if not m.reply_to_message:
        return await m.reply_text("💗 Reply karo user ko compatibility check karne!")
    a, b = m.from_user, m.reply_to_message.from_user
    score = random.randint(20, 99)
    bars = "❤️" * (score // 20) + "🤍" * (5 - score // 20)
    verdict = (
        "🔥 PERFECT JODI!" if score >= 90 else
        "💗 BHAI WAH!" if score >= 70 else
        "😅 Try kar lo" if score >= 50 else
        "💔 Bhai bhen lago"
    )
    await m.reply_text(
        f"💘 **{stylish('LOVE COMPATIBILITY')}** 💘\n\n"
        f"{a.mention} ❤️ {b.mention}\n\n"
        f"{bars}\n💗 Match: **{score}%**\n{verdict}\n\n"
        f"💗 — {stylish('Rajan Baby')}"
    )


# 👶 BABY NAME
@app.on_message(filters.command("baby"))
async def baby_cmd(_, m):
    if not m.reply_to_message:
        return await m.reply_text("👶 Reply karo partner ko!")
    a, b = m.from_user, m.reply_to_message.from_user
    names = ["Rajan Jr 💗", "Pari", "Kuku", "Chiku", "Sonu", "Pinky", "Bunty", "Gugu", "Mishti", "Rohan", "Anaya"]
    weight = round(random.uniform(2.5, 4.5), 1)
    await m.reply_text(
        f"👶 **{stylish('Tumhara Baby')}** 💗\n\n"
        f"👨 Papa: {a.mention}\n👩 Mumma: {b.mention}\n\n"
        f"📛 Naam: **{random.choice(names)}**\n"
        f"⚖️ Weight: {weight} kg\n"
        f"😍 Looks: {random.choice(['cute', 'super cute', 'extra cute', 'gol matol', 'sundar'])}\n\n"
        f"💗 — {stylish('Rajan Baby Hospital')}"
    )


# 😈 INSULT (group-safe roast)
INSULTS = [
    "Tum WiFi se bhi slow ho 🐌",
    "Tumhare jokes hospital ke ICU mein hain 💀",
    "Tumhari intelligence Google se bhi miss ho gayi 🤡",
    "Tum aate ho to BSNL ka tower bhi ro deta hai 📡",
    "Tum cute ho — kabhi rules tod ke ghaas mein chhup jao 🐄",
    "Tumhari selfies se mirror crack ho jata hai 🪞",
    "Tum brain bhi rent pe doge to landlord refund maangega 🧠",
    "Tum English bolte ho to dictionary suicide kar leti hai 📚",
    "Tum gym jate ho ya gym tumse bachne bhagta hai? 💪",
]


@app.on_message(filters.command("insult"))
async def insult_cmd(_, m):
    target = m.reply_to_message.from_user.mention if m.reply_to_message else m.from_user.mention
    await m.reply_text(f"😈 {target}\n\n{random.choice(INSULTS)}\n\n💗 — {stylish('Rajan Baby Roast')}")


# 🎭 CHARACTER
CHARS = ["Shahrukh", "Salman", "Heer", "Ranjha", "Kabir Singh", "Geet", "Bunny", "Naina",
         "Radhe", "Bahubali", "Devdas", "Paro", "Munna Bhai", "Jab We Met Aditya", "Rocky"]


@app.on_message(filters.command("character"))
async def character_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    a, b = random.sample(CHARS, 2)
    pa = random.randint(40, 90)
    pb = 100 - pa
    await m.reply_text(
        f"🎭 **{target.first_name}** ka character analysis:\n\n"
        f"🎬 {pa}% **{a}**\n🎬 {pb}% **{b}**\n\n"
        f"💗 — {stylish('Rajan Baby Bollywood')}"
    )


# 🎤 RAJAN BABY RAP
RAAP_LINES = [
    "Tu hai mast, tu hai cool,\nTera dimaag chalta full —",
    "Yo yo, sun le baby,\nRajan Baby tera lagta hai daddy —",
    "Aaja gym, aaja road,\nTu hi hai sabka heart-throb —",
    "Roast karu ya pyaar du,\nDono mein hi tujhe haar du —",
    "Tu hai swag ka raja,\nBolne wala mast taaja —",
]


@app.on_message(filters.command(["raap", "rap"]))
async def raap_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    line = random.choice(RAAP_LINES)
    await m.reply_text(
        f"🎤 **{stylish('RAJAN BABY RAP')}** 🔥\n\n"
        f"Yo {target.first_name}, sun mera flow,\n"
        f"{line}\n"
        f"Mic drop! 🎤💥\n\n"
        f"💗 — {stylish('Rajan Baby')}"
    )


# 💍 PROPOSAL
PROPOSALS = [
    "💗 Tumhare bina mera dil dhadkta nahi, bolo haan ya na?",
    "🌹 Mere saath shaadi karogi please?",
    "💍 Tum mil jao to zindagi sangeet ban jaye!",
    "💕 Main coffee, tum sugar — pi loge mujhe?",
    "🌟 Aasman ke saare tare tumhare liye — bas ek YES!",
]


@app.on_message(filters.command("proposal"))
async def proposal_cmd(_, m):
    if not m.reply_to_message:
        return await m.reply_text("💍 Reply karo crush ko!")
    target = m.reply_to_message.from_user
    await m.reply_text(
        f"💍 **{stylish('PROPOSAL')}** by {m.from_user.mention}\n\n"
        f"Dear {target.mention},\n\n{random.choice(PROPOSALS)}\n\n"
        f"💗 — {stylish('Rajan Baby Cupid')}"
    )


# 💀 DEATH PREDICTION
DEATH_CAUSES = [
    "too much love 💗", "Maggi overdose 🍜", "selfie addiction 🤳",
    "binge watching Netflix 📺", "scrolling reels 24/7 📱",
    "extra cute hone ki wajah se 😍", "crush ne block kar diya 💔",
    "WiFi off ho gaya 📶", "chai khatam ho gayi ☕",
]


@app.on_message(filters.command("death"))
async def death_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    year = random.randint(2050, 2099)
    await m.reply_text(
        f"⚰️ **{stylish('DEATH PREDICTION')}** 💀\n\n"
        f"👤 {target.mention}\n"
        f"📅 Year: **{year}**\n"
        f"⚱️ Cause: **{random.choice(DEATH_CAUSES)}**\n\n"
        f"💗 — {stylish('Rajan Baby Astro')}"
    )


# 💰 NETWORTH
@app.on_message(filters.command(["dhanda", "networth"]))
async def dhanda_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    cr = random.randint(1, 9999)
    src = random.choice([
        "Tinder verified 💗", "Mama ki dukaan 🛒", "Crypto scam 💀",
        "Reels royalty 📱", "YouTube hate 😂", "Pyaar ke chande 💕",
        "PUBG winnings 🎮", "Insta blue tick 💙",
    ])
    await m.reply_text(
        f"💰 **{target.first_name}** ki net worth:\n\n"
        f"💸 ₹{cr} crore\n"
        f"📈 Source: {src}\n\n"
        f"💗 — {stylish('Rajan Baby Forbes')}"
    )


# 🔮 KISMAT
KISMAT = [
    "Aaj tumhe surprise milega 🎁",
    "Crush ka message aane wala hai 💌",
    "Paisa milega aaj 💰",
    "Bahut load hai aaj — chai pi lo ☕",
    "Naya friend banega 🤝",
    "Khud se pyaar karo aaj 💗",
    "Kisi ka block khulega 🔓",
    "Lottery ka chance hai 🎰",
]


@app.on_message(filters.command("kismat"))
async def kismat_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    await m.reply_text(
        f"🔮 **{target.first_name}** ki aaj ki kismat:\n\n"
        f"✨ {random.choice(KISMAT)}\n\n"
        f"💗 — {stylish('Rajan Baby')}"
    )


# 🧠 IQ TEST
@app.on_message(filters.command(["iq", "iqtest"]))
async def iq_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    iq = random.randint(50, 200)
    verdict = (
        "🧠 GENIUS!" if iq >= 150 else
        "💡 Smart!" if iq >= 110 else
        "😊 Average" if iq >= 80 else
        "🤡 Bhai pading shuru karo"
    )
    await m.reply_text(
        f"🧠 **IQ Test** — {target.first_name}\n\n"
        f"📊 IQ: **{iq}**\n"
        f"{verdict}\n\n"
        f"💗 — {stylish('Rajan Baby Lab')}"
    )


# 🎮 ROCK PAPER SCISSORS
@app.on_message(filters.command(["rps"]))
async def rps_cmd(_, m):
    target_name = m.reply_to_message.from_user.mention if m.reply_to_message else "Bot 🤖"
    a = random.choice(["🪨", "📄", "✂️"])
    b = random.choice(["🪨", "📄", "✂️"])
    if a == b:
        result = "🤝 Tie!"
    elif (a, b) in [("🪨", "✂️"), ("📄", "🪨"), ("✂️", "📄")]:
        result = f"🏆 {m.from_user.mention} WINS! 💗"
    else:
        result = f"🏆 {target_name} WINS! 💗"
    await m.reply_text(
        f"🎮 **Rock Paper Scissors** 🎮\n\n"
        f"{m.from_user.mention}: {a}\n{target_name}: {b}\n\n{result}"
    )


# 🏁 RACE
@app.on_message(filters.command("race") & filters.group)
async def race_cmd(_, m):
    racers = ["🐎", "🐢", "🐰", "🚗", "🦄"]
    winner = random.choice(racers)
    await m.reply_text(
        f"🏁 **{stylish('RACE START')}** 🏁\n\n"
        f"Racers: {' '.join(racers)}\n\n"
        f"⚡ 3...2...1... GO!\n\n"
        f"🏆 Winner: **{winner}** 💗\n\n"
        f"💗 — {stylish('Rajan Baby')}"
    )


# 🤚 PETPET
@app.on_message(filters.command("petpet"))
async def petpet_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    await m.reply_text(
        f"🤚 *pat pat pat* {target.mention} 💗\n\n"
        f"😘 Aww kitne cute ho!\n\n"
        f"💗 — {stylish('Rajan Baby')}"
    )


# 🌅 GOODMORNING
GM_QUOTES = [
    "🌅 Sun ne kaha — uth jao baby!",
    "☀️ Aaj ka din tumhara hai — go win it!",
    "🌸 Subha ke phool tumhare liye 💗",
    "💗 Goodmorning sweetu! Chai pi lo 😘",
    "🌞 Aaj smile karna mat bhulna 💗",
]


@app.on_message(filters.command(["gm", "goodmorning"]))
async def gm_cmd(_, m):
    await m.reply_text(
        f"🌅 **{stylish('Goodmorning')}** {m.from_user.mention}!\n\n"
        f"{random.choice(GM_QUOTES)}\n\n💗 — {stylish('Rajan Baby')}"
    )


# 🌙 GOODNIGHT
GN_QUOTES = [
    "🌙 Subah jaldi uth jana, sapne mein milte hain 💗",
    "✨ Stars dekh kar so jao — kal sab badiya hoga!",
    "💗 Goodnight baby — sweet dreams 😘",
    "🌃 Phone band kar do, neend tujhe yaad kar rahi hai!",
    "🌜 Chand dekh ke so jao 💗",
]


@app.on_message(filters.command(["gn", "goodnight"]))
async def gn_cmd(_, m):
    await m.reply_text(
        f"🌙 **{stylish('Goodnight')}** {m.from_user.mention}!\n\n"
        f"{random.choice(GN_QUOTES)}\n\n💗 — {stylish('Rajan Baby')}"
    )


# 🤡 CLOWN
@app.on_message(filters.command("clown"))
async def clown_cmd(_, m):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    await m.reply_text(
        f"🤡 **CLOWN OF THE DAY** 🤡\n\n"
        f"👉 {target.mention} 🤡🤡🤡\n\n"
        f"💗 — {stylish('Rajan Baby Circus')}"
    )


# 🎂 SHAYARI
SHAYARIS = [
    "Mohabbat ek nasha hai,\nJise pee liya use bhula nahi sakta — 💗",
    "Tere bina dil pe ek bhi nahi,\nBas tu hi tu hai meri zindagi mein — 💕",
    "Chai ki pyaali mein chini kam,\nTeri yaadon mein meri neend gum — ☕",
    "Aankhein band karu to tu dikhe,\nKhol du to tu zindagi banke chhupe — 👀",
]


@app.on_message(filters.command(["shayari", "shyri"]))
async def shayari_cmd(_, m):
    await m.reply_text(
        f"📜 **{stylish('Shayari')}** 💗\n\n"
        f"{random.choice(SHAYARIS)}\n\n"
        f"💗 — {stylish('Rajan Baby')}"
    )


# ─── Clone Bot System ────────────────────────────────────────────────────────

CLONES_FILE = "clones.json"
CLONES: dict[int, dict] = {}
ACTIVE_CLONES: dict[int, Client] = {}
MAIN_BOT_NAME = "rajan_baby_bot"

if os.path.exists(CLONES_FILE):
    try:
        with open(CLONES_FILE, "r", encoding="utf-8") as _f:
            CLONES = {int(k): v for k, v in json.load(_f).items()}
    except Exception:
        pass


def _save_clones():
    with open(CLONES_FILE, "w", encoding="utf-8") as _f:
        json.dump({str(k): v for k, v in CLONES.items()}, _f)


def _copy_handlers_to_clone(clone: Client):
    for group, handlers in app.dispatcher.groups.items():
        for handler in handlers:
            try:
                clone.add_handler(handler, group)
            except Exception:
                pass


async def _start_clone(user_id: int, token: str):
    if user_id in ACTIVE_CLONES:
        return False, "❌ Tumhara clone already running hai. /delclone karke fir try karo."
    session_name = f"clone_{user_id}"
    try:
        clone = Client(
            session_name,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=token,
        )
        _copy_handlers_to_clone(clone)
        await clone.start()
        me = await clone.get_me()
        ACTIVE_CLONES[user_id] = clone
        CLONES[user_id] = {
            "token": token,
            "username": me.username,
            "name": me.first_name,
        }
        _save_clones()
        return True, (
            f"✅ Clone Bot Started! 💗\n\n"
            f"🤖 @{me.username}\n"
            f"👑 Name: {me.first_name}\n\n"
            f"💗 Tumhara bot ab Rajan Baby ki tarah saare features chala raha hai!\n"
            f"📋 /myclone — status\n"
            f"🛑 /delclone — band karne ke liye"
        )
    except Exception as e:
        for ext in (".session", ".session-journal"):
            p = session_name + ext
            if os.path.exists(p):
                try: os.remove(p)
                except Exception: pass
        return False, f"❌ Clone failed: `{e}`\n\nToken sahi hai? @BotFather se naya banao!"


async def _stop_clone(user_id: int):
    if user_id not in ACTIVE_CLONES:
        return False
    clone = ACTIVE_CLONES.pop(user_id)
    try:
        await clone.stop()
    except Exception:
        pass
    return True


@app.on_message(filters.command("clone") & filters.private)
async def clone_cmd(client, m):
    if len(m.command) < 2:
        return await m.reply_text(
            "💗 𝗖𝗟𝗢𝗡𝗘 𝗕𝗢𝗧 𝗦𝗬𝗦𝗧𝗘𝗠 💗\n\n"
            "Apna BOT TOKEN do baby 😘\n\n"
            "Usage: `/clone <BOT_TOKEN>`\n\n"
            "📝 Steps:\n"
            "1. @BotFather pe jao\n"
            "2. /newbot karke naya bot banao\n"
            "3. Token copy karke yahaan paste karo:\n"
            "   `/clone 123456:ABC-DEF...`\n\n"
            "💗 Phir tumhara bot bilkul mere jaisa ban jayega!"
        )
    token = m.command[1].strip()
    user_id = m.from_user.id
    status = await m.reply_text("⏳ Clone bot start ho raha hai... please wait")
    ok, msg = await _start_clone(user_id, token)
    await status.edit_text(msg)


@app.on_message(filters.command("myclone") & filters.private)
async def myclone_cmd(client, m):
    user_id = m.from_user.id
    if user_id not in CLONES:
        return await m.reply_text("❌ Tumhara koi clone nahi hai baby.\n\n/clone se banao 💗")
    info = CLONES[user_id]
    status = "🟢 Running" if user_id in ACTIVE_CLONES else "🔴 Stopped"
    await m.reply_text(
        f"🤖 𝗧𝘂𝗺𝗵𝗮𝗿𝗮 𝗖𝗹𝗼𝗻𝗲 𝗕𝗼𝘁:\n\n"
        f"👤 Username: @{info.get('username', 'N/A')}\n"
        f"📛 Name: {info.get('name', 'N/A')}\n"
        f"📊 Status: {status}\n\n"
        f"🛑 /delclone — band karne ke liye"
    )


@app.on_message(filters.command("delclone") & filters.private)
async def delclone_cmd(client, m):
    user_id = m.from_user.id
    if user_id not in CLONES:
        return await m.reply_text("❌ Tumhara koi clone nahi hai.")
    await _stop_clone(user_id)
    CLONES.pop(user_id, None)
    _save_clones()
    for ext in (".session", ".session-journal"):
        p = f"clone_{user_id}{ext}"
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass
    await m.reply_text("✅ Clone bot stop aur delete ho gaya 💔\n\n/clone se phir bana sakte ho!")


@app.on_message(filters.command("clones") & owner_only)
async def clones_list_cmd(client, m):
    if not CLONES:
        return await m.reply_text("📭 Koi clone nahi hai abhi.")
    text = f"📊 Total Clones: {len(CLONES)}\n🟢 Active: {len(ACTIVE_CLONES)}\n\n"
    for uid, info in CLONES.items():
        st = "🟢" if uid in ACTIVE_CLONES else "🔴"
        text += f"{st} @{info.get('username', 'N/A')} — owner: `{uid}`\n"
    await m.reply_text(text)


async def _restore_clones():
    if not CLONES:
        return
    print(f"💗 Restoring {len(CLONES)} clone bots...")
    for user_id, info in list(CLONES.items()):
        try:
            ok, _ = await _start_clone(user_id, info["token"])
            print(f"  Clone {user_id} (@{info.get('username')}): {'OK' if ok else 'FAIL'}")
        except Exception as e:
            print(f"  Clone {user_id} error: {e}")


async def _main():
    await app.start()
    me = await app.get_me()
    print(f"💗 Main Bot @{me.username} started!")
    await _restore_clones()
    asyncio.create_task(_stats_saver())
    print("💗 All systems ready 💗")
    await asyncio.Event().wait()


if __name__ == "__main__":
    print("💗 Starting Rajan Baby Bot v4.0 MEGA... 💗")
    app.run(_main())
