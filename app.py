import logging,os,requests,petrol
from ocr import OCRSpace
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = '190572241:AAHr93U-50dvynk2l5SeQr25G6lvDIBReJw'
#TOKEN = os.environ['BOT_TOKEN']
HELP_MSG = '🌄 Send a picture to begin OCR\n🔹 /petrol Get Latest M\'sia Petrol Price'

def is_image(url):
    return url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.png') 

def process_ocr(url):
    data = requests.get(url).content
    img = url.split('/')[-1]
    with open(img, 'wb') as f:
        f.write(data)
    ocr = OCRSpace()
    result = ocr.ocr_file(img)['ParsedResults'][0]['ParsedText']	
    l = [x.strip() for x in result.split(' ') if x.strip() != '']
    string = ''
    for word in l:
        string += word + ' '	 
    logger.info('OCR result: %s' %string) 		
    os.remove(img)
    return string.strip()
	
def get_input(bot, update):
    user = update.message.from_user
    if update.message.photo:
        update.message.reply_text("Thinking hard...")
        logger.info("Photo received from %s" % user.first_name)
        photo_id = update.message.photo[-1].file_id
        json_url = ('https://api.telegram.org/bot' + TOKEN + '/getFile?file_id=' + photo_id)
        logger.info('Photo details: %s' %(requests.get(json_url).json()))

        file_path = (requests.get(json_url).json())['result']['file_path']
        photo_url = 'https://api.telegram.org/file/bot' + TOKEN + "/" + file_path
        logger.info('Photo url: %s' %photo_url)
        #update.message.reply_photo(update.message.photo[-1])
        update.message.reply_text(process_ocr(photo_url))		
    else:
        update.message.reply_text(HELP_MSG)

def petrol_price(bot,update):
    info = petrol.get_petrol_info()
    details = ''
    for i in range(0,len(info[1])):
        if info[1][i].diff > 0:
            diff = '⬆️ ' + info[1][i].diff
        elif info[1][i].diff < 0:
            diff = '⬇️ ' + info[1][i].diff
        else:
            diff = '↔️ ' + info[1][i].diff
        
        br = ''
        if i<2:
            br = '\n'
        details = details + '%s : %s' %(info[1][i].type,info[1][i].price,diff) + br
    update.message.reply_text('This is the Latest Petrol Price %s.\n%s' %(info[0],details))
        
def start(bot, update):
    update.message.reply_text('Hi, %s!\nSend a picture contain text to begin OCR or use /help to see more 😃' %str(update.message.from_user.first_name))


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
        dp.add_handler(CommandHandler("petrol", petrol_price))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.all, get_input))

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