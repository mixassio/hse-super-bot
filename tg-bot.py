import os
from os.path import join
import logging
import re
import redis
import random
from quest_loader import load_questions
from weaver import weaver, check_weaver
from rates import rates, check_rates
from state_val import CHOOSING, CHOOSING_REQ, CHECK_ANSWER, CHECK_WEAVER, CHECK_RATES
from dotenv import load_dotenv
from functools import partial
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

logger = logging.getLogger(__file__)



def help(bot, update):
    reply_markup = ReplyKeyboardRemove()
    bot.send_message(chat_id=update.message.chat_id, text="Hi", reply_markup=reply_markup)


def start(bot, update):
    custom_keyboard = [['Погода', 'Курс валюты'], ['Викторина', 'Поболтать']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, 
                     text="Привет! Выбери что-нибудь", 
                     reply_markup=reply_markup)
    return CHOOSING


def victorina(r, bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет', 'Надоело']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, 
                     text="Поиграем? Нажми новый вопрос", 
                     reply_markup=reply_markup)
    return CHOOSING_REQ


def handle_new_question_request(questions, r, bot, update):
    chat_id = update.message.chat_id
    number_q = random.randrange(0, len(questions) - 1)
    bot.send_message(chat_id=chat_id, text=questions[number_q]['question'])
    answer = questions[number_q]['answer']
    r.set(f'tg-{chat_id}', answer)
    return CHECK_ANSWER


def handle_solution_attempt(r, bot, update):
    chat_id = update.message.chat_id
    answer = r.get(f'tg-{chat_id}')
    if update.message.text == answer:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        bot.send_message(chat_id=chat_id, text=message)
        return CHOOSING_REQ
    else:
        message = f'Неправильно… Попробуешь ещё раз? {answer}'
        bot.send_message(chat_id=chat_id, text=message)
        return CHECK_ANSWER


def handle_show_answer(questions, r, bot, update):
    chat_id = update.message.chat_id
    answer = r.get(f'tg-{chat_id}')
    bot.send_message(chat_id=chat_id, text=answer)
    number_q = random.randrange(0, len(questions) - 1)
    bot.send_message(chat_id=chat_id, text=questions[number_q]['question'])
    answer = questions[number_q]['answer']
    r.set(f'tg-{chat_id}', answer)
    return CHECK_ANSWER



def talking(r, bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text='Привет-привет')
    return CHECK_ANSWER


def done_handler(bot, update):
    return ConversationHandler.END


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    load_dotenv()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
    token_telegram_bot = os.getenv('TG_BOT_TOKEN')
    token_currency = os.getenv('CURRENCY_TOKEN')
    redis_url = os.getenv('REDIS_URL')
    redis_passw = os.getenv('REDIS_PASSW')
    redis_port = os.getenv('REDIS_PORT')
    project_id = os.getenv('GOOGLE_CLOUD_PROGECT')
    r = redis.Redis(
        host=redis_url,
        port=redis_port,
        password=redis_passw,
        decode_responses=True,
        charset="utf-8")
    updater = Updater(token_telegram_bot)
    questions = load_questions("questions")
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],

            states={
                CHOOSING: [
                  RegexHandler('^Погода$', partial(weaver, r)),
                  RegexHandler('^Курс валюты$', partial(rates, r)),
                  RegexHandler('^Викторина$', partial(victorina, r)),
                  RegexHandler('^Поболтать$', partial(talking, r)),
                  ],
                CHECK_WEAVER: [
                  RegexHandler('^Нет$', start),
                  MessageHandler(Filters.text, partial(check_weaver, project_id, r))
                  ],
                CHECK_RATES: [
                  RegexHandler('^Нет$', start),
                  MessageHandler(Filters.text, partial(check_rates, token_currency, project_id, r))
                ],
                CHOOSING_REQ: [
                  RegexHandler('^Надоело$', start),
                  RegexHandler('^Новый вопрос$', partial(handle_new_question_request, questions, r))
                  ],
                CHECK_ANSWER: [
                  RegexHandler('^Надоело$', start),
                  RegexHandler('^Сдаться$', partial(handle_show_answer, questions, r)),
                  MessageHandler(Filters.text, partial(handle_solution_attempt, r)),
                  ],

            },

            fallbacks=[RegexHandler('^Done$', done_handler)]
        )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error_handler)


    updater.start_polling()
    updater.idle()

    


if __name__ == '__main__':
    main()
