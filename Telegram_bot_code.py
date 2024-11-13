import telebot
import http.client
import json
from telebot import types
'''
Библиотека json используется для проверки полученных данных, поскольку OpenJourney
отправляет только закодированные данные, что приведет к ошибке, 
которую вы можете интерпретировать как ошибку в API или URL.
Если вы собираетесь дополнять код, я советую вам ознакомиться с документацией
----------------------------------------------------------------------------------------------------
The json library is used to verify the received data, since OpenJourney
sends only encoded data, which will produce an error
that you can count as an error in the API or URL.
If you are going to supplement the code, I advise you to familiarize yourself with the documentation
'''
# Инициализация бота
# Initializing the bot
bot = telebot.TeleBot('Bot_token')

# Новый ключ API для RapidAPI (OpenJourney)
# New API key for RapidAPI (OpenJourney)
RAPIDAPI_KEY = "Rapid_key"

# Новый URL для запросов к OpenJourney через RapidAPI
# New URL for requests to OpenJourney via RapidAPI
OPENJOURNEY_API_URL = "/models/stabilityai/stable-diffusion-xl-base-1.0"

# Функция для создания изображения через OpenJourney API (с использованием http.client)
# Function for creating an image via the OpenJourney API (using http.client)
def generate_image(prompt):
    conn = http.client.HTTPSConnection("openjourney1.p.rapidapi.com")

    payload = json.dumps({
        "inputs": prompt
    })

    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': "openjourney1.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    # Отправляем запрос на создание изображения
    # Sending a request to create an image
    try:
        conn.request("POST", OPENJOURNEY_API_URL, payload, headers)

        res = conn.getresponse()
        data = res.read()

        # Логируем ответ для диагностики
        # We log the response for diagnosis
        print(f"Ответ от API: {data[:100]}...")  # Печатаем первые 100 байт данных для отладки

        # Пытаемся понять, что возвращает API (например, проверка типа данных)
        # Trying to figure out what the API returns (for example, checking the data type)
        if res.getheader('Content-Type') == 'application/json':
            # Если это JSON, то обрабатываем как обычный ответ
            # If it is JSON, then we process it as a normal response
            response_json = json.loads(data.decode("utf-8"))
            if "outputs" in response_json:
                return response_json["outputs"][0]
            else:
                print("Ответ не содержит ожидаемой информации.")
                return None
        else:
            # Если это не JSON, то предполагаем, что это изображение
            # If it's not JSON, then we assume it's an image
            return data  # Возвращаем бинарные данные изображения / Returning binary image data

    except Exception as e:
        print(f"Ошибка при запросе: {e}")
        return None

# Обработчик команды /start
# Handler of the /start command
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот для генерации картинок с помощью OpenJourney!", reply_markup=markup)

# Старт процесса создания картинки
# Start of the image creation process
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Сгенерировать картинку')
        btn2 = types.KeyboardButton('Правила бота')
        btn3 = types.KeyboardButton('API OpenJourney')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup)

    elif message.text == 'Сгенерировать картинку':
        # Запрашиваем, какой запрос хочет пользователь для изображения
        # Requesting which request the user wants for the image
        bot.send_message(message.from_user.id, 'Напишите запрос для создания картинки (чем более подробным, тем лучше)', parse_mode='Markdown')

        # Сохраняем состояние пользователя, что он начал процесс генерации
        # Saving the user's state that he has started the generation process
        bot.register_next_step_handler(message, handle_image_request)

    elif message.text == 'Правила бота':
        bot.send_message(message.from_user.id, 'Правила использования бота: ...')

    elif message.text == 'API OpenJourney':
        bot.send_message(message.from_user.id, 'Получить API ключ можно по ' + '[ссылке](https://rapidapi.com/openjourney)', parse_mode='Markdown')


# Обработка текстового запроса для генерации изображения
# Processing a text request to generate an image
def handle_image_request(message):
    prompt = message.text

    # Генерация картинки
    # Image generation
    bot.send_message(message.from_user.id, "🖼️ Создание изображения... Пожалуйста, подождите.")

    result = generate_image(prompt)

    if result:
        try:
            # Если это изображение, отправляем его
            # If this is an image, we send it
            if isinstance(result, bytes):
                bot.send_photo(message.from_user.id, result)
                bot.send_message(message.from_user.id, "🎉 Изображение успешно сгенерировано!")
            else:
                bot.send_message(message.from_user.id, "Ошибка при генерации изображения.")
        except Exception as e:
            print(f"Ошибка при отправке изображения: {e}")
            bot.send_message(message.from_user.id, "Не удалось загрузить изображение.")
    else:
        bot.send_message(message.from_user.id, "Ошибка при генерации изображения.")

# Запуск бота
# Launching the bot
bot.polling(none_stop=True, interval=0)
