from telegram.ext import Updater
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from autocorrect import spell
import logging
import re
import datetime
import telegram


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


symbols = list('?!.@#$%()+-*/"\':;<>=^~\{\}[]_`\n')

def ignore_symbols(sentence):
    for symbol in symbols:
        sentence = sentence.replace(symbol, '')
    return sentence

def is_alpha(word):
    try:
        return ignore_symbols(word).replace(' ', '').encode('ascii').isalpha()
    except UnicodeEncodeError:
        return False

def start(bot, update):
    message = """If you think you type incorrect words.
Just type "fuck"."""
    bot.send_message(chat_id=update.message.chat_id, text=message)

def spell_correct(bot, update, log={}):
    user = update.message.from_user.username
    message = update.message.text

    if message == 'fuck' and log.get(user, None) is not None:
        logger.info('Sent for {}'.format(user))
        log[user]['message'].reply_text(
            log[user]['reply'],
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        del log[user]
        return

    if message and is_alpha(message):
        for symbol in symbols:
            message = message.replace(symbol, ' {} '.format(symbol))

        spelled = []
        for word in message.split(' '):
            if word in symbols:
                spelled.append(word)
            elif len(word) > 1:
                spelled.append(spell(word))
            elif word:
                spelled.append(word)
        spelled = ' '.join(spelled)

        if spelled != message:
            logger.info('Saved "{}" from {}'.format(spelled, user))
            reply = 'Maybe {}\'s meaning is\n```\n{}\n```'.format(user, spelled)
            log[user] = {
                'message': update.message,
                'reply': reply
            }

def main():
    updater = Updater('SECRET_TOKEN')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(RegexHandler(u'(?i)(?:[\w ]+|fuck)'.format(re.escape(''.join(symbols))), spell_correct))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
