import os
from dotenv import load_dotenv
import requests

from config import open_weather_token

from aiogram import executor
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database import UserSettings,UserLog, Session

load_dotenv()

bot = Bot(token=os.getenv('tg_bot_token'))
dp = Dispatcher(bot)

user_city_storage = {}

def log_user_command(user_id, command, response):
    session = Session()
    log_entry = UserLog(user_id=user_id, command_request=command, response=response)
    session.add(log_entry)
    session.commit()
    session.close()

button_set_city = KeyboardButton("Установить город")
button_my_city = KeyboardButton("Мой город")

keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_set_city, button_my_city)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Я Бот-Синоптик, созданный в качестве теста для BobrAi!\nВы можете написать мне город, а я вам отправлю точную погоду на данный момент!\nИли можете Установить свой город,чтобы быстро смотреть погоду!",
                        reply_markup=keyboard)
    

@dp.message_handler(lambda message: message.text == "Установить город")
async def set_city_handler(message: types.Message):
    await message.reply("Введите название города, который вы хотите установить:")
    user_city_storage[message.from_user.id] = True

@dp.message_handler(lambda message: message.from_user.id in user_city_storage)
async def city_name_handler(message: types.Message):
    user_id = message.from_user.id
    city_name = message.text
    
    session = Session()
    usersetting = session.query(UserSettings).filter_by(user_id=user_id).first()
    
    if usersetting:
        usersetting.fixed_city = city_name
    else:
        usersetting = UserSettings(user_id=user_id, fixed_city=city_name)
        session.add(usersetting)

    session.commit()
    session.close()

    log_user_command(user_id, "Установить город", f"Город установлен: {city_name}")
    user_city_storage.pop(user_id, None)

    await message.reply(f"Город '{city_name}' успешно установлен!", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Мой город")
async def my_city_handler(message: types.Message):
    user_id = message.from_user.id
    session = Session()
    usersetting = session.query(UserSettings).filter_by(user_id=user_id).first()
    
    if usersetting and usersetting.fixed_city:
        city = usersetting.fixed_city
        weather_info = await get_weather(city)
        log_user_command(user_id, "Мой город", weather_info)
        await message.reply(weather_info, reply_markup=keyboard)
    else:
        response = "Город не установлен. Используйте кнопку 'Установить город', чтобы установить его."
        log_user_command(user_id, "Мой город", response)
        await message.reply(response, reply_markup=keyboard)
    
    session.close()

async def get_weather(city_name):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F32B",
        "Mist": "Туман \U0001F32B"
    }

    try:
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={open_weather_token}&units=metric'
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        wd = code_to_smile.get(weather_description, "Честно говоря, к такому меня жизнь не готовила, посмотри в окошко!")
        
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        return f"Погода в городе: {city}\nТемпература: {cur_weather}°C, {wd}\nВлажность: {humidity}%\nВетер: {wind} м/с"

    except Exception as e:
        return "Проверьте название города или попробуйте позже."

@dp.message_handler(commands=['weather'])
async def weather_command(message: types.Message):
    city_name = message.get_args()  
    if city_name:
        weather_info = await get_weather(city_name)
        log_user_command(message.from_user.id, "weather", weather_info)
        await message.reply(weather_info, reply_markup=keyboard)
    else:
        await message.reply("Пожалуйста, укажите название города после команды /weather.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)