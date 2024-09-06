import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

API_TOKEN = ''

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определение состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, помогающий вашему здоровью!")


# Функция для ввода возраста
@dp.message_handler(lambda message: message.text == "Calories")
async def set_age(message: types.Message):
    await UserState.age.set()
    await message.reply("Введите свой возраст:")


# Функция для ввода роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text  # Сохраняем возраст
    await UserState.growth.set()
    await message.reply("Введите свой рост (в см):")


# Функция для ввода веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['growth'] = message.text  # Сохраняем рост
    await UserState.weight.set()
    await message.reply("Введите свой вес (в кг):")


# Функция для отправки нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['weight'] = message.text  # Сохраняем вес

        # Используем формулу Миффлина - Сан Жеора (для мужчин)
        age = int(data['age'])
        growth = int(data['growth'])
        weight = int(data['weight'])

        # Формула для мужчин
        calories = 10 * weight + 6.25 * growth - 5 * age + 5

        await message.reply(f"Ваша норма калорий: {calories} ккал.")

    await state.finish()  # Завершение состояния


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)