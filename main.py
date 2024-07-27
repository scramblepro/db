import random
import psycopg2
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

#beta-version
print('start tg bot...')

conn = psycopg2.connect(
    dbname="english_bot",
    user="postgres",
    password="*********",
    host="localhost",
    client_encoding="utf8"
)
cursor = conn.cursor()

state_storage = StateMemoryStorage()
token_bot = '********************************'
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


# Обработчик команды /start и /cards
@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    username = message.from_user.id #if message.from_user.id else "Unknown"

    # Добавление нового пользователя в базу данных
    cursor.execute("""
        INSERT INTO users (chat_id, username) 
        VALUES (%s, %s)
        ON CONFLICT (chat_id) DO NOTHING;
    """, (cid, username))
    conn.commit()

    # Получение user_id для нового пользователя
    cursor.execute("SELECT user_id FROM users WHERE chat_id = %s;", (cid,))
    user_id = cursor.fetchone()[0]

    # Добавление всех слов из таблицы words в user_words для нового пользователя
    cursor.execute("""
        INSERT INTO user_words (user_id, word_id)
        SELECT %s, word_id FROM words
        ON CONFLICT DO NOTHING;
    """, (user_id,))
    conn.commit()

    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, "Hello, stranger, let's study English...")

    markup = types.ReplyKeyboardMarkup(row_width=2)
    buttons.clear()

    # Получаем случайное слово для данного пользователя из БД
    cursor.execute("""
        SELECT w.word, w.translation 
        FROM words w
        JOIN user_words uw ON w.word_id = uw.word_id
        JOIN users u ON uw.user_id = u.user_id
        WHERE u.chat_id = %s
        ORDER BY RANDOM()
        LIMIT 1;
    """, (cid,))
    result = cursor.fetchone()

    if not result:
        bot.send_message(cid, "Нет слов для изучения. Добавьте новые слова.")
        return

    target_word, translate = result
    target_word_btn = types.KeyboardButton(target_word)  # показываем слово на английском
    buttons.append(target_word_btn)

    # Получаем три случайных неправильных перевода
    cursor.execute("""
        SELECT word 
        FROM words 
        WHERE word != %s 
        ORDER BY RANDOM() 
        LIMIT 3;
    """, (target_word,))
    others = [row[0] for row in cursor.fetchall()]
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)

    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"  # показываем перевод для выбора правильного слова
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


# Обработчик команды Дальше
@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


# Обработчик команды Удалить слово
@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        cursor.execute("""
            DELETE FROM user_words 
            WHERE user_id = (SELECT user_id FROM users WHERE chat_id = %s)
            AND word_id = (SELECT word_id FROM words WHERE word = %s);
        """, (message.from_user.id, target_word))
        conn.commit()
        bot.send_message(message.chat.id, f"Слово '{target_word}' удалено.")
        # Обновление данных после удаления слова
    bot.delete_state(message.from_user.id, message.chat.id)
    create_cards(message)


# Обработчик команды Добавить слово
@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    bot.send_message(message.chat.id, "Введите новое слово и его перевод в формате: слово перевод")
    bot.set_state(message.from_user.id, MyStates.translate_word, message.chat.id)


# Обработчик состояния добавления слова
@bot.message_handler(state=MyStates.translate_word)
def save_new_word(message):
    try:
        word, translation = message.text.split()
        user_id = message.from_user.id

        cursor.execute("INSERT INTO words (word, translation, example) VALUES (%s, %s, %s) RETURNING word_id;",
                       (word, translation, "No example available."))
        word_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO user_words (user_id, word_id)
            VALUES ((SELECT user_id FROM users WHERE chat_id = %s), %s);
        """, (user_id, word_id))

        cursor.execute("UPDATE users SET word_count = word_count + 1 WHERE chat_id = %s;", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id,
                         f"Слово '{word}' добавлено. Теперь вы изучаете {get_word_count(user_id)} слов.")
        bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id,
                         "Произошла ошибка. Убедитесь, что вы вводите слово и перевод в правильном формате: слово "
                         "перевод")


# Получение количества слов у пользователя
def get_word_count(user_id):
    cursor.execute("SELECT word_count FROM users WHERE chat_id = %s;", (user_id,))
    return cursor.fetchone()[0]


# Обработчик всех остальных сообщений (проверка правильного ответа)
@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if message.text == target_word:
            bot.send_message(message.chat.id, "Правильно!")
        else:
            bot.send_message(message.chat.id, "Неправильно, попробуйте снова.")
    next_cards(message)


# Добавление кастомных фильтров и запуск бота
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)
