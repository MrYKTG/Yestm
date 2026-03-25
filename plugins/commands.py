import os
import re
import base64
import logging
import random
import asyncio
import string
import sys
import pytz
from .pmfilter import auto_filter 
from Script import script
from datetime import datetime
from database.refer import referdb
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, ChatAdminRequired, UserNotParticipant , ChannelInvalid, PeerIdInvalid
from database.ia_filterdb import Media, Media2, get_file_details, unpack_new_file_id, get_bad_files, save_file
from database.users_chats_db import db
from info import *
from utils import get_settings, save_group_settings, is_subscribed, is_req_subscribed, get_size, get_shortlink, is_check_admin, temp, get_readable_time, get_time, generate_settings_text, log_error, clean_filename, get_random_mix_id
import time

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"
BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        stick_id = "CAACAgUAAxkBAAEQJmJpViid_0yscWKPfh3RMCY8pIkmXwACMAcAAqzbsFexyKU6FPQAAjgE"
        try:
            sticker = await message.reply_sticker(sticker=stick_id)
        except Exception as e:
            logger.exception("reply_sticker failed: %s", e)
        if EMOJI_MODE:
            try:
                await message.react(emoji=random.choice(REACTIONS), big=True)
            except Exception:
                await message.react(emoji="⚡️")
                pass
        m = message
        if len(m.command) == 2 and m.command[1].startswith(('notcopy', 'sendall')):
            _, userid, verify_id, file_id = m.command[1].split("_", 3)
            user_id = int(userid)
            grp_id = temp.VERIFICATIONS.get(user_id, 0)
            settings = await get_settings(grp_id)         
            verify_id_info = await db.get_verify_id_info(user_id, verify_id)
            if not verify_id_info or verify_id_info["verified"]:
                return await message.reply("<b>ʟɪɴᴋ ᴇxᴘɪʀᴇᴅ ᴛʀʏ ᴀɢᴀɪɴ...</b>")  

            ist_timezone = pytz.timezone('Asia/Kolkata')
            if await db.user_verified(user_id):
                key = "third_time_verified"
            else:
                key = "second_time_verified" if await db.is_user_verified(user_id) else "last_verified"
            current_time = datetime.now(tz=ist_timezone)
            result = await db.update_notcopy_user(user_id, {key:current_time})
            await db.update_verify_id_info(user_id, verify_id, {"verified":True})
            if key == "third_time_verified": 
                num = 3 
            else: 
                num =  2 if key == "second_time_verified" else 1 
            if key == "third_time_verified": 
                msg = script.THIRDT_VERIFY_COMPLETE_TEXT
            else:
                msg = script.SECOND_VERIFY_COMPLETE_TEXT if key == "second_time_verified" else script.VERIFY_COMPLETE_TEXT
            if message.command[1].startswith('sendall'):
                verifiedfiles = f"https://telegram.me/{temp.U_NAME}?start=allfiles_{grp_id}_{file_id}"
            else:
                verifiedfiles = f"https://telegram.me/{temp.U_NAME}?start=file_{grp_id}_{file_id}"
            await client.send_message(settings['log'], script.VERIFIED_LOG_TEXT.format(m.from_user.mention, user_id, datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %B %Y'), num))
            btn = [[
                InlineKeyboardButton("✅ ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ꜰɪʟᴇ ✅", url=verifiedfiles),
            ]]
            reply_markup=InlineKeyboardMarkup(btn)
            dlt=await m.reply_photo(
                photo=(VERIFY_IMG),
                caption=msg.format(message.from_user.mention, get_readable_time(TWO_VERIFY_GAP)),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await sticker.delete()
            await asyncio.sleep(300)
            await dlt.delete()
            return         
        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            buttons = [[
                        InlineKeyboardButton('❤️ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ❤️', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton('🍁 Update Channel 🍁', url=UPDATE_CHNL_LNK)
                      ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply(script.GSTART_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
            await sticker.delete()
            await asyncio.sleep(2) 
            if not await db.get_chat(message.chat.id):
                total=await client.get_chat_members_count(message.chat.id)
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
                await db.add_chat(message.chat.id, message.chat.title)
            return 
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
        if len(message.command) != 2:
            buttons = [[
                        InlineKeyboardButton('🔰 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ 🔰', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton(' ʜᴇʟᴘ 📢', callback_data='help'),
                        InlineKeyboardButton(' ᴀʙᴏᴜᴛ 📖', callback_data='about')
                    ],[
                        InlineKeyboardButton('ᴜᴘɢʀᴀᴅᴇ 🎟', callback_data="premium_info"),
                    ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            current_time = datetime.now(pytz.timezone(TIMEZONE))
            curr_time = current_time.hour        
            if curr_time < 12:
                gtxt = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 🌞" 
            elif curr_time < 17:
                gtxt = "ɢᴏᴏᴅ ᴀғᴛᴇʀɴᴏᴏɴ 🌓" 
            elif curr_time < 21:
                gtxt = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘"
            else:
                gtxt = "ɢᴏᴏᴅ ɴɪɢʜᴛ 🌑"
            try:      
                PIC = f"{random.choice(PICS_URL)}?r={get_random_mix_id()}"
            except Exception:
                PIC = random.choice(PICS)
            await message.reply_photo(
                photo=PIC,
                caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return

        if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
            buttons = [[
                        InlineKeyboardButton('🔰 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ 🔰', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton(' ʜᴇʟᴘ 📢', callback_data='help'),
                        InlineKeyboardButton(' ᴀʙᴏᴜᴛ 📖', callback_data='about')
                    ],[
                        InlineKeyboardButton('ᴜᴘɢʀᴀᴅᴇ 🎟', callback_data="premium_info"),
                    ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            current_time = datetime.now(pytz.timezone(TIMEZONE))
            curr_time = current_time.hour        
            if curr_time < 12:
                gtxt = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 🌞" 
            elif curr_time < 17:
                gtxt = "ɢᴏᴏᴅ ᴀғᴛᴇʀɴᴏᴏɴ 🌓" 
            elif curr_time < 21:
                gtxt = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘"
            else:
                gtxt = "ɢᴏᴏᴅ ɴɪɢʜᴛ 🌑"
            try:
                PIC = f"{random.choice(PICS_URL)}?r={get_random_mix_id()}"
            except Exception:
                PIC = random.choice(PICS)
            await message.reply_photo(
                photo=PIC,
                caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return
        if message.command[1].startswith("reff_"):
            try:
                user_id = int(message.command[1].split("_")[1])
            except ValueError:
                await message.reply_text("Invalid refer!")
                return
            if user_id == message.from_user.id:
                await message.reply_text("Hᴇʏ Dᴜᴅᴇ, Yᴏᴜ Cᴀɴ'ᴛ Rᴇғᴇʀ Yᴏᴜʀsᴇʟғ 🤣!\n\nsʜᴀʀᴇ ʟɪɴᴋ ʏᴏᴜʀ ғʀɪᴇɴᴅ ᴀɴᴅ ɢᴇᴛ 10 ʀᴇғᴇʀʀᴀʟ ᴘᴏɪɴᴛ ɪғ ʏᴏᴜ ᴀʀᴇ ᴄᴏʟʟᴇᴄᴛɪɴɢ 100 ʀᴇғᴇʀʀᴀʟ ᴘᴏɪɴᴛs ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ 1 ᴍᴏɴᴛʜ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀsʜɪᴘ.")
                return
            if referdb.is_user_in_list(message.from_user.id):
                await message.reply_text("Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀʟʀᴇᴀᴅʏ ɪɴᴠɪᴛᴇᴅ ❗")
                return
            if await db.is_user_exist(message.from_user.id): 
                await message.reply_text("‼️ Yᴏᴜ Hᴀᴠᴇ Bᴇᴇɴ Aʟʀᴇᴀᴅʏ Iɴᴠɪᴛᴇᴅ ᴏʀ Jᴏɪɴᴇᴅ")
                return 
            try:
                uss = await client.get_users(user_id)
            except Exception:
                return 	    
            referdb.add_user(message.from_user.id)
            fromuse = referdb.get_refer_points(user_id) + 10
            if fromuse == 100:
                referdb.add_refer_points(user_id, 0) 
                await message.reply_text(f"🎉 𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘂𝗹𝗮𝘁𝗶𝗼𝗻𝘀! 𝗬𝗼𝘂 𝘄𝗼𝗻 𝟭𝟬 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹 𝗽𝗼𝗶𝗻𝘁 𝗯𝗲𝗰𝗮𝘂𝘀𝗲 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗜𝗻𝘃𝗶𝘁𝗲𝗱 ☞ {uss.mention}!")		    
                await message.reply_text(user_id, f"You have been successfully invited by {message.from_user.mention}!") 	
                seconds = 2592000
                if seconds > 0:
                    expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                    user_data = {"id": user_id, "expiry_time": expiry_time}  # Using "id" instead of "user_id"  
                    await db.update_user(user_data)  # Use the update_user method to update or insert user data		    
                    await client.send_message(
                    chat_id=user_id,
                    text=f"<b>Hᴇʏ {uss.mention}\n\nYᴏᴜ ɢᴏᴛ 1 ᴍᴏɴᴛʜ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʙʏ ɪɴᴠɪᴛɪɴɢ 10 ᴜsᴇʀs ❗", disable_web_page_preview=True              
                    )
                for admin in ADMINS:
                    await client.send_message(chat_id=admin, text=f"Sᴜᴄᴄᴇss ғᴜʟʟʏ ᴛᴀsᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʙʏ ᴛʜɪs ᴜsᴇʀ:\n\nuser NᴀᴍE: {uss.mention}\n\nUsᴇʀ ɪᴅ: {uss.id}!")	
            else:
                referdb.add_refer_points(user_id, fromuse)
                await message.reply_text(f"You have been successfully invited by {uss.mention}!")
                await client.send_message(user_id, f"𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘂𝗹𝗮𝘁𝗶𝗼𝗻𝘀! 𝗬𝗼𝘂 𝘄𝗼𝗻 𝟭𝟬 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹 𝗽𝗼𝗶𝗻𝘁 𝗯𝗲𝗰𝗮𝘂𝘀𝗲 𝗬𝗼ᴜ 𝗵𝗮ᴠᴇ 𝗯ᴇ𝗲𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗜𝗻𝘃𝗶𝘁𝗲𝗱 ☞{message.from_user.mention}!")
            return

        if len(message.command) == 2 and message.command[1] in ["premium"]:
            buttons = [[
                        InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ', url=OWNER_LNK)
                      ],[
                        InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
                      ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_photo(
                photo=(SUBSCRIPTION),
                caption=script.PREPLANS_TXT.format(message.from_user.mention, OWNER_UPI_ID, QR_CODE),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return  

        if len(message.command) == 2 and message.command[1].startswith('getfile'):
            movies = message.command[1].split("-", 1)[1] 
            movie = movies.replace('-',' ')
            message.text = movie 
            await auto_filter(client, message) 
            return

        data = message.command[1]
        try:
            _, grp_id, file_id = data.split("_", 2)
            grp_id = int(grp_id)
        except:
            grp_id = 0
            file_id = data

        # Fetch file details concurrently with user checks
        file_details_task = asyncio.create_task(get_file_details(file_id))

        if not await db.has_premium_access(message.from_user.id): 
            try:
                btn = []
                chat = grp_id
                settings      = await get_settings(chat)
                fsub_channels = list(dict.fromkeys((settings.get('fsub', []) if settings else [])+ AUTH_CHANNELS)) 

                if fsub_channels:
                    btn += await is_subscribed(client, message.from_user.id, fsub_channels)
                if AUTH_REQ_CHANNELS:
                    btn += await is_req_subscribed(client, message.from_user.id, AUTH_REQ_CHANNELS)
                if btn:
                    if len(message.command) > 1 and "_" in message.command[1]:
                        kk, file_id = message.command[1].split("_", 1)
                        btn.append([
                            InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", callback_data=f"checksub#{kk}#{file_id}")
                        ])
                        reply_markup = InlineKeyboardMarkup(btn)
                    photo = random.choice(FSUB_PICS) if FSUB_PICS else "https://graph.org/file/7478ff3eac37f4329c3d8.jpg"
                    caption = (
                        f"👋 ʜᴇʟʟᴏ {message.from_user.mention}\n\n"
                        "🛑 ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.\n"
                        "👉 ᴊᴏɪɴ ᴀʟʟ ᴛʜᴇ ʙᴇʟᴏᴡ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
                    )
                    await message.reply_photo(
                        photo=photo,
                        caption=caption,
                        reply_markup=reply_markup,
                        parse_mode=enums.ParseMode.HTML
                    )
                    return

            except Exception as e:
                await log_error(client, f"❗️ Force Sub Error:\n\n{repr(e)}")
                logger.error(f"❗️ Force Sub Error:\n\n{repr(e)}")


        user_id = m.from_user.id
        if not await db.has_premium_access(user_id):
            try:
                grp_id = int(grp_id)
                user_verified = await db.is_user_verified(user_id)
                settings = await get_settings(grp_id)
                is_second_shortener = await db.use_second_shortener(user_id, settings.get('verify_time', TWO_VERIFY_GAP)) 
                is_third_shortener = await db.use_third_shortener(user_id, settings.get('third_verify_time', THREE_VERIFY_GAP))
                if settings.get("is_verify", IS_VERIFY) and (not user_verified or is_second_shortener or is_third_shortener):
                    verify_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
                    await db.create_verify_id(user_id, verify_id)
                    temp.VERIFICATIONS[user_id] = grp_id
                    if message.command[1].startswith('allfiles'):
                        verify = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=sendall_{user_id}_{verify_id}_{file_id}", grp_id, is_second_shortener, is_third_shortener)
                    else:
                        verify = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=notcopy_{user_id}_{verify_id}_{file_id}", grp_id, is_second_shortener, is_third_shortener)
                    if is_third_shortener:
                        howtodownload = settings.get('tutorial_3', TUTORIAL_3)
                    else:
                        howtodownload = settings.get('tutorial_2', TUTORIAL_2) if is_second_shortener else settings.get('tutorial', TUTORIAL)
                    buttons = [[
                        InlineKeyboardButton(text="♻️ ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴠᴇʀɪꜰʏ ♻️", url=verify)
                    ],[
                        InlineKeyboardButton(text="⁉️ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪꜰʏ ⁉️", url=howtodownload)
                    ]]
                    reply_markup=InlineKeyboardMarkup(buttons)
                    if await db.user_verified(user_id): 
                        msg = script.THIRDT_VERIFICATION_TEXT
                    else:            
                        msg = script.SECOND_VERIFICATION_TEXT if is_second_shortener else script.VERIFICATION_TEXT
                    n=await m.reply_text(
                        text=msg.format(message.from_user.mention),
                        protect_content = True,
                        reply_markup=reply_markup,
                        parse_mode=enums.ParseMode.HTML
                    )
                    await sticker.delete()
                    await asyncio.sleep(300) 
                    await n.delete()
                    await m.delete()
                    return
            except Exception as e:
                print(f"Error In Verification - {e}")
                pass

        # Now, await the file details task
        files_ = await file_details_task

        if data.startswith("allfiles"):
            try:
                files = temp.GETALL.get(file_id)
                if not files:
                    return await message.reply('<b><i>ɴᴏ ꜱᴜᴄʜ ꜰɪʟᴇ ᴇxɪꜱᴛꜱ !</b></i>')
                filesarr = []
                cover = None
                for file in files:
                    file_id = file.file_id
                    files_ = await get_file_details(file_id)
                    files1 = files_[0]
                    title = clean_filename(files1.file_name)
                    cover = files1.cover
                    size = get_size(files1.file_size)
                    f_caption = files1.caption
                    settings = await get_settings(int(grp_id))
                    DREAMX_CAPTION = settings.get('caption', CUSTOM_FILE_CAPTION)
                    if DREAMX_CAPTION:
                        try:
                            f_caption=DREAMX_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                        except Exception as e:
                            logger.exception(e)
                            f_caption = f_caption
                    if f_caption is None:
                        f_caption = f"{clean_filename(files1.file_name)}"
                    btn = await stream_buttons(message.from_user.id, file_id)
                    msg = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        cover=cover,
                        file_id=file_id,
                        caption=f_caption,
                        protect_content=settings.get('file_secure', PROTECT_CONTENT),
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    filesarr.append(msg)
                k = await client.send_message(chat_id=message.from_user.id, text=script.DEL_MSG.format(get_time(DELETE_TIME)), parse_mode=enums.ParseMode.HTML)
                await sticker.delete()
                await asyncio.sleep(DELETE_TIME)
                for x in filesarr:
                    await x.delete()
                await k.edit_text("<b>ʏᴏᴜʀ ᴀʟʟ ᴠɪᴅᴇᴏꜱ/ꜰɪʟᴇꜱ ᴀʀᴇ ᴅᴇʟᴇᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ !\nᴋɪɴᴅʟʏ ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ</b>")
                return
            except Exception as e:
                logger.exception(e)
                return

        user = message.from_user.id
        settings = await get_settings(int(grp_id))
        if not files_:
            raw = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
            sep = raw.find(b"_")
            if sep == -1:
                raise ValueError("Invalid encoded data")
            pre = raw[:sep].decode("ascii")
            file_id = raw[sep + 1:].decode("latin1")
        # if not files_:
        #     pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("utf-8")).split("_", 1)
            try:
                cover = None
                if COVERX:
                    details= await get_file_details(file_id)
                    cover = details.get('cover', None)
                btn = await stream_buttons(message.from_user.id, file_id)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    cover=cover,
                    file_id=file_id,
                    protect_content=settings.get('file_secure', PROTECT_CONTENT),
                    reply_markup=InlineKeyboardMarkup(btn))

                filetype = msg.media
                file = getattr(msg, filetype.value)
                title = clean_filename(file.file_name)
                size=get_size(file.file_size)
                f_caption = f"<code>{title}</code>"
                settings = await get_settings(int(grp_id))
                DREAMX_CAPTION = settings.get('caption', CUSTOM_FILE_CAPTION)
                if DREAMX_CAPTION:
                    try:
                        f_caption=DREAMX_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                    except:
                        return
                await msg.edit_caption(
                    f_caption,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                k = await msg.reply(script.DEL_MSG.format(get_time(DELETE_TIME)),
                    quote=True, parse_mode=enums.ParseMode.HTML
                )
                await sticker.delete()
                await asyncio.sleep(DELETE_TIME)
                await msg.delete()
                await k.edit_text("<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!</b>")
                return
            except Exception as e:
                logger.exception(e)
                pass
            return await message.reply('ɴᴏ ꜱᴜᴄʜ ꜰɪʟᴇ ᴇxɪꜱᴛꜱ !')

        files = files_[0]
        title = clean_filename(files.file_name)
        size = get_size(files.file_size)
        cover = files.cover if files.cover else None
        f_caption = files.caption
        settings = await get_settings(int(grp_id))            
        DREAMX_CAPTION = settings.get('caption', CUSTOM_FILE_CAPTION)
        if DREAMX_CAPTION:
            try:
                f_caption=DREAMX_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption

        if f_caption is None:
            f_caption = clean_filename(files.file_name)
        btn = await stream_buttons(message.from_user.id, file_id)
        msg = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            cover=cover,
            caption=f_caption,
            protect_content=settings.get('file_secure', PROTECT_CONTENT),
            reply_markup=InlineKeyboardMarkup(btn)
        )
        
        k = await msg.reply(script.DEL_MSG.format(get_time(DELETE_TIME)),
            quote=True, parse_mode=enums.ParseMode.HTML
        )
        await sticker.delete()
        await asyncio.sleep(DELETE_TIME)
        await msg.delete()
        await k.edit_text("<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!</b>")
        return
    except Exception as e:
        logger.exception(f"Error In /start command - {e}")
        pass
    finally:
        if sticker:
            try:
                await sticker.delete()
            except Exception as e:
                logger.exception(f"Error In Deleting Sticker - {e}")
                pass

async def stream_buttons(user_id: int, file_id: str):
    if STREAM_MODE and not PREMIUM_STREAM_MODE:
        return [
            [InlineKeyboardButton('🚀 ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ / ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ 🖥️', callback_data=f'generate_stream_link:{file_id}')],
            [InlineKeyboardButton('ℹ️ ᴠɪᴇᴡ ᴀᴜᴅɪᴏ & ꜱᴜʙꜱ ɪɴꜰᴏ ℹ️', callback_data=f'extract_data:{file_id}')],
            [InlineKeyboardButton('📌 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ 📌', url=UPDATE_CHNL_LNK)]
        ]
    elif STREAM_MODE and PREMIUM_STREAM_MODE:
        if not await db.has_premium_access(user_id):
            return [
                [InlineKeyboardButton('🚀 ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ / ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ 🖥️', callback_data='prestream')],
                [InlineKeyboardButton('ℹ️ ᴠɪᴇᴡ ᴀᴜᴅɪᴏ & ꜱᴜʙꜱ ɪɴꜰᴏ ℹ️', callback_data='prestream')],
                [InlineKeyboardButton('📌 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ 📌', url=UPDATE_CHNL_LNK)]
            ]
        else:
            return [
                [InlineKeyboardButton('🚀 ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ / ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ 🖥️', callback_data=f'generate_stream_link:{file_id}')],
                [InlineKeyboardButton('ℹ️ ᴠɪᴇᴡ ᴀᴜᴅɪᴏ & ꜱᴜʙꜱ ɪɴꜰᴏ ℹ️', callback_data=f'extract_data:{file_id}')],
                [InlineKeyboardButton('📌 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ 📌', url=UPDATE_CHNL_LNK)]
            ]
    else:
        return [[InlineKeyboardButton('📌 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ 📌', url=UPDATE_CHNL_LNK)]]
    
@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('DreamXlogs.txt', caption="📑 **ʟᴏɢꜱ**")
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('save') & filters.user(ADMINS))
async def save_file_handler(bot, message):
    """Save file to database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Pʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Rᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ /save ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴀᴠᴇ', quote=True)
        return

    try:
        for file_type in ("document", "video", "audio"):
            media = getattr(reply, file_type, None)
            if media is not None:
                break
        else:
            await msg.edit('Tʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ')
            return
        
        file_id, file_ref = unpack_new_file_id(media.file_id)
        media.file_type = file_type
        media.caption = reply.caption
        success, status = await save_file(media)
        if success:
            await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ sᴀᴠᴇᴅ ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇ ✅')
        elif status == 0:
            await msg.edit('Fɪʟᴇ ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛs ɪɴ ᴅᴀᴛᴀʙᴀsᴇ ⚠️')
        elif status == 2:
            await msg.edit('Eʀʀᴏʀ: Fɪʟᴇ ᴠᴀʟɪᴅᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ ❌')
        else:
            await msg.edit('Eʀʀᴏʀ: Fᴀɪʟᴇᴅ ᴛᴏ sᴀᴠᴇ ғɪʟᴇ ❌')
    except Exception as e:
        logger.exception(e)
        await msg.edit(f'Aɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e} ❌')


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Pʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Rᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ /delete ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Tʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)
    if await Media.count_documents({'file_id': file_id}):
        result = await Media.collection.delete_one({
            '_id': file_id,
        })
    else:
        result = await Media2.collection.delete_one({
            '_id': file_id,
        })
    if result.deleted_count:
        await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ ✅')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ ✅')
        else:
            result = await Media2.collection.delete_many({
                'file_name': file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
            else:
                result = await Media.collection.delete_many({
                    'file_name': media.file_name,
                    'file_size': media.file_size,
                    'mime_type': media.mime_type
                })
                if result.deleted_count:
                    await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ ✅')
                else:
                    result = await Media2.collection.delete_many({
                        'file_name': media.file_name,
                        'file_size': media.file_size,
                        'mime_type': media.mime_type
                    })
                    if result.deleted_count:
                        await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ ✅')
                    else:
                        await msg.edit('Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ ❌')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'ᴛʜɪꜱ ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ʏᴏᴜʀ ɪɴᴅᴇxᴇᴅ ꜰɪʟᴇꜱ !\nᴅᴏ ʏᴏᴜ ꜱᴛɪʟʟ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⚠️ ʏᴇꜱ ⚠️", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ ɴᴏ ❌", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )

@Client.on_message(filters.command('settings'))
async def settings(client, message):
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ.")
    chat_type = message.chat.type
    if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        if not await is_check_admin(client, grp_id, message.from_user.id):
            return await message.reply_text(script.NT_ADMIN_ALRT_TXT)
        await db.connect_group(grp_id, user_id)
        btn = [[
                InlineKeyboardButton("👤 ᴏᴘᴇɴ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ 👤", callback_data=f"opnsetpm#{grp_id}")
              ],[
                InlineKeyboardButton("👥 ᴏᴘᴇɴ ʜᴇʀᴇ 👥", callback_data=f"opnsetgrp#{grp_id}")
              ]]
        await message.reply_text(
                text="<b>ᴡʜᴇʀᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ ꜱᴇᴛᴛɪɴɢꜱ ᴍᴇɴᴜ ? ⚙️</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
        )
    elif chat_type == enums.ChatType.PRIVATE:
        connected_groups = await db.get_connected_grps(user_id)
        if not connected_groups:
            return await message.reply_text("Nᴏ Cᴏɴɴᴇᴄᴛᴇᴅ Gʀᴏᴜᴘs Fᴏᴜɴᴅ .")
        group_list = []
        for group in connected_groups:
            try:
                Chat = await client.get_chat(group)
                group_list.append([ InlineKeyboardButton(text=Chat.title, callback_data=f"grp_pm#{Chat.id}") ])
            except Exception as e:
                print(f"Error In PM Settings Button - {e}")
                pass
        await message.reply_text(
                    "⚠️ ꜱᴇʟᴇᴄᴛ ᴛʜᴇ ɢʀᴏᴜᴘ ᴡʜᴏꜱᴇ ꜱᴇᴛᴛɪɴɢꜱ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ.\n\n"
                    "ɪꜰ ʏᴏᴜʀ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ꜱʜᴏᴡɪɴɢ ʜᴇʀᴇ,\n"
                    "ᴜꜱᴇ /reload ɪɴ ᴛʜᴀᴛ ɢʀᴏᴜᴘ ᴀɴᴅ ɪᴛ ᴡɪʟʟ ᴀᴘᴘᴇᴀʀ ʜᴇʀᴇ.",
                    reply_markup=InlineKeyboardMarkup(group_list)
                )

@Client.on_message(filters.command('reload'))
async def connect_group(client, message):
    user_id = message.from_user.id
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await db.connect_group(message.chat.id, user_id)
        await message.reply_text("Gʀᴏᴜᴘ Rᴇʟᴏᴀᴅᴇᴅ ✅ Nᴏᴡ Yᴏᴜ Cᴀɴ Mᴀɴᴀɢᴇ Tʜɪs Gʀᴏᴜᴘ Fʀᴏᴍ PM.")
    elif message.chat.type == enums.ChatType.PRIVATE:
        if len(message.command) < 2:
            await message.reply_text("Example: /reload 123456789")
            return
        try:
            group_id = int(message.command[1])
            if not await is_check_admin(client, group_id, user_id):
                await message.reply_text(script.NT_ADMIN_ALRT_TXT)
                return
            chat = await client.get_chat(group_id)
            await db.connect_group(group_id, user_id)
            await message.reply_text(f"Lɪɴᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅ {chat.title} ᴛᴏ PM.")
        except:
            await message.reply_text("Invalid group ID or error occurred.")

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("ᴄʜᴇᴄᴋɪɴɢ ᴛᴇᴍᴘʟᴀᴛᴇ...")
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply("ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ.")

    if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await sts.edit("⚠️ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ.")

    group_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, group_id, user_id):
        await message.reply_text(script.NT_ADMIN_ALRT_TXT)
        return

    if len(message.command) < 2:
        return await sts.edit("⚠️ ɴᴏ ᴛᴇᴍᴘʟᴀᴛᴇ ᴘʀᴏᴠɪᴅᴇᴅ!")

    template = message.text.split(" ", 1)[1]
    await save_group_settings(group_id, 'template', template)
    await sts.edit(
        f"✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ ᴛᴇᴍᴘʟᴀᴛᴇ ꜰᴏʀ <code>{title}</code> ᴛᴏ:\n\n{template}"
    )

# Must add REQST_CHANNEL and SUPPORT_CHAT_ID to use this feature
@Client.on_message((filters.command(["request", "Request"]) | filters.regex("#request") | filters.regex("#Request")) & filters.group)
async def requests(bot, message):
    if REQST_CHANNEL is None or SUPPORT_CHAT_ID is None:
        return
    if message.reply_to_message and SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.reply_to_message.text
        try:
            if REQST_CHANNEL is not None:
                btn = [[
                    InlineKeyboardButton('ᴠɪᴇᴡ ʀᴇǫᴜᴇꜱᴛ', url=f"{message.reply_to_message.link}"),
                    InlineKeyboardButton('ꜱʜᴏᴡ ᴏᴘᴛɪᴏɴꜱ', callback_data=f'show_option#{reporter}')
                ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>📝 ʀᴇǫᴜᴇꜱᴛ : <u>{content}</u>\n\n📚 ʀᴇᴘᴏʀᴛᴇᴅ ʙʏ : {mention}\n📖 ʀᴇᴘᴏʀᴛᴇʀ ɪᴅ : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('ᴠɪᴇᴡ ʀᴇǫᴜᴇꜱᴛ', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('ꜱʜᴏᴡ ᴏᴘᴛɪᴏɴꜱ', callback_data=f'show_option#{reporter}')
                    ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>📝 ʀᴇǫᴜᴇꜱᴛ : <u>{content}</u>\n\n📚 ʀᴇᴘᴏʀᴛᴇᴅ ʙʏ : {mention}\n📖 ʀᴇᴘᴏʀᴛᴇʀ ɪᴅ : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>ʏᴏᴜ ᴍᴜꜱᴛ ᴛʏᴘᴇ ᴀʙᴏᴜᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ [ᴍɪɴɪᴍᴜᴍ 3 ᴄʜᴀʀᴀᴄᴛᴇʀꜱ]. ʀᴇǫᴜᴇꜱᴛꜱ ᴄᴀɴ'ᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b>")
                if len(content) < 3:
                    success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass
        
    elif SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.text
        keywords = ["#request", "/request", "#Request", "/Request"]
        for keyword in keywords:
            if keyword in content:
                content = content.replace(keyword, "")
        try:
            if REQST_CHANNEL is not None and len(content) >= 3:
                btn = [[
                    InlineKeyboardButton('ᴠɪᴇᴡ ʀᴇǫᴜᴇꜱᴛ', url=f"{message.link}"),
                    InlineKeyboardButton('ꜱʜᴏᴡ ᴏᴘᴛɪᴏɴꜱ', callback_data=f'show_option#{reporter}')
                ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>📝 ʀᴇǫᴜᴇꜱᴛ : <u>{content}</u>\n\n📚 ʀᴇᴘᴏʀᴛᴇᴅ ʙʏ : {mention}\n📖 ʀᴇᴘᴏʀᴛᴇʀ ɪᴅ : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('ᴠɪᴇᴡ ʀᴇǫᴜᴇꜱᴛ', url=f"{message.link}"),
                        InlineKeyboardButton('ꜱʜᴏᴡ ᴏᴘᴛɪᴏɴꜱ', callback_data=f'show_option#{reporter}')
                    ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>📝 ʀᴇǫᴜᴇꜱᴛ : <u>{content}</u>\n\n📚 ʀᴇᴘᴏʀᴛᴇᴅ ʙʏ : {mention}\n📖 ʀᴇᴘᴏʀᴛᴇʀ ɪᴅ : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>ʏᴏᴜ ᴍᴜꜱᴛ ᴛʏᴘᴇ ᴀʙᴏᴜᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ [ᴍɪɴɪᴍᴜᴍ 3 ᴄʜᴀʀᴀᴄᴛᴇʀꜱ]. ʀᴇǫᴜᴇꜱᴛꜱ ᴄᴀɴ'ᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b>")
                if len(content) < 3:
                    success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass

    if success:
        await message.reply_text(f"<b>ʜᴇʏ {mention}, ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ʜᴀꜱ ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ǫᴜᴇᴜᴇ. ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ sᴏᴍᴇ ᴛɪᴍᴇ ᴜɴᴛɪʟ ɪᴛ ɪs ᴘʀᴏᴄᴇssᴇᴅ.</b>")

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(client, message):
    msg = await message.reply('**Cʜᴇᴄᴋɪɴɢ Sᴛᴀᴛs...**')
    files = await Media.count_documents()
    files2 = await Media2.count_documents()
    users = await db.total_users_count()
    chats = await db.total_chat_count()
    total_files = files + files2
    await msg.edit(f'**Bᴏᴛ Sᴛᴀᴛs:**\n\n'
                   f'**Tᴏᴛᴀʟ Fɪʟᴇs:** {total_files}\n'
                   f'**Tᴏᴛᴀʟ Usᴇʀs:** {users}\n'
                   f'**Tᴏᴛᴀʟ Cʜᴀᴛs:** {chats}')

@Client.on_message(filters.command("clean_groups") & filters.user(ADMINS))
async def clean_groups(client, message):
    msg = await message.reply('**Cʟᴇᴀɴɪɴɢ Gʀᴏᴜᴘs...**')
    total_groups = await db.total_chat_count()
    processed = 0
    deleted_count = 0
    batch_size = 100
    chats = await db.get_all_chats()
    async for chat in chats:
        try:
            processed += 1
            chat_id = chat['id']
            try:
                await client.get_chat_member(chat_id, client.me.id)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await client.get_chat_member(chat_id, client.me.id)
                except (UserNotParticipant, PeerIdInvalid, ChannelInvalid):
                    await db.delete_chat(chat_id)
                    deleted_count += 1
                except Exception:
                    pass
            except (UserNotParticipant, PeerIdInvalid, ChannelInvalid):
                await db.delete_chat(chat_id)
                deleted_count += 1
            except Exception as e:
                print(f'Error checking chat {chat_id}: {e}')
                pass
            if processed % batch_size == 0:
                try:
                    await msg.edit(f'Progress: {processed}/{total_groups}\nDeleted: {deleted_count}')
                    await asyncio.sleep(2)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await msg.edit(f'Progress: {processed}/{total_groups}\nDeleted: {deleted_count}')
        except Exception as e:
            print(f'Error in clean_groups loop: {e}')
    await msg.edit(f'**Clean Groups Complete**\n\nTotal Processed: {processed}\nDeleted: {deleted_count}')
