import requests
from telegram import ReplyKeyboardRemove
from state_val import CHECK_RATES
from dialog_flow_lib import detect_intent_texts


def get_rates(token_currency, currency):
    params =  {
      'get': 'rates',
      'key': token_currency,
      'q': '',
      'pairs': f'{currency}RUB'
      }
    url = 'https://currate.ru/api/'
    response = requests.get(url, params=params)
    response.raise_for_status()
    res = response.json()
    return res['data'][f'{currency}RUB']


def rates(r, bot, update):
    reply_markup = ReplyKeyboardRemove()
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text='введите валюту', reply_markup=reply_markup)
    return CHECK_RATES



def check_rates(token_currency, project_id, r, bot, update):
    chat_id = update.message.chat_id
    mes = update.message.text

    user = update.message.from_user
    session_id = f'tg-{user["id"]}'
    currency = detect_intent_texts(project_id, session_id, [update.message.text], 'ru-RU')
    if currency.intent.display_name == 'choose rate':
        rate = get_rates(token_currency, currency.fulfillment_text)
        answer = f'1 рубль стоит {rate} {currency.fulfillment_text}'
        bot.send_message(chat_id=chat_id, text=answer)
        bot.send_message(chat_id=chat_id, text='Посмотрим другую валюту?? Если нет - напишите "Нет")')
        return CHECK_RATES
    bot.send_message(chat_id=chat_id, text='Не могу найти такую валюту.')
    return CHECK_RATES
