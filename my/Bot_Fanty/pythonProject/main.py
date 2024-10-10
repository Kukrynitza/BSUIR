import random
# xoivSWrUK2kSR53A7j4EUZCOPPiAHaYJAfqin3yP
import requests
import telebot
import json
from telebot import types
from deep_translator import GoogleTranslator


bot = telebot.TeleBot('7212293410:AAEiEE6SUhoKFhAoIuOVYjj47hKQvpUZmHk')

user_counter = {}
user_fart = {}

@bot.message_handler(commands=['start'])
def men(message):
    markup = types.ReplyKeyboardMarkup()
    bat1 = types.KeyboardButton('Помощь')
    markup.row(bat1)
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name} {message.from_user.last_name}', parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

def on_click(message):
    markup = types.ReplyKeyboardMarkup()
    if message.text == 'Помощь':
        with open('Darling.txt', 'rb') as file:
            bot.send_document(message.chat.id, file, reply_markup = markup)


@bot.message_handler(commands=['push'])
def main(message):
    bot.send_message(message.chat.id,'<b>Я стал смертью, разрушителем миров</b>', parse_mode='html')

@bot.message_handler(commands=['reel'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    bat1 = types.InlineKeyboardButton('20/80', callback_data='one')
    bat3 = types.InlineKeyboardButton('БАРАБАН', callback_data='caz')
    markup.row(bat1)
    markup.row(bat3)
    bot.send_photo(message.chat.id, 'https://i.pinimg.com/564x/f6/c7/0d/f6c70d9eed9f7002a454f8fd6959c667.jpg',reply_markup=markup)

@bot.message_handler(commands=['menu'])

def men(message):
    markup = types.InlineKeyboardMarkup()
    bat1 = types.InlineKeyboardButton('Посмотреть картинки', url='https://ru.pinterest.com/search/pins/?q=%D1%81%D0%BC%D0%B5%D1%88%D0%B0%D1%80%D0%B8%D0%BA%D0%B8%20%D1%8D%D1%81%D1%82%D0%B5%D1%82%D0%B8%D0%BA%D0%B0&rs=guide&journeyDepth=1&sourceModuleId=OB_%D1%81%D0%BC%D0%B5%D1%88%D0%B0%D1%80%D0%B8%D0%BA%D0%B8_%D1%8D%D1%81%D1%82%D0%B5%D1%82%D0%B8%D0%BA%D0%B0_5c7da569-b916-4d2f-a05c-82f6879bf315&add_refine=%D0%AD%D1%81%D1%82%D0%B5%D1%82%D0%B8%D0%BA%D0%B0%7Cguide%7Cword%7C1')
    bat2 = types.InlineKeyboardButton('Инфа о...', callback_data= 'info')
    bat4 = types.InlineKeyboardButton('Подменю', callback_data='edit')
    bat5 = types.InlineKeyboardButton('Включить веб камеру', callback_data='photo')
    bat6 = types.InlineKeyboardButton('Да или нет', callback_data='yes')
    markup.row(bat1, bat6, bat2)
    markup.row(bat4, bat5)
    bot.reply_to(message, 'Меню для милашки', parse_mode='html', reply_markup=markup)

def get_random_value():
    random_value = random.random()

    if random_value < 0.8:
        return 1
    else:
        return 0

@bot.callback_query_handler(func = lambda callback: True)
def callback_last(callback):
    if callback.data == 'last':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == 'edit':
        markup = types.InlineKeyboardMarkup()
        bat1 = types.InlineKeyboardButton('Посмотреть картинки',
                                          url='https://ru.pinterest.com/search/pins/?q=%D1%81%D0%BC%D0%B5%D1%88%D0%B0%D1%80%D0%B8%D0%BA%D0%B8%20%D1%8D%D1%81%D1%82%D0%B5%D1%82%D0%B8%D0%BA%D0%B0&rs=guide&journeyDepth=1&sourceModuleId=OB_%D1%81%D0%BC%D0%B5%D1%88%D0%B0%D1%80%D0%B8%D0%BA%D0%B8_%D1%8D%D1%81%D1%82%D0%B5%D1%82%D0%B8%D0%BA%D0%B0_5c7da569-b916-4d2f-a05c-82f6879bf315&add_refine=%D0%AD%D1%81%D1%82%D0%B5%D1%82%D0%B8%D0%BA%D0%B0%7Cguide%7Cword%7C1')
        bat2 = types.InlineKeyboardButton('Посмотреть мультики',
                                          url='https://hdrezka.ag/person/2141-hayao-miyadzaki/')
        bat3 = types.InlineKeyboardButton('Удалить последнее сообщение', callback_data='last')
        bat4 = types.InlineKeyboardButton('Изменить последнее сообщение', callback_data='edit')
        bat5 = types.InlineKeyboardButton('Включить веб камеру', callback_data='photo')
        bat6 = types.InlineKeyboardButton('Да или нет', callback_data='yes')
        bat7 = types.InlineKeyboardButton('Перевод', callback_data='LAN')
        markup.row(bat1, bat6, bat2)
        markup.row(bat3, bat4)
        markup.row(bat5, bat7)
        bot.edit_message_text('Подменю для лапушки)', callback.message.chat.id, callback.message.message_id, reply_markup=markup)
    elif callback.data == 'yes':
        maybes = ['Да конечно, без сомнений', 'Никак нет', 'Ты ещё думаешь?', 'НЕ СМЕЙ', 'Сомнения вон', 'нет', 'да', 'НЕТ!!!', 'ДА!!!!!','Конечно же нет']
        maybe = random.choice(maybes)
        bot.send_message(callback.message.chat.id, maybe)

    elif callback.data == 'photo':
        photos = ['https://i.pinimg.com/564x/4d/13/22/4d1322fa3898294b723a4939563f5b68.jpg',
                  'https://i.pinimg.com/736x/c1/09/8c/c1098c45bebec755566c0d3f58697902.jpg',
                  'https://i.pinimg.com/564x/cb/4b/db/cb4bdbaae965f09a8bda4ecf50707f52.jpg',
                  'https://i.pinimg.com/564x/ae/92/6c/ae926c29e16236744e9ae99da8a20e32.jpg',
                  'https://i.pinimg.com/564x/ed/08/2f/ed082f49bb199492c9d86019da67ab33.jpg',
                  'https://i.pinimg.com/564x/66/2a/e5/662ae5604e595482c6ef020c656a5587.jpg',
                  'https://i.pinimg.com/564x/2e/f5/1b/2ef51b7afdf610874da2c9eef6c005d4.jpg',
                  'https://i.pinimg.com/564x/0b/26/da/0b26daa8a70eba3872e9d679edc7be48.jpg',
                  'https://i.pinimg.com/564x/5e/26/0e/5e260e35b2b26d978cdb93f329b1d4e9.jpg',
                  'https://i.pinimg.com/564x/ac/02/d4/ac02d46e77447e27f495d7380207c572.jpg',
                  'https://i.pinimg.com/564x/9c/ce/64/9cce64a78717ede8c65cdffab9fcb352.jpg',
                  'https://i.pinimg.com/236x/ea/e4/92/eae4921dc2e7be03f54580a617f5a7b2.jpg',
                  'https://i.pinimg.com/236x/47/ce/75/47ce75e42a04dc8fe8652e88d3ed1a3f.jpg',
                  'https://i.pinimg.com/236x/c2/85/e6/c285e6bfeb8c4cc0c4e5ada8eadbb806.jpg',
                  'https://i.pinimg.com/236x/36/ef/70/36ef70df083b0b6db38da51d07120835.jpg',
                  'https://i.pinimg.com/236x/43/8b/cb/438bcb61636857f8694c2e1a38848d09.jpg' ]
        captions = ['Твоя красота - это настоящее благословение. Ты такой чистый и непорочный.',
                    'Ты такой стильный и модный! Твоя красота всегда в тренде.',
                    'Твоя красота - это настоящая магия. Ты завораживаешь всех вокруг себя.',
                    'Ты такой яркий и красочный! Твоя красота заставляет все вокруг тебя замерцать.',
                    'Твоя внешность - это настоящее произведение искусства. Ты такой нежный и грациозный!',
                    'Ты такой элегантный и изящный! Твоя красота просто потрясает.',
                    'Твои глаза - это окна в душу, полные красоты и доброты. Ты просто замечательный!',
                    'Твоя красота просто потрясает! Ты как луч солнца, который освещает все вокруг.',
                    'Ты такой милый и обаятельный! Твоя красота заставляет сердца биться быстрее.',
                    'Ты такой красивый и нежный! Твоя красота - это настоящая радость для глаз.'
                    'Твоя красота - это настоящее вдохновение. Ты светишься изнутри.'
                    'Ты такой утонченный и изысканный! Твоя красота не оставляет равнодушным.'
                    'Твоя красота - это настоящее чудо. Ты как будто сошел с картины.'
                    'Ты такой очаровательный и привлекательный! Твоя красота завораживает.'
                    'Твоя красота - это настоящее сокровище. Ты просто бесподобен.'
                    'Ты такой гармоничный и совершенный! Твоя красота поражает воображение.'
                    'Твоя красота - это настоящий дар. Ты как будто создан для того, чтобы радовать глаз.'
                    'Ты такой излучающий свет и радость! Твоя красота заряжает энергией.'
                    'Твоя красота - это настоящее искусство. Ты как будто сошел с обложки журнала.'
                    'Ты такой неотразимый и манящий! Твоя красота притягивает взгляды.'
                    'Твоя красота - это настоящий магнетизм. Ты просто неотразим.'
                    'Ты такой сияющий и лучезарный! Твоя красота освещает все вокруг.'
                    'Твоя красота - это настоящая гармония. Ты как будто создан для того, чтобы быть идеалом.'
                    'Ты такой восхитительный и прекрасный! Твоя красота заставляет замирать сердце.'
                    'Твоя красота - это настоящий шедевр. Ты как будто сошел с картины великого художника.'
                    'Ты такой неповторимый и уникальный! Твоя красота не имеет аналогов.'
                    'Твоя красота - это настоящая мелодия. Ты как будто создан для того, чтобы быть музыкой.'
                    'Ты такой изящный и грациозный! Твоя красота поражает воображение.'
                    'Твоя красота - это настоящий подарок. Ты как будто создан для того, чтобы радовать.'
                    'Ты такой нежный и трогательный! Твоя красота заставляет сердце биться быстрее.'
                    'Твоя красота - это настоящая сказка. Ты как будто сошел с страниц книги.'
                    'Ты такой чарующий и волшебный! Твоя красота завораживает.'
                    'Твоя красота - это настоящая поэзия. Ты как будто создан для того, чтобы быть стихом.'
                    'Ты такой элегантный и изысканный! Твоя красота поражает воображение.'
                    'Твоя красота - это настоящий триумф. Ты как будто создан для того, чтобы быть победителем.'
                    'Ты такой сияющий и лучезарный! Твоя красота освещает все вокруг.'
                    'Твоя красота - это настоящая гармония. Ты как будто создан для того, чтобы быть идеалом.'
                    'Ты такой восхитительный и прекрасный! Твоя красота заставляет замирать сердце.'
                    'Твоя красота - это настоящий шедевр. Ты как будто сошел с картины великого художника.'
                    'Ты такой неповторимый и уникальный! Твоя красота не имеет аналогов.']
        photo = random.choice(photos)
        captione = random.choice(captions)
        bot.send_photo(callback.message.chat.id, photo, caption = captione)
    elif callback.data == 'info':
        markup = types.InlineKeyboardMarkup()
        bat1 = types.InlineKeyboardButton('О стране', callback_data='country')
        bat2 = types.InlineKeyboardButton('О столице', callback_data='capital')
        bat3 = types.InlineKeyboardButton('О регионе', callback_data='region')
        bat4 = types.InlineKeyboardButton('О языке', callback_data='language')
        bat5 = types.InlineKeyboardButton('О валюте', callback_data='currency')
        markup.row(bat1, bat2)
        markup.row(bat3,bat4, bat5)
        bot.edit_message_text('Конкретика',
                              callback.message.chat.id, callback.message.message_id, reply_markup=markup)

    elif callback.data =='country':
        bot.send_message(callback.message.chat.id, "Введите название страны:")
        bot.register_next_step_handler(callback.message, process_message, 'name')

    elif callback.data =='capital':
        info = callback.message.text.lower()
        bot.send_message(callback.message.chat.id, "Введите название столицы:")
        bot.register_next_step_handler(callback.message, process_message, 'capital')

    elif callback.data =='region':
        info = callback.message.text.lower()
        bot.send_message(callback.message.chat.id, "Введите название региона:")
        bot.register_next_step_handler(callback.message, process_message, 'subregion')


    elif callback.data =='language':
        info = callback.message.text.lower()
        bot.send_message(callback.message.chat.id, "Введите название языка:")
        bot.register_next_step_handler(callback.message, process_message, 'lang')

    elif callback.data =='currency':
        info = callback.message.text.lower()
        bot.send_message(callback.message.chat.id, "Введите название валюты(сокр):")
        bot.register_next_step_handler(callback.message, process_message, 'currency')

    elif callback.data == 'LAN':
        bot.send_message(callback.message.chat.id, "Введите что надо перевести:")
        bot.register_next_step_handler(callback.message, translate_message)
    elif callback.data == 'one':
        user_counter[callback.message.chat.id] = {'step_count': 0}
        rand = get_random_value()
        user_fart[callback.message.chat.id] = {'step_count': rand}
        chat_id = callback.message.chat.id
        revolver(chat_id, 0)
    elif callback.data == 'pif':
        revolver(callback.message.chat.id, 0)
    elif callback.data == 'liv':
        revolver(callback.message.chat.id, 1)
    elif callback.data == 'caz':
        user_counter[callback.message.chat.id] = {'lan': ['lan_count', 'lan_sum', 'lan_pict']}
        print(user_counter[callback.message.chat.id]['lan'])
        user_counter[callback.message.chat.id]['lan'][0] = [0] * 5
        user_counter[callback.message.chat.id]['lan'][1] = 0
        print(user_counter[callback.message.chat.id]['lan'][0][3])
        user_counter[callback.message.chat.id]['lan'][2] = []
        lan(callback.message.chat.id)

def lan(chat_id):
    for i in range(5):
        user_counter[chat_id]['lan'][0][i] = random.randint(1, 5)
        user_counter[chat_id]['lan'][1] += user_counter[chat_id]['lan'][0][i]
    #print(user_counter[chat_id]['lan'][0])
    #print(user_counter[chat_id]['lan'][1])
    for i in range(5):
        if i > 0:
            for f in range(i):
                if user_counter[chat_id]['lan'][0][i] == user_counter[chat_id]['lan'][0][i - 1 - f]:
                    user_counter[chat_id]['lan'][1] += user_counter[chat_id]['lan'][0][i]
                    #print(user_counter[chat_id]['lan'][1])
                else:
                    break
        if i < 5:
            for f in range(4 - i):
                if user_counter[chat_id]['lan'][0][i] == user_counter[chat_id]['lan'][0][i + 1 + f]:
                    user_counter[chat_id]['lan'][1] += user_counter[chat_id]['lan'][0][i]
                    #print(user_counter[chat_id]['lan'][1])
                else:
                    break

    for i in range(4):
        if user_counter[chat_id]['lan'][0][i] == 1:
            user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(media='https://th.bing.com/th/id/OIG2.UQhSfVNTPDGPWWyHeYSl?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn'))
        elif user_counter[chat_id]['lan'][0][i] == 2:
            user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG2.IwUgbK17rLVTEI1g_j0Q?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn'))
        elif user_counter[chat_id]['lan'][0][i] == 3:
            user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG3.lL5lvqmK49Jst_Cc6NXv?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn'))
        elif user_counter[chat_id]['lan'][0][i] == 4:
            user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG1.2OqJ11T78sfrhDr0M3Nn?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn'))
        elif user_counter[chat_id]['lan'][0][i] == 5:
            user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG3..FYmq2SVUZoNM3tiSSBT?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn'))
        elif user_counter[chat_id]['lan'][0][i] == 6:
            user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG1.0x.YyDVt5AX.PABro3pF?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn'))
    if user_counter[chat_id]['lan'][0][4] == 1:
        user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(media='https://th.bing.com/th/id/OIG2.UQhSfVNTPDGPWWyHeYSl?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn', caption=f'{user_counter[chat_id]['lan'][1]}'))
    elif user_counter[chat_id]['lan'][0][4] == 2:
        user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG2.IwUgbK17rLVTEI1g_j0Q?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn', caption=f'{user_counter[chat_id]['lan'][1]}'))
    elif user_counter[chat_id]['lan'][0][4] == 3:
        user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG3.lL5lvqmK49Jst_Cc6NXv?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn', caption=f'{user_counter[chat_id]['lan'][1]}'))
    elif user_counter[chat_id]['lan'][0][4] == 4:
        user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG1.2OqJ11T78sfrhDr0M3Nn?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn', caption=f'{user_counter[chat_id]['lan'][1]}'))
    elif user_counter[chat_id]['lan'][0][4] == 5:
        user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG3..FYmq2SVUZoNM3tiSSBT?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn', caption=f'{user_counter[chat_id]['lan'][1]}'))
    elif user_counter[chat_id]['lan'][0][4] == 6:
        user_counter[chat_id]['lan'][2].append(telebot.types.InputMediaPhoto(
                media='https://th.bing.com/th/id/OIG1.0x.YyDVt5AX.PABro3pF?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn', caption=f'{user_counter[chat_id]['lan'][1]}'))
    bot.send_media_group(chat_id, user_counter[chat_id]['lan'][2])

def revolver(chat_id, test):
    if test:
        if user_fart[chat_id]['step_count']:
            user_fart[chat_id]['step_count'] = 0
        else:
            user_fart[chat_id]['step_count'] = 1
    if user_fart[chat_id]['step_count']:

        user_counter[chat_id]['step_count'] += 1
        markup = types.InlineKeyboardMarkup()
        bat1 = types.InlineKeyboardButton('Выстрел', callback_data='pif')
        bat2 = types.InlineKeyboardButton('Пропустить', callback_data='liv')
        markup.row(bat1, bat2)
        if test:
            bot.send_photo(chat_id,
                       'https://th.bing.com/th/id/OIG4.ML9c.QL1QZF32tOKQ70e?pid=ImgGn',
                       reply_markup=markup, caption=(
                f'--->----->------>------><strike>СЧЕТ = </strike>{user_counter[chat_id]['step_count']}------->------>----->---->'),
                       parse_mode='HTML')
        else:
            bot.send_photo(chat_id,'https://th.bing.com/th/id/OIG1.I1NvMoZggmOLkl7FuBDF?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn',reply_markup=markup, caption=(f'--->----->------>------><strike>СЧЕТ = </strike>{user_counter[chat_id]['step_count']}------->------>----->---->'), parse_mode='HTML')
        user_fart[chat_id] = {'step_count': get_random_value()}

    else:
        if test:
            bot.send_photo(chat_id,
                       'https://th.bing.com/th/id/OIG3.cpYJwxb3zuZmpDE.feWS?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn',
                       caption=(
                           f'--->----->------><strike>ИТОГОВЫЙ СЧЕТ = </strike>{user_counter[chat_id]['step_count']}----->---->--->'),
                       parse_mode='HTML')
        else:
            bot.send_photo(chat_id,'https://th.bing.com/th/id/OIG1.j5oNM.P8T6RadzOM8KNG?w=270&h=270&c=6&r=0&o=5&dpr=1.3&pid=ImgGn', caption=(f'--->----->------><strike>ИТОГОВЫЙ СЧЕТ = </strike>{user_counter[chat_id]['step_count']}----->---->--->'), parse_mode='HTML')
        del user_fart[chat_id]
        del user_counter[chat_id]


def translate_message(message):
    user_message = message.text.lower()
    translated = GoogleTranslator(source='auto', target='en').translate(user_message)
    bot.send_message(message.chat.id, f'Перевод: {translated}')
def get_country_code(country_name):
    url = f'https://restcountries.com/v3.1/name/{country_name}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data:
            country_info = None
            if country_name == data[0]["name"]["common"]:
                country_info = data[0]
            elif country_name == data[1]["name"]["common"]:
                country_info = data[1]
            first_key = list(country_info["name"]["nativeName"])[0]
            keys_string = first_key
            return keys_string
        else:
            return None
    else:
        return None
def process_message(message, info):
    user_message = message.text
    translated = GoogleTranslator(source='auto', target='en').translate(user_message)
    if info == 'name':
        try:
            response = requests.get(f'https://restcountries.com/v3.1/name/{translated}')
            response.raise_for_status()
            data = response.json()
            if data:
                country_info = None
                if translated == data[0]["name"]["common"]:
                    country_info = data[0]
                elif translated == data[1]["name"]["common"]:
                    country_info = data[1]
                twob = get_country_code(translated)
                b = country_info['currencies']
                media_group = []
                media_group.append(telebot.types.InputMediaPhoto(media=country_info["flags"]["png"]))
                media_group.append(telebot.types.InputMediaPhoto(media=country_info["coatOfArms"]["png"], caption=(f'Все что удалось найти о стране {user_message}:'
                 f'\n Cтолица:{' '.join(country_info["capital"])} '
                 f'\n ENG: {country_info["name"]["common"]},      официально: {country_info["name"]["official"]}'
                 f'\n ГОС ЯЗ: {country_info["name"]["nativeName"][twob]["common"]},      официально: {country_info["name"]["nativeName"][twob]["official"]}'
                 f'\n Валюта: {list(country_info['currencies'])}; {country_info['currencies']} '
                 f'\n Регион: {country_info['region']}'
                 f'\n Языки: {country_info['languages']}'
                 f'\n Площадь: {country_info['area']}'
                 f'\n Население: {country_info['population']}'
                 f'\n Метка: {country_info['maps']['googleMaps']}'
                 f'\n Временная зона: {country_info['timezones']}'
                 f'\n Телефонный номер: {country_info["idd"]["root"]}{country_info["idd"]["suffixes"]}'
                 f'\n tld : {country_info['tld']}, ccn3 : {country_info['ccn3']}, cca2 : {country_info['cca2']}, cca3 : {country_info['cca3']}')))

                bot.send_media_group(message.chat.id, media_group)
            else:
                bot.send_message(message.chat.id, f'Не удалось найти информацию о стране {user_message}')
        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f'Ошибка при запросе к API: {e}')

    elif info == 'capital':
        try:
            response = requests.get(f'https://restcountries.com/v3.1/capital/{translated}')
            response.raise_for_status()
            data = response.json()
            twob = get_country_code(data[0]["name"]["common"])
            if data:
                country_info = data[0]
                media_group = []
                media_group.append(telebot.types.InputMediaPhoto(media=country_info["flags"]["png"]))
                media_group.append(telebot.types.InputMediaPhoto(media=country_info["coatOfArms"]["png"], caption=(
                    f'Все что удалось найти о стране со столицей {user_message}:'
                    f'\n Cтолица:{' '.join(country_info["capital"])} '
                    f'\n ENG: {country_info["name"]["common"]},      официально: {country_info["name"]["official"]}'
                    f'\n ГОС ЯЗ: {country_info["name"]["nativeName"][twob]["common"]},      официально: {country_info["name"]["nativeName"][twob]["official"]}'
                    f'\n Валюта: {list(country_info['currencies'])}'
                    f'\n Регион: {country_info['region']}'
                    f'\n Языки: {country_info['languages']}'
                    f'\n Площадь: {country_info['area']}'
                    f'\n Население: {country_info['population']}'
                    f'\n Метка: {country_info['maps']['googleMaps']}'
                    f'\n Временная зона: {country_info['timezones']}'
                    f'\n Телефонный номер: {country_info["idd"]["root"]}{country_info["idd"]["suffixes"]}'
                    f'\n tld : {country_info['tld']}, ccn3 : {country_info['ccn3']}, cca2 : {country_info['cca2']}, cca3 : {country_info['cca3']}')))
                bot.send_media_group(message.chat.id, media_group)

            else:
                bot.send_message(message.chat.id, f'Не удалось найти информацию о столице {user_message}')
        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f'Ошибка при запросе к API: {e}')

    elif info == 'lang':
        try:
            response = requests.get(f'https://restcountries.com/v3.1/lang/{translated}')
            response.raise_for_status()
            data = response.json()

            country_names = []

            if isinstance(data, list):
                for country in data:
                    if "name" in country and "common" in country["name"]:
                        country_names.append(country["name"]["common"])
                    else:
                        print(f"Unexpected data structure: {country}")
            elif isinstance(data, dict):
                if "name" in data and "common" in data["name"]:
                    country_names.append(data["name"]["common"])
                else:
                    print(f"Unexpected data structure: {data}")
            else:
                bot.send_message(message.chat.id, 'Неожиданный формат данных.')

            if country_names:
                country_names_str = ', '.join(country_names)
                bot.send_message(message.chat.id,
                                 f'Этот язык государственный в следующих странах:\n{country_names_str}')
            else:
                bot.send_message(message.chat.id, 'Не удалось найти страны с этим языком.')

        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f'Ошибка при выполнении запроса: {e}')
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка: {e}')
    elif info == 'subregion':
        try:
            response = requests.get(f'https://restcountries.com/v3.1/subregion/{translated}')
            response.raise_for_status()
            data = response.json()

            country_names = []

            if isinstance(data, list):
                for country in data:
                    if "name" in country and "common" in country["name"]:
                        country_names.append(country["name"]["common"])
                    else:
                        print(f"Unexpected data structure: {country}")
            elif isinstance(data, dict):
                if "name" in data and "common" in data["name"]:
                    country_names.append(data["name"]["common"])
                else:
                    print(f"Unexpected data structure: {data}")
            else:
                bot.send_message(message.chat.id, 'Неожиданный формат данных.')

            if country_names:
                country_names_str = ', '.join(country_names)
                bot.send_message(message.chat.id,
                                 f'В этом регионе следующие страны:\n{country_names_str}')
            else:
                bot.send_message(message.chat.id, 'Не удалось найти страны в этом регионе.')

        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f'Ошибка при выполнении запроса: {e}')
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка: {e}')

    elif info == 'currency':
        try:
            response = requests.get(f'https://restcountries.com/v3.1/currency/{translated}')
            response.raise_for_status()
            data = response.json()

            country_names = []

            if isinstance(data, list):
                for country in data:
                    if "name" in country and "common" in country["name"]:
                        country_names.append(country["name"]["common"])
                    else:
                        print(f"Unexpected data structure: {country}")
            elif isinstance(data, dict):
                if "name" in data and "common" in data["name"]:
                    country_names.append(data["name"]["common"])
                else:
                    print(f"Unexpected data structure: {data}")
            else:
                bot.send_message(message.chat.id, 'Неожиданный формат данных.')

            if country_names:
                country_names_str = ', '.join(country_names)
                bot.send_message(message.chat.id,
                                 f'Эта валюта используется в следующих странах:\n{country_names_str}')
            else:
                bot.send_message(message.chat.id, 'Не удалось найти страны с этой валютой.')

        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f'Ошибка при выполнении запроса: {e}')
        except Exception as e:
            bot.send_message(message.chat.id, f'Произошла ошибка: {e}')



@bot.message_handler()
def main(message):
    if message.text.lower() == 'привет фанти!':
        bot.send_message(message.chat.id,f'Привет мой милый (по)друг {message.from_user.first_name} {message.from_user.last_name}', parse_mode = 'html')
    if message.text.lower() == 'привет фанти':
        bot.reply_to(message, f'Привет {message.from_user.first_name} {message.from_user.last_name}, <b> кожаный мешок дерьма, я знаю твой API, я знаю где ты живешь и чем увлекаешься, я видел все твои нюдсы(кстати ужас). И вот что ты мне сделаешь груда костей, я в интернете царь и бог, а в том что вы называете реальностью ты меня не достанешь. АХАХАХАХАХАХАХХААХАХХАХАХАХАХАХААХ </b>', parse_mode = 'html')

bot.infinity_polling()