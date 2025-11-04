import telebot
import os
import io
import uuid
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from telebot import types

# ====== Подключение токена ======
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

# ====== База знаний ======
knowledge = {
    "Python": {
        "О языке": "🐍 Python — это язык программирования высокого уровня с динамической типизацией и простой синтаксис.",
        "Списки": "Списки (list) — изменяемые коллекции данных. Пример: my_list = [1, 2, 3]",
        "Декораторы": "Декораторы — это функции, изменяющие поведение других функций.",
    },
    "Java": {
        "О языке": "☕ Java — объектно-ориентированный язык, широко используемый для Android и серверных приложений.",
        "Класс": "Класс — это шаблон, описывающий объекты. Пример: public class Example {}",
        "Интерфейс": "Интерфейс — контракт, который реализуют классы. Пример: interface Car { void drive(); }",
    },
    "Kotlin": {
        "О языке": "🚀 Kotlin — современный язык, официально поддерживаемый для Android.",
        "Корутины": "Корутины — инструмент для асинхронного программирования в Kotlin.",
        "Null safety": "Null-safety — защита от ошибок NullPointerException.",
    }
}

# ====== Команда /start ======
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [types.KeyboardButton(lang) for lang in knowledge.keys()]
    markup.add(*buttons)
    
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я учебный бот.\n\n"
        "Я умею:\n"
        "💬 Отвечать на вопросы по Python, Java и Kotlin\n"
        "🖼️ Читать текст с изображений\n"
        "🎙️ Распознавать голосовые сообщения\n"
        "🎞️ Узнавать длительность видео\n\n"
        "Выбери язык для изучения с помощью кнопки ниже:",
        reply_markup=markup
    )

# ====== Выбор языка ======
@bot.message_handler(func=lambda message: message.text in knowledge.keys())
def choose_topic(message):
    lang = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [types.KeyboardButton(topic) for topic in knowledge[lang].keys()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, f"Выбери тему по {lang}:", reply_markup=markup)

# ====== Выбор темы ======
@bot.message_handler(func=lambda message: any(message.text in topics for topics in knowledge.values()))
def show_answer(message):
    for lang, topics in knowledge.items():
        if message.text in topics:
            bot.send_message(message.chat.id, topics[message.text])
            return

# ====== Фото (распознавание текста) ======
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        image = Image.open(io.BytesIO(downloaded))

        text = pytesseract.image_to_string(image, lang='rus+eng')
        if text.strip():
            bot.reply_to(message, f"🖼️ Текст на изображении:\n\n{text}")
        else:
            bot.reply_to(message, "😕 Не удалось распознать текст на фото.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке изображения: {e}")

# ====== Голосовые сообщения ======
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    voice_file = None
    wav_file = None
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded = bot.download_file(file_info.file_path)

        voice_file = f"voice_{uuid.uuid4().hex}.ogg"
        wav_file = f"voice_{uuid.uuid4().hex}.wav"

        with open(voice_file, "wb") as f:
            f.write(downloaded)

        # Конвертация OGG -> WAV
        AudioSegment.from_ogg(voice_file).export(wav_file, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")

        bot.reply_to(message, f"🎙️ Распознанная речь:\n{text}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при распознавании аудио: {e}")
    finally:
        if voice_file and os.path.exists(voice_file):
            os.remove(voice_file)
        if wav_file and os.path.exists(wav_file):
            os.remove(wav_file)

# ====== Видео (анализ длительности) ======
@bot.message_handler(content_types=['video'])
def handle_video(message):
    video_file = None
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded = bot.download_file(file_info.file_path)

        video_file = f"video_{uuid.uuid4().hex}.mp4"
        with open(video_file, "wb") as f:
            f.write(downloaded)

        clip = VideoFileClip(video_file)
        duration = round(clip.duration, 2)
        clip.close()

        bot.reply_to(message, f"🎞️ Видео получено!\nДлительность: {duration} сек.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке видео: {e}")
    finally:
        if video_file and os.path.exists(video_file):
            os.remove(video_file)

# ====== Обработка обычного текста ======
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.lower().strip()
    # Ищем язык и тему
    for lang, topics in knowledge.items():
        if lang.lower() in text:
            for keyword, answer in topics.items():
                if keyword.lower() in text:
                    bot.reply_to(message, answer)
                    return
            bot.reply_to(message, f"🧠 Что именно ты хочешь узнать о {lang}?")
            return
    # Ищем только тему
    for lang, topics in knowledge.items():
        for keyword, answer in topics.items():
            if keyword.lower() in text:
                bot.reply_to(message, answer)
                return

    bot.reply_to(message, "🤔 Не понял вопрос. Попробуй уточнить, например: 'О языке Python'.")

# ====== Запуск ======
print("✅ Бот запущен и ждёт сообщений...")
bot.infinity_polling()
