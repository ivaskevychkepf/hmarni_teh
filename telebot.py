import telebot
from telebot import types
import requests

telegram_token = '7766741139:AAGBcKO0G2lpZURE-ZRNExB3BcrN9RAwslA'
weather_api_token = 'bd5e378503939ddaee76f12ad7a97608'
hugging_face_token = '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'

stable_diffusion_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-medium"

bot = telebot.TeleBot(telegram_token)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привіт")
    btn2 = types.KeyboardButton("❓ Що ти вмієш?")
    btn3 = types.KeyboardButton("☀️ Прогноз погоди")
    btn4 = types.KeyboardButton("🎨 Генерувати зображення")
    markup.add(btn1, btn2, btn3, btn4)

    bot.send_message(
        message.chat.id,
        f"Привіт, {message.from_user.first_name}! Я бот із різними функціями. Обери опцію нижче:",
        reply_markup=markup
    )


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "👋 Привіт":
        bot.send_message(message.chat.id, "Привіт! Як твої справи?")

    elif message.text == "❓ Що ти вмієш?":
        bot.send_message(
            message.chat.id,
            "Я можу:\n- Привітатися\n- Розказати, що я вмію\n- Надати прогноз погоди\n- Згенерувати зображення"
        )

    elif message.text == "☀️ Прогноз погоди":
        bot.send_message(message.chat.id, "Введи назву міста, щоб я міг знайти прогноз погоди:")
        bot.register_next_step_handler(message, get_weather)

    elif message.text == "🎨 Генерувати зображення":
        bot.send_message(message.chat.id, "Введи опис зображення, яке ти хочеш згенерувати:")
        bot.register_next_step_handler(message, generate_image)

    else:
        bot.send_message(message.chat.id, "На жаль, я поки не знаю такої команди. Обери опцію з меню.")


def get_weather(message):
    city = message.text.strip()
    weather_url = (
        f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_token}&units=metric&lang=uk"
    )

    try:
        response = requests.get(weather_url)
        data = response.json()

        if data["cod"] == 200:
            city_name = data["name"]
            temp = data["main"]["temp"]
            weather_description = data["weather"][0]["description"]
            icon_code = data["weather"][0]["icon"]
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

            bot.send_photo(
                message.chat.id,
                icon_url,
                caption=f"Погода в місті {city_name}:\nТемпература: {temp}°C\nОпис: {weather_description.capitalize()}"
            )
        else:
            bot.send_message(message.chat.id, "Не вдалося знайти місто. Спробуй ще раз.")

    except Exception:
        bot.send_message(message.chat.id, "Сталася помилка під час отримання прогнозу погоди. Спробуй пізніше.")


def generate_image(message):
    prompt = message.text.strip()
    bot.send_message(message.chat.id, "Генерую зображення, зачекай кілька секунд...")

    headers = {"Authorization": f"Bearer {hugging_face_token}"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}

    try:
        response = requests.post(stable_diffusion_url, headers=headers, json=payload)

        if response.status_code == 200:
            with open("generated_image.png", "wb") as f:
                f.write(response.content)
            with open("generated_image.png", "rb") as img:
                bot.send_photo(message.chat.id, img, caption=f"Ось твоє зображення за запитом: \"{prompt}\"")
        else:
            bot.send_message(
                message.chat.id,
                f"Не вдалося згенерувати зображення. Код помилки: {response.status_code}"
            )

    except Exception as e:
        bot.send_message(message.chat.id, f"Сталася помилка під час генерації зображення: {e}")


bot.polling(non_stop=True)
