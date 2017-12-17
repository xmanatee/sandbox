#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (Updater, MessageHandler, Filters)
from tokens import tg_bot_token

import logging
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

admin_uns_filename = "admin_uns.json"
admin_uns = ["xmanatee"]

un_to_chat_id_filename = "un_to_chat_id.json"
un_to_chat_id = {}


def init():
    with open(un_to_chat_id_filename, "r") as f:
        un_to_chat_id = json.load(f)
    with open(admin_uns_filename, "r") as f:
        admin_uns = json.load(f)


def update_users(chat_id, username):
    if not username in un_to_chat_id:
        un_to_chat_id[username] = chat_id
        with open(un_to_chat_id_filename, "w") as f:
            json.dump(un_to_chat_id, f)


def update_admins(username):
    if not username in admin_uns:
        admin_uns.append(username)
        with open(admin_uns_filename, "w") as f:
            json.dump(admin_uns, f)


def authorize(bot, update):
    un = update.message.from_user.username
    un_to_chat_id[un] = update.message.chat.id

    if update.message.text == "4815162342":
        update_admins(un)


def photo(bot, update):
    un = update.message.from_user.username
    un_to_chat_id[un] = update.message.chat.id

    from_chat_id = update.message.chat.id
    message_id = update.message.message_id
    user = update.message.from_user

    logger.info("Photo of %s: %s", user.username)

    for admin_un in admin_uns:
        admin_chat_id = un_to_chat_id[admin_un]
        bot.forwardMessage(admin_chat_id, from_chat_id, message_id)

    update.message.reply_text("Sent to admins!")

    return True


def log(bot, update):
    un = update.message.from_user.username
    print(un, ": ", update.message.message_id)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(tg_bot_token)

    dp = updater.dispatcher

    # dp.add_handler(MessageHandler(Filters.text, authorize))
    dp.add_handler(MessageHandler(Filters.photo, photo))

    # dp.add_handler(MessageHandler(Filters.all, log))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
