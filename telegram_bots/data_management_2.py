import sqlite3

import logging

conn = None
cursor = None


def channel_chat_ids_f():
    rows = cursor.execute("SELECT chat_id FROM channel_chat_ids").fetchall()
    return [row[0] for row in rows]


def admin_chat_ids_f():
    rows = cursor.execute("SELECT chat_id FROM admin_chat_ids").fetchall()
    return [row[0] for row in rows]


def chat_id_to_photo_ids_f(chat_id):
    chat_id = str(chat_id)
    rows = cursor.execute("SELECT photo_id FROM chat_id_to_photo_ids WHERE chat_id == ?;", (chat_id,)).fetchall()
    return [row[0] for row in rows]


def try_add_vote(chat_id, user_id, message_id):
    rows = cursor.execute("SELECT * FROM votes WHERE chat_id == ? AND user_id == ? AND message_id == ?;",
                          (chat_id, user_id, message_id)).fetchall()
    if rows:
        return False
    cursor.execute("INSERT OR IGNORE INTO votes values (?, ?, ?);", (chat_id, user_id, message_id))
    conn.commit()
    return True


def add_photo_ids(media_group_id, photo_ids):
    for photo_id in photo_ids:
        cursor.execute("INSERT OR IGNORE INTO media_group_id_to_photo_ids values (?, ?);",
                       (media_group_id, photo_id))
    conn.commit()


def get_and_delete_photo_ids(media_group_id):
    media_group_id = str(media_group_id)
    rows = cursor.execute("SELECT photo_id FROM media_group_id_to_photo_ids WHERE media_group_id == ?;", (media_group_id,)).fetchall()
    cursor.execute("DELETE FROM media_group_id_to_photo_ids WHERE media_group_id == ?;", (media_group_id,))
    conn.commit()

    rows = [row[0] for row in rows]
    return rows


def init():
    global conn, cursor

    conn = sqlite3.connect('./data/bot_tables.sqlite', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS channel_chat_ids (chat_id INTEGER PRIMARY key);")
    conn.commit()
    logging.info("Loaded channel_chat_ids")

    cursor.execute("CREATE TABLE IF NOT EXISTS admin_chat_ids (chat_id INTEGER PRIMARY key);")
    conn.commit()
    logging.info("Loaded admin_chat_ids")

    cursor.execute("CREATE TABLE IF NOT EXISTS chat_id_to_photo_ids (chat_id INTEGER, photo_id TEXT, PRIMARY KEY (chat_id, photo_id));")
    conn.commit()
    logging.info("Loaded chat_id_to_photo_ids")

    cursor.execute("CREATE TABLE IF NOT EXISTS votes (chat_id INTEGER, user_id INTEGER, message_id INTEGER);")
    conn.commit()
    logging.info("Loaded votes")

    cursor.execute("CREATE TABLE IF NOT EXISTS media_group_id_to_photo_ids (media_group_id INTEGER, photo_id INTEGER);")
    conn.commit()
    logging.info("Loaded group_id_to_photo_ids")


def update_admins(chat_id):
    chat_id = str(chat_id)
    cursor.execute("INSERT OR IGNORE INTO admin_chat_ids values (?);", (chat_id,))
    conn.commit()


def update_channels(chat_id):
    chat_id = str(chat_id)
    cursor.execute("INSERT OR IGNORE INTO channel_chat_ids values (?);", (chat_id,))
    conn.commit()


def update_photos(chat_id, photo_ids, reset=False):
    chat_id = str(chat_id)
    if reset:
        cursor.execute("DELETE FROM chat_id_to_photo_ids WHERE chat_id == ?;", (chat_id,))
        conn.commit()
        return

    photo_id = str(photo_ids[-1])
    cursor.execute("INSERT OR IGNORE INTO chat_id_to_photo_ids values (?, ?);", (chat_id, photo_id))
    conn.commit()


def log_all():
    rows = cursor.execute("SELECT * FROM channel_chat_ids").fetchall()
    logging.info("channel_chat_ids:")
    logging.info(rows)

    rows = cursor.execute("SELECT * FROM admin_chat_ids").fetchall()
    logging.info("admin_chat_ids:")
    logging.info(rows)

    rows = cursor.execute("SELECT * FROM chat_id_to_photo_ids;").fetchall()
    logging.info("chat_id_to_photo_ids:")
    logging.info(rows)


def close():
    conn.close()

