#!/usr/bin/env python
# -*- coding: utf-8 -*-

from data_management_2 import *

import logging

from message_texts import *

from telegram import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto)
from telegram.ext import (CommandHandler, Updater, MessageHandler, Filters, CallbackQueryHandler)

import time

from tokens import tg_bot_token

from callbacks import inline_callback


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text(GREETING_TEXT)


def try_authorize(bot, update):
    post = None
    if update.channel_post:
        post = update.channel_post
    elif update.message:
        post = update.message

    from_chat_id = post.chat.id
    txt = post.text

    if txt == CHANNEL_PASSWORD:
        update_channels(from_chat_id)
        # logging.info("Authorized in channel {} by {}".format(from_chat_id, un))

    if txt == ADMIN_PASSWORD:
        update_admins(from_chat_id)
        # logging.info("Authorized {} as new admin {}".format(from_chat_id, un))


def photo(bot, update):
    from_chat_id = update.message.chat.id
    photo_ids = [photo.file_id for photo in update.message.photo]
    update_photos(from_chat_id, photo_ids)

    reply_markup = ReplyKeyboardMarkup([["/publish", "/reset"]],
                                       one_time_keyboard=False)

    update.message.reply_text(ADDED_PHOTO,
                              reply_markup=reply_markup)

    return True


def reset(bot, update):
    from_chat_id = update.message.chat.id
    if not chat_id_to_photo_ids_f(from_chat_id):
        update.message.reply_text("nothing to reset")
        return True

    update.message.reply_text("photo buffer reset")

    update_photos(from_chat_id, [], reset=True)

    return True


def publish(bot, update):
    from_chat_id = update.message.chat.id

    if not chat_id_to_photo_ids_f(from_chat_id):
        update.message.reply_text("nothing to send")
        return True

    photo_ids = chat_id_to_photo_ids_f(from_chat_id)
    media_group = [InputMediaPhoto(id) for id in photo_ids]

    media_group_id = time.time()

    add_photo_ids(media_group_id, photo_ids)

    admin_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Approve", callback_data="a,{},{}".format(media_group_id, from_chat_id)),
        InlineKeyboardButton("Reject", callback_data="r,{},{}".format(media_group_id, from_chat_id))
    ]])

    for admin_chat_id in admin_chat_ids_f():
        messages = bot.sendMediaGroup(admin_chat_id, media_group)

        bot.sendMessage(admin_chat_id,
                        "from @{}".format(update.message.from_user.username),
                        reply_markup=admin_keyboard)

    bot.sendMessage(from_chat_id, PHOTOS_SENT_TEXT)

    return reset(bot, update)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    init()

    updater = Updater(tg_bot_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('publish', publish))
    dp.add_handler(CommandHandler('reset', reset))

    dp.add_handler(MessageHandler(Filters.text, try_authorize))
    dp.add_handler(MessageHandler(Filters.photo, photo))
    dp.add_handler(CallbackQueryHandler(inline_callback))

    # dp.add_handler(MessageHandler(Filters.all, log))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
