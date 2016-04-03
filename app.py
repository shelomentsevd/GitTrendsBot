# Author: Dmitriy Shelomentsev (shelomentsev@protonmail.ch)
# -*- coding: utf-8 -*-
from telegram.ext import Updater
from telegram import Emoji, ParseMode
import gittrends as git
import logging
import ConfigParser as cp
import sys
import re

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


class GitTrendsBot:
    __about_text = (
        'Shows GitHub trending repositories from: http://github.com/trending\n'
        'Written \'Just for Fun\' by [ShelomentsevD](https://github.com/shelomentsevd)\n'
        '[Source code here](https://github.com/shelomentsevd/GitTrendsBot)'
    )

    __help_text = (
        'Supports commands:\n'
        '/today [language] - shows today trending repositories written in [language]\n'
        '/week [language] - same as /today\n'
        '/month [language] - same as previous two\n'
        '/help - this text\n'
        '/about - bot information\n'
    )

    def __init__(self, telegram, botan=None):
        if botan:
            from telegram.utils.botan import Botan
            self.__botan = Botan(botan)

        self.__updater = Updater(telegram)
        dp = self.__updater.dispatcher
        dp.addTelegramCommandHandler('start', self.__start)
        dp.addTelegramCommandHandler('help', self.__help)
        dp.addTelegramCommandHandler('about', self.__about)
        dp.addTelegramCommandHandler('today', self.__today)
        dp.addTelegramCommandHandler('week', self.__week)
        dp.addTelegramCommandHandler('month', self.__month)
        
        dp.addUnknownTelegramCommandHandler(self.__unknow)

        dp.addErrorHandler(self.__error)

    def __logger_wrap(self, message, command):
        if self.__botan:
            self.__botan.track(
                message=message,
                event_name=command
            )
        user = message.from_user
        logger.info(u'%s from %s @%s %s' % (message.text,
                                            user.first_name,
                                            user.username,
                                            user.last_name))

    def __trends_wrap(self, period, language=''):
        trends = list()
        description = (
            '*Name*: [%s](http://github.com/%s)\n'
            '*Description*: %s\n'
            '*Language*: %s\n'
            '%s')
        
        try:
            trends = git.get_trends(period, language)
        except Exception as e:
            logger.exception(e)

        repos = [description % (repo['name'],
                                repo['name'],
                                repo['description'],
                                repo['language'],
                                re.sub(u'stars',
                                Emoji.WHITE_MEDIUM_STAR.decode('utf-8'),
                                repo['stars'])) for repo in trends]

        return '\n\n'.join(repos)

    def __start(self, bot, update, args):
        self.__logger_wrap(update.message, 'start')
        bot.sendMessage(update.message.chat_id, text=self.__help_text)

    def __help(self, bot, update):
        self.__logger_wrap(update.message, 'help')
        bot.sendMessage(update.message.chat_id, text=self.__help_text)

    def __about(self, bot, update):
        self.__logger_wrap(update.message, 'about')
        bot.sendMessage(update.message.chat_id, text=self.__about_text, parse_mode=ParseMode.MARKDOWN)

    def __today(self, bot, update, args):
        self.__logger_wrap(update.message, 'today')
        result = ''
        if args:
            result = self.__trends_wrap('daily', args[0])
        else:
            result = self.__trends_wrap('daily')
        bot.sendMessage(update.message.chat_id, text=result, parse_mode=ParseMode.MARKDOWN)

    def __week(self, bot, update, args):
        self.__logger_wrap(update.message, 'week')
        result = ''
        if args:
            result = self.__trends_wrap('weekly', args[0])
        else:
            result = self.__trends_wrap('weekly')
        bot.sendMessage(update.message.chat_id, text=result, parse_mode=ParseMode.MARKDOWN)

    def __month(self, bot, update, args):
        self.__logger_wrap(update.message, 'month')
        result = ''
        if args:
            result = self.__trends_wrap('monthly', args[0])
        else:
            result = self.__trends_wrap('monthly')
        bot.sendMessage(update.message.chat_id, text=result, parse_mode=ParseMode.MARKDOWN)

    def __unknow(self, bot, update):
        self.__logger_wrap(update.message, 'unknow')

    def __error(self, bot, update, error):
        self.__logger_wrap(update.message, 'error')
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def idle(self):
        self.__updater.start_polling()
        self.__updater.idle()

def main():
    try:
        configuration = cp.ConfigParser()
        configuration.read('configuration.ini')
        bot_token = configuration.get('bot', 'token')
        botan_token = configuration.get('botan', 'token')
    except Exception as e:
        logger.exception(e)
        sys.exit()       

    if not bot_token:
        logger.error('Bot token is empty')
        sys.exit()

    bot = GitTrendsBot(bot_token, botan_token)
    bot.idle()


if __name__ == '__main__':
    main()