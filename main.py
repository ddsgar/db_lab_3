import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Подключение к базе данных
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Создание таблиц в базе данных
c.execute('''CREATE TABLE IF NOT EXISTS medicine (
                code_medicine INTEGER PRIMARY KEY,
                name_medicine TEXT,
                use TEXT,
                value TEXT,
                count INTEGER,
                distributor TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS sells (
                code_medicine INTEGER,
                code_seller INTEGER,
                date_sell TEXT,
                price REAL,
                count INTEGER,
                code_input INTEGER
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS sellers (
                code_seller INTEGER PRIMARY KEY,
                name TEXT,
                full_name TEXT,
                address TEXT,
                phone TEXT,
                director TEXT
            )''')

# Создание бота
bot = Bot(token='7028908084:AAHe6UTnNIEKrBhW13dLIVjB0_tkcnMw4P0')
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def show_table(message: types.Message):
    await message.reply('Бот запущен')

@dp.message_handler(commands=['commands'])
async def commands_list(message: types.Message):
    await message.reply('Список доступных команд:\n'
                        '\n'
                        '/start - запуск бота\n'
                        '/command - список доступных команд\n'
                        '/show [название таблицы] - первые 5 строк из указанной таблицы\n'
                        '/add [название] [1] [2] [3] [4] [5] [6] - добавление новой строки в указанную таблицу\n'
                        '/sellers - информация о поставщиках\n'
                        '/salesum - общая информация о продажах каждого лекарства\n'
                        '/dates - общая информация о датах продаж')


# Функция, которая выводит первые 5 строк из указанной таблицы
@dp.message_handler(commands=['show'])
async def show_table(message: types.Message):
    # Получение названия таблицы из команды
    table_name = message.text.split()[1]

    try:
        # Выполнение запроса к базе данных
        c.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = c.fetchall()

        # Формирование ответа
        response = f"Первые 5 строк из таблицы '{table_name}':\n\n"
        for row in rows:
            response += " | ".join(map(str, row)) + "\n"

        await message.reply(response)

    except sqlite3.Error as e:
        await message.reply(f"Ошибка: {e}")


# Словарь для хранения временных данных ввода
user_data = {}


@dp.message_handler(commands=['add'])
async def add_row(message: types.Message):
    # Получение названия таблицы и данных для новой строки из команды
    parts = message.text.split()
    table_name = parts[1]
    values = parts[2:]

    try:
        # Формирование SQL-запроса для вставки новой строки
        placeholders = ', '.join('?' * len(values))
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"

        # Выполнение запроса к базе данных
        c.execute(query, values)
        conn.commit()

        await message.reply(f"Новая строка добавлена в таблицу '{table_name}'.")

    except sqlite3.Error as e:
        await message.reply(f"Ошибка: {e}")


@dp.message_handler(commands=['sellers'])
async def get_unique_sellers(message: types.Message):
    try:
        # Выполнение запроса к базе данных для получения уникальных поставщиков
        c.execute("SELECT DISTINCT code_seller FROM sells")
        unique_sellers = c.fetchall()

        # Подсчет числа уникальных поставщиков
        num_sellers = len(unique_sellers)

        # Формирование ответа
        response = f"Число уникальных поставщиков: {num_sellers}\n\nСписок поставщиков:\n"
        for seller in unique_sellers:
            response += f"- {seller[0]}\n"

        await message.reply(response)

    except sqlite3.Error as e:
        await message.reply(f"Ошибка: {e}")


@dp.message_handler(commands=['salesum'])
async def get_sales_sum(message: types.Message):
    try:
        # Выполнение запроса к базе данных для получения суммы продаж для каждого лекарства
        c.execute("SELECT code_medicine, SUM(price * count) AS total_sales FROM sells GROUP BY code_medicine")
        sales_sums = c.fetchall()

        # Формирование ответа
        response = "Сумма продаж для каждого лекарства:\n"
        for sale in sales_sums:
            response += f"Лекарство: {sale[0]}, Сумма продаж: {sale[1]}\n"

        await message.reply(response)

    except sqlite3.Error as e:
        await message.reply(f"Ошибка: {e}")


@dp.message_handler(commands=['dates'])
async def get_dates(message: types.Message):
    try:
        # Выполнение запроса к базе данных для получения самой первой и последней даты продажи
        c.execute("SELECT MIN(date_sell) AS first_date, MAX(date_sell) AS last_date FROM sells")
        dates = c.fetchall()

        # Формирование ответа
        response = f"Первая дата продажи: {dates[0][0]}\n"
        response += f"Последняя дата продажи: {dates[0][1]}\n"

        await message.reply(response)

    except sqlite3.Error as e:
        await message.reply(f"Ошибка: {e}")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp)