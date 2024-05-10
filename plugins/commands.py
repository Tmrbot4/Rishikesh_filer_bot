import os
import logging
import random, string
import asyncio
import time
import datetime
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait, ButtonDataInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, delete_files
from database.users_chats_db import db
from info import STICKERS_IDS,SUPPORT_GROUP ,INDEX_CHANNELS, ADMINS, IS_VERIFY, VERIFY_TUTORIAL, VERIFY_EXPIRE, TUTORIAL, SHORTLINK_API, SHORTLINK_URL, AUTH_CHANNEL, DELETE_TIME, SUPPORT_LINK, UPDATES_LINK, LOG_CHANNEL, PICS, PROTECT_CONTENT, IS_STREAM, IS_FSUB, PAYMENT_QR
from utils import get_settings, get_size, is_subscribed, is_check_admin, get_shortlink, get_verify_status, update_verify_status, save_group_settings, temp, get_readable_time, get_wish, get_seconds
import requests
from telegraph import upload_file

@Client.on_message(filters.command("ask") & filters.incoming) #add your support grp
async def aiRes(_, message):
    if message.chat.id == SUPPORT_GROUP:
        asked = message.text.split(None, 1)[1]
        if not asked:
            return await message.reply("Bhai kuch puch to le /ask k baad !")
        thinkStc = await message.reply_sticker(sticker=random.choice(STICKERS_IDS))
        url = f"https://bisal-ai-api.vercel.app/biisal" 
        res = requests.post(url , data={'query' : asked})
        if res.status_code == 200:
            response = res.json().get("response")
            await thinkStc.delete()
            await message.reply(f"<b>hey {message.from_user.mention()},\n{response.lstrip() if response.startswith(' ') else response}</b>")
        else:
            await thinkStc.delete()
            await message.reply("Mausam kharab hai ! Thode der mein try kre !\nor Report to Developer.")
    else:
        btn = [[
            InlineKeyboardButton('ðŸ’¡ Support Group ðŸ’¡', url=SUPPORT_LINK)
        ]]
        await message.reply(f"<b>hey {message.from_user.mention},\n\nPlease use this command in support group.</b>", reply_markup=InlineKeyboardMarkup(btn))
        
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    botid = client.me.id
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            username = f'@{message.chat.username}' if message.chat.username else 'Private'
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total))       
            await db.add_chat(message.chat.id, message.chat.title)
        wish = get_wish()
        btn = [[
            InlineKeyboardButton('âš¡ï¸ á´œá´˜á´…á´€á´›á´‡s á´„Êœá´€É´É´á´‡ÊŸ âš¡ï¸', url=UPDATES_LINK),
            InlineKeyboardButton('ðŸ’¡ Support Group ðŸ’¡', url=SUPPORT_LINK)
        ]]
        await message.reply(text=f"<b>Êœá´‡Ê {message.from_user.mention}, <i>{wish}</i>\nÊœá´á´¡ á´„á´€É´ Éª Êœá´‡ÊŸá´˜ Êá´á´œ??</b>", reply_markup=InlineKeyboardMarkup(btn))
        return 
        
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(message.from_user.mention, message.from_user.id))

    verify_status = await get_verify_status(message.from_user.id)
    if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
        await update_verify_status(message.from_user.id, is_verified=False)
    
    if (len(message.command) != 2) or (len(message.command) == 2 and message.command[1] == 'start'):
        buttons = [[
            InlineKeyboardButton('â¤¬ Aá´…á´… Má´‡ Tá´ Yá´á´œÊ€ GÊ€á´á´œá´˜ â¤¬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('ðŸŒ¿ êœ±á´œá´˜á´˜á´Ê€á´›', callback_data="my_about"),
                    InlineKeyboardButton('ðŸ‘¤ á´á´¡É´á´‡Ê€', callback_data='my_owner')
                ],[
                    InlineKeyboardButton('ðŸ Ò“á´‡á´€á´›á´œÊ€á´‡s', callback_data='help'),
                    InlineKeyboardButton('ðŸ” á´˜Ê€á´‡á´Éªá´œá´', callback_data='buy_premium')
                ],[
                    InlineKeyboardButton('ðŸ’° á´‡á´€Ê€É´ á´á´É´á´‡Ê Ê™Ê Ê™á´á´› ðŸ’°', callback_data='earn')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, get_wish()),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return


    mc = message.command[1]

    if mc.startswith('verify'):
        _, token = mc.split("_", 1)
        verify_status = await get_verify_status(message.from_user.id)
        if verify_status['verify_token'] != token:
            return await message.reply("Your verify token is invalid.")
        await update_verify_status(message.from_user.id, is_verified=True, verified_time=time.time())
        if verify_status["link"] == "":
            reply_markup = None
        else:
            btn = [[
                InlineKeyboardButton("ðŸ“Œ Get File ðŸ“Œ", url=f'https://t.me/{temp.U_NAME}?start={verify_status["link"]}')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
        await message.reply(f"âœ… You successfully verified until: {get_readable_time(VERIFY_EXPIRE)}", reply_markup=reply_markup, protect_content=True)
        return
    
    verify_status = await get_verify_status(message.from_user.id)
    if not await db.has_premium_access(message.from_user.id):
        if IS_VERIFY and not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(message.from_user.id, verify_token=token, link="" if mc == 'inline_verify' else mc)
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/{temp.U_NAME}?start=verify_{token}')
            btn = [[
                InlineKeyboardButton("ðŸ§¿ Verify ðŸ§¿", url=link)
            ],[
                InlineKeyboardButton('ðŸ—³ Tutorial ðŸ—³', url=VERIFY_TUTORIAL)
            ]]
            await message.reply("You not verified today! Kindly verify now. ðŸ”", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return
    else:
        pass

    settings = await get_settings(int(mc.split("_", 2)[1]))
    if settings.get('is_fsub', IS_FSUB):
        btn = await is_subscribed(client, message, settings['fsub'])
        if btn:
            btn.append(
                [InlineKeyboardButton("ðŸ” Try Again ðŸ”", callback_data=f"checksub#{mc}")]
            )
            reply_markup = InlineKeyboardMarkup(btn)
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=f"ðŸ‘‹ Hello {message.from_user.mention},\n\nPlease join my 'Updates Channel' and try again. ðŸ˜‡",
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return 
        
    if mc.startswith('all'):
        _, grp_id, key = mc.split("_", 2)
        files = temp.FILES.get(key)
        if not files:
            return await message.reply('No Such All Files Exist!')
        settings = await get_settings(int(grp_id))
        for file in files:
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name = file.file_name,
                file_size = get_size(file.file_size),
                file_caption=file.caption
            )   
            if settings.get('is_stream', IS_STREAM):
                btn = [[
                    InlineKeyboardButton("âœ› á´¡á´€á´›á´„Êœ & á´…á´á´¡É´ÊŸá´á´€á´… âœ›", callback_data=f"stream#{file.file_id}")
                ],[
                    InlineKeyboardButton('âš¡ï¸ á´œá´˜á´…á´€á´›á´‡s âš¡ï¸', url=UPDATES_LINK),
                    InlineKeyboardButton('ðŸ’¡ êœ±á´œá´˜á´˜á´Ê€á´› ðŸ’¡', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('â‰ï¸ á´„ÊŸá´sá´‡ â‰ï¸', callback_data='close_data')
                ]]
            else:
                btn = [[
                    InlineKeyboardButton('âš¡ï¸ á´œá´˜á´…á´€á´›á´‡s âš¡ï¸', url=UPDATES_LINK),
                    InlineKeyboardButton('ðŸ’¡ êœ±á´œá´˜á´˜á´Ê€á´› ðŸ’¡', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('â‰ï¸ á´„ÊŸá´sá´‡ â‰ï¸', callback_data='close_data')
                ]]
            await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file.file_id,
                caption=f_caption,
                protect_content=settings['file_secure'],
                reply_markup=InlineKeyboardMarkup(btn)
            )
        return

    type_, grp_id, file_id = mc.split("_", 2)
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('No Such File Exist!')
    files = files_[0]
    settings = await get_settings(int(grp_id))
    if type_ != 'shortlink' and settings['shortlink']:
        if not await db.has_premium_access(message.from_user.id):
            link = await get_shortlink(settings['url'], settings['api'], f"https://t.me/{temp.U_NAME}?start=shortlink_{grp_id}_{file_id}")
            btn = [[
                InlineKeyboardButton("â™»ï¸ Get File â™»ï¸", url=link)
            ],[
                InlineKeyboardButton("ðŸ“ Êœá´á´¡ á´›á´ á´á´˜á´‡É´ ÊŸÉªÉ´á´‹ ðŸ“", url=settings['tutorial'])
            ]]
            await message.reply(f"[{get_size(files.file_size)}] {files.file_name}\n\nYour file is ready, Please get using this link. ðŸ‘", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return
    else:
        pass
        
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name = files.file_name,
        file_size = get_size(files.file_size),
        file_caption=files.caption
    )
    if settings.get('is_stream', IS_STREAM):
        btn = [[
            InlineKeyboardButton("âœ› á´¡á´€á´›á´„Êœ & á´…á´á´¡É´ÊŸá´á´€á´… âœ›", callback_data=f"stream#{file_id}")
        ],[
            InlineKeyboardButton('âš¡ï¸ á´œá´˜á´…á´€á´›á´‡s âš¡ï¸', url=UPDATES_LINK),
            InlineKeyboardButton('ðŸ’¡ êœ±á´œá´˜á´˜á´Ê€á´› ðŸ’¡', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('â‰ï¸ á´„ÊŸá´sá´‡ â‰ï¸', callback_data='close_data')
        ]]
    else:
        btn = [[
            InlineKeyboardButton('âš¡ï¸ á´œá´˜á´…á´€á´›á´‡s âš¡ï¸', url=UPDATES_LINK),
            InlineKeyboardButton('ðŸ’¡ êœ±á´œá´˜á´˜á´Ê€á´› ðŸ’¡', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('â‰ï¸ á´„ÊŸá´sá´‡ â‰ï¸', callback_data='close_data')
        ]]
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=settings['file_secure'],
        reply_markup=InlineKeyboardMarkup(btn)
    )

@Client.on_message(filters.command('index_channels') & filters.user(ADMINS))
async def channels_info(bot, message):
    """Send basic information of index channels"""
    ids = INDEX_CHANNELS
    if not ids:
        return await message.reply("Not set INDEX_CHANNELS")

    text = '**Indexed Channels:**\n\n'
    for id in ids:
        chat = await bot.get_chat(id)
        text += f'{chat.title}\n'
    text += f'\n**Total:** {len(ids)}'
    await message.reply(text)

@Client.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot, message):
    msg = await message.reply('Please Wait...')
    files = await Media.count_documents()
    users = await db.total_users_count()
    chats = await db.total_chat_count()
    u_size = get_size(await db.get_db_size())
    f_size = get_size(536870912 - await db.get_db_size())
    uptime = get_readable_time(time.time() - temp.START_TIME)
    await msg.edit(script.STATUS_TXT.format(files, users, chats, u_size, f_size, uptime))    
    
@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")
    grp_id = message.chat.id
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
    settings = await get_settings(grp_id)
    if settings is not None:
        buttons = [[
            InlineKeyboardButton('Auto Filter', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
            InlineKeyboardButton('âœ… Yes' if settings["auto_filter"] else 'âŒ No', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
        ],[
            InlineKeyboardButton('File Secure', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}'),
            InlineKeyboardButton('âœ… Yes' if settings["file_secure"] else 'âŒ No', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}')
        ],[
            InlineKeyboardButton('IMDb Poster', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'),
            InlineKeyboardButton('âœ… Yes' if settings["imdb"] else 'âŒ No', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')
        ],[
            InlineKeyboardButton('Spelling Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'),
            InlineKeyboardButton('âœ… Yes' if settings["spell_check"] else 'âŒ No', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')
        ],[
            InlineKeyboardButton('Auto Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'),
            InlineKeyboardButton(f'{get_readable_time(DELETE_TIME)}' if settings["auto_delete"] else 'âŒ No', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')
        ],[
            InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',),
            InlineKeyboardButton('âœ… Yes' if settings["welcome"] else 'âŒ No', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}'),
        ],[
            InlineKeyboardButton('Shortlink', callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'),
            InlineKeyboardButton('âœ… Yes' if settings["shortlink"] else 'âŒ No', callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'),
        ],[
            InlineKeyboardButton('Result Page', callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}'),
            InlineKeyboardButton('â›“ Link' if settings["links"] else 'ðŸ§² Button', callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}')
        ],[
            InlineKeyboardButton('Fsub', callback_data=f'setgs#is_fsub#{settings.get("is_fsub", IS_FSUB)}#{str(grp_id)}'),
            InlineKeyboardButton('âœ… On' if settings.get("is_fsub", IS_FSUB) else 'âŒ Off', callback_data=f'setgs#is_fsub#{settings.get("is_fsub", IS_FSUB)}#{str(grp_id)}')
        ],[
            InlineKeyboardButton('Stream', callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}'),
            InlineKeyboardButton('âœ… On' if settings.get("is_stream", IS_STREAM) else 'âŒ Off', callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}')
        ],[
            InlineKeyboardButton('âŒ Close âŒ', callback_data='close_data')
        ]]
        await message.reply_text(
            text=f"Change your settings for <b>'{message.chat.title}'</b> as your wish. âš™",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.reply_text('Something went wrong!')

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
    try:
        template = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Command Incomplete!")   
    await save_group_settings(grp_id, 'template', template)
    await message.reply_text(f"Successfully changed template for {title} to\n\n{template}")  
    
@Client.on_message(filters.command('set_caption'))
async def save_caption(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
    try:
        caption = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Command Incomplete!") 
    await save_group_settings(grp_id, 'caption', caption)
    await message.reply_text(f"Successfully changed caption for {title} to\n\n{caption}")
        
@Client.on_message(filters.command('set_shortlink'))
async def save_shortlink(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")    
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
    try:
        _, url, api = message.text.split(" ", 2)
    except:
        return await message.reply_text("<b>Command Incomplete:-\n\ngive me a shortlink & api along with the command...\n\nEx:- <code>/shortlink mdisklink.link 5843c3cc645f5077b2200a2c77e0344879880b3e</code>")   
    try:
        await get_shortlink(url, api, f'https://t.me/{temp.U_NAME}')
    except:
        return await message.reply_text("Your shortlink API or URL invalid, Please Check again!")   
    await save_group_settings(grp_id, 'url', url)
    await save_group_settings(grp_id, 'api', api)
    await message.reply_text(f"Successfully changed shortlink for {title} to\n\nURL - {url}\nAPI - {api}")
    
@Client.on_message(filters.command('get_custom_settings'))
async def get_custom_settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await m
