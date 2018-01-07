from collections import defaultdict

import json
import logging

from os import makedirs, listdir, remove
from os.path import join, exists


channel_chat_ids_filename = "./data/channel_chat_ids.json"
channel_chat_ids = []

admin_chat_ids_filename = "./data/admin_chat_ids.json"
admin_chat_ids = []

chat_id_to_photo_ids_dir = "./data/photos"
chat_id_to_photo_ids = defaultdict(set)


def channel_chat_ids_f():
    return channel_chat_ids


def admin_chat_ids_f():
    return admin_chat_ids


def chat_id_to_photo_ids_f(chat_id):
    return chat_id_to_photo_ids[chat_id]


def init():
    global channel_chat_ids, admin_chat_ids, chat_id_to_photo_ids

    # uploading channel_ids if exists
    if exists(channel_chat_ids_filename):
        with open(channel_chat_ids_filename, "r") as f:
            channel_chat_ids = json.load(f)
        logging.info("Loaded channel_ids")

    # uploading admins usernames if exists
    if exists(admin_chat_ids_filename):
        with open(admin_chat_ids_filename, "r") as f:
            admin_chat_ids = json.load(f)
        logging.info("Loaded admin_uns")
    #
    # # uploading chat_ids if exists
    # if exists(un_to_chat_id_filename):
    #     with open(un_to_chat_id_filename, "r") as f:
    #         un_to_chat_id = json.load(f)
    #     logging.info("Loaded chat_ids")

    # uploading photo_ids if exists
    if exists(chat_id_to_photo_ids_dir):
        for fn in listdir(chat_id_to_photo_ids_dir):
            if fn.endswith(".json"):
                chat_id = int(fn[:-5])
                with open(join(chat_id_to_photo_ids_dir, fn), "r") as f:
                    chat_id_to_photo_ids[chat_id] = set(json.load(f))
        logging.info("Loaded photo_ids")
    else:
        makedirs(chat_id_to_photo_ids_dir)


def update_admins(chat_id):
    if not chat_id in admin_chat_ids:
        admin_chat_ids.append(chat_id)
        with open(admin_chat_ids_filename, "w") as f:
            json.dump(admin_chat_ids, f)


def update_channels(chat_id):
    if not chat_id in channel_chat_ids:
        channel_chat_ids.append(chat_id)
        with open(channel_chat_ids_filename, "w") as f:
            json.dump(channel_chat_ids, f)


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

    with open(fn, "w") as f:
        json.dump(list(chat_id_to_photo_ids[chat_id]), f)
