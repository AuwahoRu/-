from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class One_Button_menu():
    def __init__(self, num_menu: int ):
        self.num_menu = num_menu
    
async def inline_pis():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Настойка ⚙️', callback_data='settings'))
    keyboard.add(InlineKeyboardButton(text='Старт ▶️', callback_data='start'))
    return keyboard.adjust(2).as_markup()

            
# keyboard.add(InlineKeyboardButton(text='Настойка', callback_data='settings_op'))
# keyboard.add(InlineKeyboardButton(text='Старт', callback_data='start_op'))
        
start_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Письма 📨', callback_data='message_for_ole')],
                                             [InlineKeyboardButton(text='Напоминание(не работает)', callback_data='message_for_artem')]])


# confirm = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅', callback_data='YES')],
#                                              [InlineKeyboardButton(text='❌', callback_data='NO')]])





        
