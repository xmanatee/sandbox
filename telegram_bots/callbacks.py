from data_management_2 import *
from emoji import emojize

import logging
from message_texts import *

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto)


# LEFT_BUTTON = ":+1:"
LEFT_BUTTON = ":fire:"
# LEFT_BUTTON = "\xF0\x9F\x94\xA5"
# RIGHT_BUTTON = ":-1:"
RIGHT_BUTTON = ":poop:"
# RIGHT_BUTTON = "\xF0\x9F\x92\xA9"


def build_keyboard(pros, cons):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            emojize("{}{}".format(pros, LEFT_BUTTON), use_aliases=True),
            callback_data="v,{},{}".format(pros+1, cons)),
        InlineKeyboardButton(
            emojize("{}{}".format(cons, RIGHT_BUTTON), use_aliases=True),
            callback_data="v,{},{}".format(pros, cons+1))
    ]])


def vote(bot, update):
    query = update.callback_query

    if try_add_vote(query.message.chat.id, query.message.from_user.id, query.message.message_id):
        text = query.message.text

        _, pros, cons = query.data.split(",")
        pros, cons = int(pros), int(cons)

        bot.edit_message_text(
            text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=build_keyboard(pros, cons))


def approve(bot, update):
    query = update.callback_query

    text = query.message.text

    button, media_group_id, from_chat_id = query.data.split(",")

    if button == "a":
        text += " [Approved]"
    elif button == "r":
        text += " [Rejected]"
    else:
        return False

    bot.edit_message_text(
        text,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)

    logging.info("sending to_channels {}".format(channel_chat_ids_f()))

    if button == "r":
        return
    photo_ids = get_and_delete_photo_ids(media_group_id)
    media_group = [InputMediaPhoto(id) for id in photo_ids]

    for channel_chat_id in channel_chat_ids_f():
        messages = bot.sendMediaGroup(channel_chat_id, media_group)

        bot.sendMessage(
            text=POLL_TEXT,
            chat_id=channel_chat_id,
            reply_markup=build_keyboard(0, 0))

        notify_user_about_post(bot, from_chat_id)


def notify_user_about_post(bot, from_chat_id):
    bot.sendMessage(
        text=USER_POST_NOTIFICATION_TEXT,
        chat_id=from_chat_id)


def inline_callback(bot, update):
    if update.callback_query.data.startswith("v,"):
        vote(bot, update)
    elif update.callback_query.data.startswith("a,") or update.callback_query.data.startswith("r,"):
        approve(bot, update)
