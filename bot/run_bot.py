'''
Script for Bot Execution
'''

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import tweepy

from autosarkasmus.bot.autosarkasmus_bot import AutosarkasmusBot, AutosarkasmusBotStreamer

CONFIG_PATH = 'config.json'

if __name__ == '__main__':
    print('\n - Autosarkasmus Bot -\n')

    print('preparing the bot...')
    bot = AutosarkasmusBot(CONFIG_PATH, verbose=True)
    bot.train()

    print('opening stream...')
    twitter_stream = tweepy.Stream(bot.oauth, AutosarkasmusBotStreamer(bot))
    twitter_stream.filter(track=['@'+bot.screen_name], async=True) # set bot to track its username
    print('@'+bot.screen_name, 'is listening.')
