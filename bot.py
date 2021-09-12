#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import json
import os
import re
import requests
import time

from typing import Optional, List

from telegram import Message, Update, Bot, User, InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, InlineQueryHandler, CommandHandler, run_async

# the secret configuration specific things
ENV = bool(os.environ.get("ENV", False))
if ENV:
    from sample_config import Config
else:
    from config import Config


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# this method will call the API, and return in the appropriate format
# with the name provided.
def ReTrieveFile(input_file_name, output_file_name):
    if os.path.exists(output_file_name):
        os.remove(output_file_name)
    headers = {
        "X-API-Key": Config.REM_BG_API_KEY,
    }
    files = {
        "image_file": (input_file_name, open(input_file_name, 'rb')),
    }
    r = requests.post("https://api.remove.bg/v1.0/removebg", headers=headers, files=files, allow_redirects=True, stream=True)
    with open(output_file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=Config.CHUNK_SIZE):
            fd.write(chunk)
    return output_file_name


def ReTrieveURL(input_url, output_file_name):
    if os.path.exists(output_file_name):
        os.remove(output_file_name)
    headers = {
        "X-API-Key": Config.REM_BG_API_KEY,
    }
    data = {
      "image_url": input_url
    }
    r = requests.post("https://api.remove.bg/v1.0/removebg", headers=headers, data=data, allow_redirects=True, stream=True)
    with open(output_file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=Config.CHUNK_SIZE):
            fd.write(chunk)
    return output_file_name


# the Telegram trackings
from chatbase import Message


def TRChatBase(chat_id, message_text, intent):
    msg = Message(api_key=Config.CBTOKEN,
                  platform="Telegram",
                  version="1.3",
                  user_id=chat_id,
                  message=message_text,
                  intent=intent)
    resp = msg.send()


@run_async
def version(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "version")
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        text="28.01.2019 19:45:30"
    )


@run_async
def rate(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "rate")
    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        reply_to_message_id=update.message.message_id,
        text="""If you like me, please give 5 star ⭐️⭐️⭐️⭐️⭐️ rating at: https://github.com/ALBINPRAVEEN/RemoveBg 
Have a nice day!"""
    )


@run_async
def developer(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "developer")
    inline_keyboard = []
    inline_keyboard.append([
        InlineKeyboardButton(text="Developer", url="https://albinpraveen.ml")
    ])
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=reply_markup,
        reply_to_message_id=update.message.message_id,
        text="There are multiple ways to contact him: 👇"
    )


@run_async
def start(bot, update):
    TRChatBase(update.message.chat_id, update.message.text, "start")
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text="""Hi. I am simply a wrapper around the awesome ReMove.BG API.
By uploading an image or URL, you agree to ReMove.BG's [Terms of Service](https://www.remove.bg/tos).
        """
    )


@run_async
def got_photo(bot: Bot, update: Update):
    TRChatBase(update.message.chat_id, update.message.text, "got_photo")
    msg = update.effective_message # type: Optional[Message]
    from_user_id = update.effective_chat.id # type: Optional[Chat]
    file_id = msg.photo[-1].file_id
    newFile = bot.get_file(file_id)
    input_file_name = "{}/{}.jpg".format(Config.DOWNLOAD_LOCATION, from_user_id)
    output_file_name = "{}/{}_nobg.jpg".format(Config.DOWNLOAD_LOCATION, from_user_id)
    newFile.download(input_file_name)
    out_put_file_name = ReTrieveFile(input_file_name, output_file_name)
    bot.send_document(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        document=open(out_put_file_name, "rb")
    )
    # clean up after send
    os.remove(input_file_name)
    os.remove(out_put_file_name)


@run_async
def got_link(bot: Bot, update: Update):
    TRChatBase(update.message.chat_id, update.message.text, "got_link")
    msg = update.effective_message # type: Optional[Message]
    from_user_id = update.effective_chat.id # type: Optional[Chat]
    input_url = msg.text
    output_file_name = "{}/{}_nobg.jpg".format(Config.DOWNLOAD_LOCATION, from_user_id)
    out_put_file_name = ReTrieveURL(input_url, output_file_name)
    bot.send_document(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        document=open(out_put_file_name, "rb")
    )
    # clean up after send
    os.remove(out_put_file_name)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    # TRChatBase(update.message.chat_id, update.message.text, "error")
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == "__main__":
    if not os.path.exists(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    updater = Updater(token=Config.TG_BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('developer', developer))
    updater.dispatcher.add_handler(CommandHandler('rate', rate))
    updater.dispatcher.add_handler(CommandHandler('version', version))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, got_photo))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(pattern=".*http.*"), got_link))
    updater.dispatcher.add_error_handler(error)
    if ENV:
        updater.start_webhook(
            listen="0.0.0.0", port=Config.PORT, url_path=TG_BOT_TOKEN)
        updater.bot.set_webhook(url=Config.URL + TG_BOT_TOKEN)
    else:
        updater.start_polling()
    updater.idle()
