#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (Updater, MessageHandler, Filters)
from tokens import tg_bot_token

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

admin_uns = ["xmanatee"]

un_to_chat_id = {}


def log(bot, update):
    un = update.message.from_user.username
    print(un, ": ", update.message.message_id)


# def authorize(bot, update):
#     un = update.message.from_user.username
#     un_to_chat_id[un] = update.message.chat.id
#
#     if update.message.text == "4815162342":
#         admin_uns.append(un)
#
#
# def photo(bot, update):
#     un = update.message.from_user.username
#     un_to_chat_id[un] = update.message.chat.id
#
#     from_chat_id = update.message.chat.id
#     message_id = update.message.message_id
#     user = update.message.from_user
#
#     logger.info("Photo of %s: %s", user.username)
#
#     for admin_un in admin_uns:
#         admin_chat_id = un_to_chat_id[admin_un]
#         bot.forwardMessage(admin_chat_id, from_chat_id, message_id)
#
#     update.message.reply_text("Sent to admins!")
#
#     return True


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(tg_bot_token)

    dp = updater.dispatcher

    # dp.add_handler(MessageHandler(Filters.text, authorize))
    # dp.add_handler(MessageHandler(Filters.photo, photo))

    dp.add_handler(MessageHandler(Filters.all, log))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
