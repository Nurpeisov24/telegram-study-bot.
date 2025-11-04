import os
import telebot

# ====== Подключение токена ======
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

# ====== Датасет знаний ======
knowledge = {
    "списки/массивы": {
        "description": "Коллекции элементов, упорядоченные и индексируемые.",
        "python": "my_list = [1, 2, 3]",
        "java": "int[] arr = {1, 2, 3};",
        "kotlin": "val list = listOf(1, 2, 3)"
    },
    "функции/методы": {
        "description": "Блоки кода, выполняющие определённую задачу.",
        "python": "def greet(name):\n    return f'Hello, {name}'",
        "java": "public String greet(String name) {\n    return \"Hello, \" + name;\n}",
        "kotlin": "fun greet(name: String) = \"Hello, $name\""
    },
    "классы": {
        "description": "Шаблон для создания объектов с атрибутами и методами.",
        "python": "class Car:\n    def __init__(self, model):\n        self.model = model",
        "java": "public class Car {\n    private String model;\n    public Car(String model) { this.model = model; }\n}",
        "kotlin": "class Car(val model: String)"
    },
    "наследование/интерфейсы": {
        "description": "Создание подклассов и реализация контрактов.",
        "python": "class ElectricCar(Car):\n    pass",
        "java": "class ElectricCar extends Car implements Vehicle {}",
        "kotlin": "class ElectricCar: Car(), Vehicle"
    },
    "исключения": {
        "description": "Обработка ошибок во время выполнения программы.",
        "python": "try:\n    1/0\nexcept ZeroDivisionError:\n    print('Ошибка')",
        "java": "try {\n    int a = 1/0;\n} catch (ArithmeticException e) {\n    System.out.println(\"Ошибка\");\n}",
        "kotlin": "try {\n    val a = 1/0\n} catch (e: ArithmeticException) {\n    println(\"Ошибка\")\n}"
    },
    "циклы": {
        "description": "Повторение действий.",
        "python": "for i in range(5):\n    print(i)",
        "java": "for(int i=0; i<5; i++) {\n    System.out.println(i);\n}",
        "kotlin": "for(i in 0..4) {\n    println(i)\n}"
    },
    "словари/Map": {
        "description": "Коллекции ключ-значение.",
        "python": "my_dict = {'a':1, 'b':2}",
        "java": "Map<String,Integer> map = new HashMap<>(); map.put(\"a\",1);",
        "kotlin": "val map = mapOf(\"a\" to 1, \"b\" to 2)"
    },
    "лямбда/функциональные объекты": {
        "description": "Короткие функции, которые можно передавать как объекты.",
        "python": "squared = lambda x: x**2",
        "java": "Function<Integer,Integer> squared = x -> x*x;",
        "kotlin": "val squared: (Int) -> Int = { x -> x*x }"
    },
    "декораторы/аннотации": {
        "description": "Изменяют поведение функций/классов.",
        "python": "@staticmethod\ndef hello():\n    pass",
        "java": "@Override\npublic String toString() { return \"\"; }",
        "kotlin": "@Deprecated(\"Use newFunc\")\nfun oldFunc() {}"
    },
    "корутины/async": {
        "description": "Асинхронное выполнение задач.",
        "python": "import asyncio\nasync def main():\n    await asyncio.sleep(1)",
        "java": "CompletableFuture.runAsync(() -> doSomething());",
        "kotlin": "GlobalScope.launch {\n    delay(1000)\n}"
    }
}

MAX_CHARS = 500  # ограничение длины ответа

# ====== Команда /start ======
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, (
        "👋 Привет! Я учебный бот.\n\n"
        "Я умею:\n"
        "💬 Отвечать на вопросы про Python, Java и Kotlin\n"
        "Попробуй написать, например:\n"
        "— списки в Python\n"
        "— функции в Java\n"
        "— классы в Kotlin"
    ))

# ====== Текстовые запросы ======
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.lower()
    
    for topic, info in knowledge.items():
        if topic in text:
            reply = f"{info['description']}\n\nPython: {info['python']}\nJava: {info['java']}\nKotlin: {info['kotlin']}"
            if len(reply) > MAX_CHARS:
                reply = reply[:MAX_CHARS] + "…"
            bot.reply_to(message, reply)
            return
    
    bot.reply_to(message, "🤔 Не понял вопрос. Попробуй уточнить, например: 'списки в Python'.")

# ====== Запуск ======
print("✅ Бот запущен и ждёт сообщений...")
bot.infinity_polling()
