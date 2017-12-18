#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from telegram.files.photosize import
# from telegram.files.inputfile import I
# from telegram import InputMediaPhoto
from telegram import InputMediaPhoto
from telegram import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (CommandHandler, Updater, MessageHandler, Filters)

import numpy as np

from tokens import tg_bot_token

from os import makedirs, listdir, remove
from os.path import join, exists
from collections import defaultdict, Set
import logging
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

admin_uns_filename = "./data/admin_uns.json"
admin_uns = []

un_to_chat_id_filename = "./data/un_to_chat_id.json"
un_to_chat_id = {}

chat_id_to_photo_ids_dir = "./data/photos"
chat_id_to_photo_ids = defaultdict(set)


def init():
    global admin_uns, un_to_chat_id, chat_id_to_photo_ids

    if exists(un_to_chat_id_filename):
        with open(un_to_chat_id_filename, "r") as f:
            un_to_chat_id = json.load(f)
        logging.info("Loaded chat_ids")

    if exists(admin_uns_filename):
        with open(admin_uns_filename, "r") as f:
            admin_uns = json.load(f)
        logging.info("Loaded admins")

    if exists(chat_id_to_photo_ids_dir):
        for fn in listdir(chat_id_to_photo_ids_dir):
            if fn.endswith(".json"):
                chat_id = int(fn[:-5])
                with open(join(chat_id_to_photo_ids_dir, fn), "r") as f:
                    chat_id_to_photo_ids[chat_id] = set(json.load(f))
        logging.info("Loaded photo_ids")
    else:
        makedirs(chat_id_to_photo_ids_dir)


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


def update_photos(chat_id, photos, reset=False):

    fn = join(chat_id_to_photo_ids_dir, str(chat_id) + ".json")
    if reset:
        del chat_id_to_photo_ids[chat_id]
        remove(fn)
        return

    file_ids = [p.file_id for p in photos]
    file_sizes = [p.width * p.height for p in photos]
    i = np.argmax(file_sizes)

    chat_id_to_photo_ids[chat_id].add(file_ids[i])

    # chat_id_to_photo_ids[chat_id].update(photos)

    with open(fn, "w") as f:
        json.dump(list(chat_id_to_photo_ids[chat_id]), f)


def authorize(bot, update):
    un = update.message.from_user.username
    from_chat_id = update.message.chat.id

    update_users(from_chat_id, un)

    logging.info("text from {}".format(un))

    if update.message.text == "4815162342":
        update_admins(un)


reply_keyboard = [[
    "/review",
    "/reset"
]]

reply_markup = ReplyKeyboardMarkup(reply_keyboard,
                                   one_time_keyboard=False)

admin_keyboard = InlineKeyboardMarkup([[
    InlineKeyboardButton("Approve", callback_data="approve_")
]])


def photo(bot, update):
    un = update.message.from_user.username
    from_chat_id = update.message.chat.id

    logging.info("photo from {}".format(un))

    update_users(from_chat_id, un)

    update_photos(from_chat_id, update.message.photo)

    logging.info("updated for {} : {}".format(un, chat_id_to_photo_ids[from_chat_id]))

    update.message.reply_text(
        'added to draft',
        reply_markup=reply_markup)

    return True


def reset(bot, update):
    from_chat_id = update.message.chat.id
    if not chat_id_to_photo_ids[from_chat_id]:
        update.message.reply_text("nothing to reset")
                                  # reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text("photo buffer reset")
                                  # reply_markup=ReplyKeyboardRemove())

    update_photos(from_chat_id, [], reset=True)

    return True


def review(bot, update):
    un = update.message.from_user.username
    from_chat_id = update.message.chat.id

    if not chat_id_to_photo_ids[from_chat_id]:
        update.message.reply_text("nothing to review")
    else:
        media_group = [InputMediaPhoto(id) for id in chat_id_to_photo_ids[from_chat_id]]

        logging.info("sending for review to {}".format(admin_uns))

        for admin_un in admin_uns:
            admin_chat_id = un_to_chat_id[admin_un]
            bot.sendMediaGroup(admin_chat_id, media_group)
            bot.sendMessage(admin_chat_id, "from @{}".format(un),
                            reply_markup=admin_keyboard)

    photos_num = len(chat_id_to_photo_ids[from_chat_id])
    bot.sendMessage(from_chat_id, "{} photos sent for review".format(photos_num))

    return reset(bot, update)


def log(bot, update):
    un = update.message.from_user.username
    print(un, ": ", update.message.message_id)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    init()

    updater = Updater(tg_bot_token)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, authorize))

    dp.add_handler(MessageHandler(Filters.photo, photo))

    dp.add_handler(CommandHandler('review', review))
    dp.add_handler(CommandHandler('reset', reset))

    # dp.add_handler(MessageHandler(Filters.all, log))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
