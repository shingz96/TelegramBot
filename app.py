import logging,os,requests,petrol
from functools import wraps
from ocr import OCRSpace
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = os.environ['BOT_TOKEN']
HELP_MSG = '🌄 Send a picture to begin OCR\n⛽️ /petrol Get Latest 🇲🇾 Petrol Price\n🔯 /luck Get Today Luck (星座运势)'

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

def thinking(func):
    @wraps(func)
    def wrapper(bot,update,*args, **kwargs):
        bot.send_chat_action(update.message.chat_id,action=telegram.ChatAction.TYPING)
        return func(bot,update,*args, **kwargs)
    return wrapper

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
    
@thinking   
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

@thinking        
def petrol_price(bot,update):
    info = petrol.get_petrol_info()
    details = ''
    for i in range(0,len(info[1])):
        diff = info[1][i].diff
        if float(diff) > 0:
            diff = '⬆️ ' + info[1][i].diff
        elif float(diff) < 0:
            diff = '⬇️ ' + info[1][i].diff
        else:
            diff = '↔️ ' + info[1][i].diff
        
        br = ''
        if i<2:
            br = '\n'
        details = details + '%s : %s (%s)' %(info[1][i].type,info[1][i].price,diff) + br
    update.message.reply_text('This is the Latest ⛽️ Petrol Price %s.\n\n%s' %(info[0],details))

@thinking
def zodiac_luck(bot,update):
    zodiac = [
    '♈ Aries\n白羊座 (3.21-4.19)',
    '♉ Taurus\n金牛座 (4.20-5.20)',
    '♊ Gemini\n双子座 (5.21-6.21)',
    '♋ Cancer\n巨蟹座 (6.22-7.22)',
    '♌ Leo\n狮子座 (7.23-8.22)',
    '♍ Virgo\n处女座 (8.23-9.22)',
    '♎ Libra\n天秤座 (9.23-10.23)',
    '♏ Scorpio\n天蝎座 (10.24-11.22)',
    '♐ Sagittarius\n射手座 (11.23-12.21)',
    '♑ Capricorn\n摩羯座 (12.22-1.19)',
    '♒ Aquarius\n水瓶座 (1.20-2.18)',
    '♓ Pisces\n双鱼座 (2.19-3.20)'
    ]
    button_list = [InlineKeyboardButton(x, url='http://www.xzw.com/fortune/%s' %(x.split(' ')[1].split('\n')[0])) for x in zodiac]
    update.message.reply_text("Zodiac Luck for Today",reply_markup = InlineKeyboardMarkup(util.build_menu(button_list, n_cols=3)))
    
@thinking      
def start(bot, update):
    update.message.reply_text('Hi, %s!\nSend a picture contain text to begin OCR or use /help to see more 😃' %str(update.message.from_user.first_name))

@thinking      
def help(bot, update):
    update.message.reply_text('Hi, %s!\n' %str(update.message.from_user.first_name) +HELP_MSG)

@thinking    
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
        dp.add_handler(CommandHandler("luck", zodiac_luck))

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