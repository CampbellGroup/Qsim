from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re

@respond_to('hi', re.IGNORECASE)
def hi(message):
    message.reply('Greglbot is clean and sober... not high')
    message.react('+1')

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
