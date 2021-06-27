# Ported From WilliamButcher Bot.
# Credits Goes to WilliamButcherBot

from typing import Dict, Union

from pyrogram import filters

from SungJinwooRobot.db.mongo_helpers.reputation import is_reputation_on, reputation_off, reputation_on
from SungJinwooRobot.function.pluginhelpers import member_permissions
from SungJinwooRobot.services.mongo2 import db
from SungJinwooRobot.services.pyrogram import pbot as app

repdb = db.rep
reputation_positive_group = 3
reputation_negative_group = 4


async def int_to_alpha(user_id: int) -> str:
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    text = ""
    user_id = str(user_id)
    for i in user_id:
        text += alphabet[int(i)]
    return text


async def alpha_to_int(user_id_alphabet: str) -> int:
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    user_id = ""
    for i in user_id_alphabet:
        index = alphabet.index(i)
        user_id += str(index)
    user_id = int(user_id)
    return user_id


async def get_reputation_count() -> dict:
    chats = repdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {}
    chats_count = 0
    reputation_count = 0
    for chat in await chats.to_list(length=1000000):
        for i in chat["reputation"]:
            reputation_count += chat["reputation"][i]["reputation"]
        chats_count += 1
    return {"chats_count": chats_count, "reputation_count": reputation_count}


async def get_reputation(chat_id: int) -> Dict[str, int]:
    reputation = await repdb.find_one({"chat_id": chat_id})
    if reputation:
        reputation = reputation["reputation"]
    else:
        reputation = {}
    return reputation


async def get_reputation(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    reputation = await get_reputation(chat_id)
    if name in reputation:
        return reputation[name]


async def update_reputation(chat_id: int, name: str, karma: dict):
    name = name.lower().strip()
    reputation = await get_reputation(chat_id)
    reputation[name] = reputation
    await repdb.update_one(
        {"chat_id": chat_id}, {"$set": {"reputation": reputation}}, upsert=True
    )


_mod_name_ = "Reputation"
_help_ = """[UPVOTE] - Use upvote keywords like "+", "+1", "thanks" etc to upvote a message.
[DOWNVOTE] - Use downvote keywords like "-", "-1", etc to downvote a message.
Reply to a message with /reputation to check a user's reputation
Send /reputation without replying to any message to check reputation list of top 10 users
"""


regex_upvote = r"^((?i)\+|\+\+|\+1|thx|tnx|ty|thank you|thanx|thanks|pro|cool|good|👍)$"
regex_downvote = r"^(\-|\-\-|\-1|👎)$"


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=reputation_positive_group,
)
async def upvote(_, message):

    if not await is_reputation_on(message.chat.id):
        return
    try:
        if message.reply_to_message.from_user.id == message.from_user.id:
            return
    except:
        return
    chat_id = message.chat.id
    try:
        user_id = message.reply_to_message.from_user.id
    except:
        return
    user_mention = message.reply_to_message.from_user.mention
    current_reputation = await get_reputation(chat_id, await int_to_alpha(user_id))
    if current_reputation:
        current_reputation = current_reputation["reputation"]
        reputation = current_reputation + 1
        new_reputation = {"reputation": reputation}
        await update_reputation(chat_id, await int_to_alpha(user_id), new_reputation)
    else:
        reputation = 1
        new_reputation = {"reputation": reputation}
        await update_reputation(chat_id, await int_to_alpha(user_id), new_reputation)
    await message.reply_text(
        f"Incremented Reputation of {user_mention} By 1 \nTotal Points: {reputation}"
    )


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=reputation_negative_group,
)
async def downvote(_, message):

    if not await is_reputation_on(message.chat.id):
        return
    try:
        if message.reply_to_message.from_user.id == message.from_user.id:
            return
    except:
        return
    chat_id = message.chat.id
    try:
        user_id = message.reply_to_message.from_user.id
    except:
        return
    user_mention = message.reply_to_message.from_user.mention
    current_reputation = await get_reputation(chat_id, await int_to_alpha(user_id))
    if current_reputation:
        current_reputation = current_reputation["reputation"]
        reputation = current_reputation - 1
        new_reputation = {"reputation": reputation}
        await update_reputation(chat_id, await int_to_alpha(user_id), new_reputation)
    else:
        reputation = 1
        new_reputation = {"reputation": reputation}
        await update_reputation(chat_id, await int_to_alpha(user_id), new_reputation)
    await message.reply_text(
        f"Decremented Reputation Of {user_mention} By 1 \nTotal Points: {reputation}"
    )


@app.on_message(filters.command("reputation") & filters.group)
async def reputation(_, message):
    chat_id = message.chat.id
    if len(message.command) != 2:
        if not message.reply_to_message:
            reputation = await get_reputation(chat_id)
            msg = f"**Reputation list of {message.chat.title}:- **\n"
            limit = 0
            reputation_dicc = {}
            for i in reputation:
                user_id = await alpha_to_int(i)
                user_reputation = reputation[i]["reputation"]
                reputation_dicc[str(user_id)] = user_reputation
                reputation_arranged = dict(
                    sorted(reputation_dicc.items(), key=lambda item: item[1], reverse=True)
                )
            for user_idd, reputation_count in reputation_arranged.items():
                if limit > 9:
                    break
                try:
                    user_name = (await app.get_users(int(user_idd))).username
                except Exception:
                    continue
                msg += f"{user_name} : `{reputation_count}`\n"
                limit += 1
            await message.reply_text(msg)
        else:
            user_id = message.reply_to_message.from_user.id
            reputation = await get_reputation(chat_id, await int_to_alpha(user_id))
            if reputation:
                reputation = reputation["reputation"]
                await message.reply_text(f"**Total Points**: __{reputation}__")
            else:
                reputation = 0
                await message.reply_text(f"**Total Points**: __{reputation}__")
        return
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    user_id = message.from_user.id
    permissions = await member_permissions(chat_id, user_id)
    if "can_change_info" not in permissions:
        await message.reply_text("You don't have enough permissions.")
        return
    if status == "on" or status == "ON":
        await reputation_on(chat_id)
        await message.reply_text(
            f"Added Chat {chat_id} To Database. Reputation will be enabled here"
        )
    elif status == "off" or status == "OFF":
        await reputation_off(chat_id)
        await message.reply_text(
            f"Removed Chat {chat_id} To Database. Reputation will be disabled here"
        )
