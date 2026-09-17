import asyncio
import pandas as pd
import os

from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.exceptions import TelegramBadRequest

bottoken = os.environ.get('BOT_TOKEN')
if not bottoken:
    raise ValueError("BOT_TOKEN environment variable not set")

bot = Bot(token=bottoken)
excel_file = 'schedule.xlsx'
dp = Dispatcher()

callback_to_days = {
    "day_monday": "Понедельник",
    "day_tuesday":"Вторник",
    "day_wednesday":"Среда",
    "day_thursday":"Четверг",
    "day_friday":"Пятница",
    "day_saturday":"Суббота",
    "day_sunday":"Воскресенье"
}





def get_day_excel(day_name: str):
    try:
        df = pd.read_excel(excel_file, engine='openpyxl')
        df['День'] = df['День'].ffill()
        df = df.dropna(subset=['Время начала', 'Название пары'], how='all')
        df['День'] = df['День'].astype(str).str.strip().str.lower()
        search_day = day_name.strip().lower()
        filtered_df = df[df['День'] == search_day]
        if filtered_df.empty:
            return f"На {day_name} никаких занятий не найдено, отдых."
        response = f"📅 Расписание на {day_name}:\n\n"
        for index, row in filtered_df.iterrows():
            number = str(row['Номер пары'])[:1]
            start_time = row['Время начала']
            finish_time = row['Время окончания']
            subject_name = row['Название пары']
            subject_type = row['Вид']
            lector = row['Преподаватель']
            time_str = f"{str(start_time)[:5]}-{str(finish_time)[:5]}"
            response += f"Номер пары: {number}\n     Время {time_str}\n     {subject_name}\n     {subject_type}\n     {lector}\n"

        return response
    except FileNotFoundError:
        return "Файл не найден"
    except Exception as e:
        return f"Ошибка при чтении файла:{e}"

def get_days_keyboard():
    days = [
        ("Понедельник", "day_monday"),
        ("Вторник", "day_tuesday"),
        ("Среда", "day_wednesday"),
        ("Четверг", "day_thursday"),
        ("Пятница", "day_friday"),
        ("Суббота", "day_saturday"),
        ("Воскресенье", "day_sunday")
    ]
    buttons = []
    for i in range(0, len(days), 2):
        row = []
        for name, callback_data in days[i:i + 2]:
            row.append(InlineKeyboardButton(text=name, callback_data=callback_data))
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        text = "Выбери день, чтобы узнать расписание",
        reply_markup = get_days_keyboard()
    )

@dp.callback_query(F.data.in_(callback_to_days.keys()))

async def process_day_button(callback: types.CallbackQuery):
    callback_data = callback.data
    button_day_name = callback_to_days[callback_data]
    schedule_text = get_day_excel(button_day_name)
    try:
        await callback.message.edit_text(text=schedule_text, reply_markup = get_days_keyboard())
    except TelegramBadRequest:
        pass
    await callback.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

