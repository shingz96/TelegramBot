import logging,os,requests
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
#TOKEN = '190572241:AAHr93U-50dvynk2l5SeQr25G6lvDIBReJw'
TOKEN = os.environ['BOT_TOKEN']
HELP_MSG = 'Send a picture to begin'

def is_image(url):
    return url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.png') 

def get_input(bot, update):
    user = update.message.from_user
    if update.message.photo:
        update.message.reply_text("Thinking hard...")
        logger.info("Photo received from %s" % user.first_name)
        photo_id = update.message.photo[-1].file_id
        json_url = ('https://api.telegram.org/bot' + TOKEN + '/getFile?file_id=' + photo_id)
        logger.info(update.message.photo[-1].file_size)
        logger.info(requests.get(json_url).json())

        file_path = (requests.get(json_url).json())['result']['file_path']
        photo_url = 'https://api.telegram.org/file/bot' + TOKEN + "/" + file_path
        logger.info(photo_url)
        update.message.reply_photo(photo_url)
		
    elif not is_image(update.message.text):
        update.message.reply_text(HELP_MSG)
	
def start(bot, update):
    update.message.reply_text('Hi, %s!\nSend a picture to begin' %str(update.message.from_user.first_name))


def help(bot, update):
    update.message.reply_text(HELP_MSG)


def echo(bot, update):
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

# Write your handlers here


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
        bot = Bot(TOKEN)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue)
    else:
        updater = Updater(TOKEN)
        bot = updater.bot
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text | Filters.photo, get_input))

        # log all errors
        dp.add_error_handler(error)
    # Add your handlers here
    if webhook_url:
        bot.set_webhook(webhook_url=webhook_url)
        thread = Thread(target=dp.start, name='dispatcher')
        thread.start()
        return update_queue, bot
    else:
        bot.set_webhook()  # Delete webhook
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    setup()