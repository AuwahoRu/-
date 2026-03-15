from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

async def delete_all_user_messages(message: Message):
    """
    Удаляет все сообщения пользователя в текущем чате
    """
    chat_id = message.chat.id
    message_id = message.message_id
    
    # Удаляем сообщения в цикле (начиная с текущего и далее вниз)
    try:
        for i in range(message_id, 0, -1):
            await message.bot.delete_message(chat_id, message.message_id -i)
    except TelegramBadRequest as ex:  # noqa: E722
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")# Если сообщение не найдено или нет прав - пропускаем
        return
    

