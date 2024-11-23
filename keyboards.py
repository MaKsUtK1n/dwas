from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from random import shuffle
from config import OWNER_ID


def start_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Получить $EXL", callback_data="quigame"))
    keyboard.row(InlineKeyboardButton("Профиль", callback_data="profile"))
    keyboard.row(InlineKeyboardButton("Улучшения", callback_data="upgrades"))
    keyboard.row(InlineKeyboardButton("Информация", callback_data="info"), InlineKeyboardButton("Топ", callback_data="top"))
    return keyboard


def tops_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Топ по $EXL", callback_data="topqui"))    
    keyboard.row(InlineKeyboardButton("Топ по $USD", callback_data="topbal"))    
    keyboard.row(InlineKeyboardButton("Топ по выведенным $USD", callback_data="topwit"))    
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))    
    return keyboard


def top_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup() 
    keyboard.row(InlineKeyboardButton("Назад", callback_data="top"))    
    return keyboard


def quigame_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    quigame = [*((True,) * 3), *((False,) * 6)]
    shuffle(quigame)
    for k in range(3):
        row = []
        for i in range(3):
            row.append(InlineKeyboardButton("⬜️", callback_data=f'{"qui" if quigame[k + i] else "notqui"}'))
        keyboard.row(*row)
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start")) 
    return keyboard


def info_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Поддержка", f"tg://user?id={OWNER_ID}"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))    
    return keyboard


def profile_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Реферальная система", callback_data="ref"))
    keyboard.row(InlineKeyboardButton("Пополнить", callback_data="deposit"), InlineKeyboardButton("Вывести", callback_data="withdraw"))
    keyboard.row(InlineKeyboardButton("Обменять $EXL на USDT", callback_data="change"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))    
    return keyboard

def cancel_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Отмена", callback_data="cancel"))    
    return keyboard


def withdraw_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Да", callback_data="withdraw_yes"))   
    keyboard.row(InlineKeyboardButton("Нет", callback_data="profile")) 
    return keyboard


def upgrades_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("X2", callback_data="pppx2"), InlineKeyboardButton("X3", callback_data="pppx3"), InlineKeyboardButton("X5", callback_data="pppx5"))
    keyboard.row(InlineKeyboardButton("AutoEarn", callback_data="pppauto"))
    keyboard.row(InlineKeyboardButton("Назад", callback_data="start"))
    return keyboard


def ppp_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Купить", callback_data="upgrade_buy"))   
    keyboard.row(InlineKeyboardButton("Назад", callback_data="upgrades")) 
    return keyboard