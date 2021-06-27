from SungJinwooRobot.services.mongo2 import db

repdb = db.rep2


async def is_reputation_on(chat_id: int) -> bool:
    chat = await repdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def reputation_on(chat_id: int):
    is_reputation = await is_reputation_on(chat_id)
    if is_reputation:
        return
    return await repdb.insert_one({"chat_id": chat_id})


async def reputation_off(chat_id: int):
    is_reputation = await is_reputation_on(chat_id)
    if not is_reputation:
        return
    return await repdb.delete_one({"chat_id": chat_id})
