import requests
from telegram import ReplyKeyboardRemove
from state_val import CHECK_WEAVER
from dialog_flow_lib import detect_intent_texts


def get_weather(location):
    params =  {
      'n': '',
      'T': '',
      'q': '',
      'm': '',
      'lang': 'ru'
      }
    url_template = 'http://wttr.in/{}'
    url = url_template.format(location)
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.text



def weaver(r, bot, update):
    reply_markup = ReplyKeyboardRemove()
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text='введите город', reply_markup=reply_markup)
    return CHECK_WEAVER


def check_weaver(project_id, r, bot, update):
    chat_id = update.message.chat_id
    mes = update.message.text

    user = update.message.from_user
    session_id = f'tg-{user["id"]}'
    location = detect_intent_texts(project_id, session_id, [update.message.text], 'ru-RU')
    if location.intent.display_name == 'choose city':
        answer = get_weather(location.fulfillment_text)
        bot.send_message(chat_id=chat_id, text=answer)
        bot.send_message(chat_id=chat_id, text='Посмотрим другой город? Если нет - напишите "Нет")')
        return CHECK_WEAVER
    bot.send_message(chat_id=chat_id, text='Не могу найти такой город. Введите город на русском языке')
    return CHECK_WEAVER
