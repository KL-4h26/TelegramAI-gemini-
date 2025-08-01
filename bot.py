from aiogram import Bot, Dispatcher, exceptions
from aiogram.filters import Command
from aiogram.types import Message
from config import *
import google.generativeai as genai
import asyncio
import re


disable = False

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
genai.configure(api_key=GEMINI_TOKEN)

chat_model = genai.GenerativeModel(model)

# Создание чата
# chat = chat_model.start_chat()

# Вводный промпт
# response = chat.send_message(START_PROMPTS["base"])

# Чаты
chats = {

}

def user_chat(user_id: int):
    global chats

    if user_id in chats:
        return chats[user_id]
    
    chats[user_id] = chat_model.start_chat()
    response = chats[user_id].send_message(START_PROMPTS["base"])

    return chats[user_id]
    


@dp.message(Command("disable"))
async def disable_command(message: Message):
    global disable

    # Проверка на админа
    if message.from_user.id in ADMINS:    
        # Перевод в состояние
        disable = True if not disable else False

        # Уведомление
        await message.answer(f'✅ Бот переведен в состояние: {"спящий" if disable else "работающий"}')
        return
    
    await message.answer("❗ У вас нет прав на выполнение команды")
        

@dp.message(Command("set_model"))
async def set_model(message: Message):
    global model

    # Проверка на админа
    if message.from_user.id in ADMINS:

        # получение модели
        get_model = re.search(r"^/set_model\s(.+)", message.text)

        # Проверка на присутствие текста
        if get_model == None:
            await message.answer("❗ Пожалуйста укажите модель (/set_model <имя модели>)")
            return
        
        # Получение
        model = get_model.group(1)

        # Изменение
        await message.answer("✅ Успешно изменена модель")
        return


    await message.answer("❗ У вас нет прав на выполнение команды")
        

@dp.message(Command("reload"))
async def reload_chat(message: Message):
    global chats

    # Создание нового чата
    chats[message.from_user.id] = chat_model.start_chat()
    response = chats[message.from_user.id].send_message(START_PROMPTS["base"])

    # Уведомление
    await message.answer("❗Создан новый чат")

@dp.message(Command("global_reload"))
async def gobal_reload_command(message: Message):
    global chats

    # Проверка на админа
    if message.from_user.id in ADMINS:
        # await message.answer(str(chats))
        chats = {

        }
        await message.answer("✅ Все чаты успешно очищены")
        return
    
    await message.answer("❗ У вас нет прав на выполнение команды")


@dp.message(Command("start"))
async def start_command(message: Message):
    if disable:
        return
    
    await message.answer("Привет я FreshAI, могу общатся с вами и развлекать :) А так же мой код скоро будет доступен на github!")

@dp.message(Command("ai"))
async def ai_responce(message: Message):
    if disable:
        return

    # Парсинг сообщения
    get_prompt = re.search(r"^/ai\s(.+)", message.text)

    # Проверка
    if get_prompt == None:
        await message.answer("❗ Пожалуйста пришлите сообщение (/ai <Ваше сообщение>)")
        return
        
    # Ответ chat
    try:
        # Попытка отправки сообщения
        await message.reply(user_chat(message.from_user.id).send_message(get_prompt.group(1)).text, parse_mode="markdown")

    except exceptions.TelegramBadRequest as error:
        # Проверяем что это конкретно ошибка форматирования
        if "can't parse entities" in str(error):
            # Отправляем без markdown
            await message.reply(user_chat(message.from_user.id).send_message(get_prompt.group(1)).text)
            return
        
        # Если ошибка не в markdown
        await message.answer(f"⚙️ Оооп, произошла ошибка, скажите @JustPythonLanguage что бы пофиксил, подробнее:\n\n```\n{error}\n```", parse_mode="markdown")

    except Exception as error:
        # Сообщение об ошибке
        await message.answer(f"⚙️ Оооп, произошла ошибка, скажите @JustPythonLanguage что бы пофиксил, подробнее:\n\n```\n{error}\n```", parse_mode="markdown")

async def start():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start())
