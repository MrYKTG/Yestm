import os
from plugins.Extraxeon.fotnt_string import Fonts
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Client.on_message(filters.private & filters.command(["font"]))
async def style_buttons(c, m, cb=False):
    buttons = [[
        InlineKeyboardButton('𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data='style+typewriter'),
        InlineKeyboardButton('𝕆𝕦𝕥𝕝𝕚𝕟𝕖', callback_data='style+outline'),
        InlineKeyboardButton('𝐒𝐞𝐫𝐢𝐟', callback_data='style+serif'),
        ],[
        InlineKeyboardButton('𝑺𝒆𝒓𝒊𝒇', callback_data='style+bold_cool'),
        InlineKeyboardButton('𝑆𝑒𝑟𝑖𝑓', callback_data='style+cool'),
        InlineKeyboardButton('Sᴍᴀʟʟ Cᴀᴘs', callback_data='style+small_cap'),
        ],[
        InlineKeyboardButton('𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉', callback_data='style+bold_typewriter'),
        InlineKeyboardButton('𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭', callback_data='style+bold_sans'),
        InlineKeyboardButton('𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙', callback_data='style+bold_serif'),
        ],[
        InlineKeyboardButton('ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ', callback_data='style+extended_smallcap'),
        InlineKeyboardButton('𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍', callback_data='style+italic_cool'),
        InlineKeyboardButton('𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁', callback_data='style+bold_italic_cool'),
        ],[
        InlineKeyboardButton('⺓ᏴᏟᎠΞҒᏀᎻ ᎫᏦᏞᎷƝᎧᎮⵕᎡꕶᎢᏌᏙᎳXᎽᏃ', callback_data='style+comic_extended'),
        InlineKeyboardButton('Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎', callback_data='style+circles'),
        InlineKeyboardButton('🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎', callback_data='style+circle_dark'),
        ],[
        InlineKeyboardButton('𝔊𝔬𝔱𝔥𝔦𝔠', callback_data='style+gothic'),
        InlineKeyboardButton('🇸 🇵 🇪 🇨 🇮 🇦 🇱 ', callback_data='style+special'),
        InlineKeyboardButton('🅂🅀🅄🄰🅁🄴🅂', callback_data='style+squares'),
        ],[
        InlineKeyboardButton('🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎', callback_data='style+squares_bold'),
        InlineKeyboardButton('Next ➡️', callback_data="nxt")
    ]]
    if not cb:
        if ' ' in m.text:
            title = m.text.split(" ", 1)[1]
            await m.reply_text(title, reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=m.id)                     
        else:
            await m.reply_text(text="Ente Any Text Eg:- `/font [text]`")    
    else:
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex('^nxt'))
async def nxt(c, m):
    if m.data == "nxt":
        buttons = [[
            InlineKeyboardButton('⬅️ Back', callback_data='nxt+0')
        ]]
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    else:
        await style_buttons(c, m, cb=True)


@Client.on_callback_query(filters.regex('^style'))
async def style(c, m):
    await m.answer()
    cmd, style = m.data.split('+')

    if style == 'typewriter':
        cls = Fonts.typewriter
    elif style == 'outline':
        cls = Fonts.outline
    elif style == 'serif':
        cls = Fonts.serief
    elif style == 'bold_cool':
        cls = Fonts.bold_cool
    elif style == 'cool':
        cls = Fonts.cool
    elif style == 'small_cap':
        cls = Fonts.smallcap
    elif style == 'script':
        cls = Fonts.script
    elif style == 'script_bolt':
        cls = Fonts.bold_script
    elif style == 'tiny':
        cls = Fonts.tiny
    elif style == 'comic':
        cls = Fonts.comic
    elif style == 'sans':
        cls = Fonts.san
    elif style == 'slant_sans':
        cls = Fonts.slant_san
    elif style == 'slant':
        cls = Fonts.slant
    elif style == 'sim':
        cls = Fonts.sim
    elif style == 'circles':
        cls = Fonts.circles
    elif style == 'circle_dark':
        cls = Fonts.dark_circle
    elif style == 'gothic':
        cls = Fonts.gothic
    elif style == 'gothic_bolt':
        cls = Fonts.bold_gothic
    elif style == 'cloud':
        cls = Fonts.cloud
    elif style == 'happy':
        cls = Fonts.happy
    elif style == 'sad':
        cls = Fonts.sad
    elif style == 'special':
        cls = Fonts.special
    elif style == 'squares':
        cls = Fonts.square
    elif style == 'squares_bold':
        cls = Fonts.dark_square
    elif style == 'andalucia':
        cls = Fonts.andalucia
    elif style == 'manga':
        cls = Fonts.manga
    elif style == 'stinky':
        cls = Fonts.stinky
    elif style == 'bubbles':
        cls = Fonts.bubbles
    elif style == 'underline':
        cls = Fonts.underline
    elif style == 'ladybug':
        cls = Fonts.ladybug
    elif style == 'rays':
        cls = Fonts.rays
    elif style == 'birds':
        cls = Fonts.birds
    elif style == 'slash':
        cls = Fonts.slash
    elif style == 'stop':
        cls = Fonts.stop
    elif style == 'skyline':
        cls = Fonts.skyline
    elif style == 'arrows':
        cls = Fonts.arrows
    elif style == 'qvnes':
        cls = Fonts.rvnes
    elif style == 'strike':
        cls = Fonts.strike
    elif style == 'frozen':
        cls = Fonts.frozen
    # NEW STYLES ADDED HERE
    elif style == 'bold_typewriter':
        cls = Fonts.bold_typewriter
    elif style == 'bold_sans':
        cls = Fonts.bold_sans
    elif style == 'bold_serif':
        cls = Fonts.bold_serif
    elif style == 'extended_smallcap':
        cls = Fonts.extended_smallcap
    elif style == 'italic_cool':
        cls = Fonts.italic_cool
    elif style == 'bold_italic_cool':
        cls = Fonts.bold_italic_cool
    elif style == 'comic_extended':
        cls = Fonts.comic_extended

    r, oldtxt = m.message.reply_to_message.text.split(None, 1) 
    new_text = cls(oldtxt)            
    try:
        await m.message.edit_text(f"`{new_text}`\n\n👆 Click To Copy", reply_markup=m.message.reply_markup)
    except Exception as e:
        print(e)
