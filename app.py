import logging,os,requests,json,petrol,zodiac
import schedule
from functools import wraps
from ocr import OCRSpace
from queue import Queue
from threading import Thread
from telegram import Bot, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, CallbackQueryHandler, Updater, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = os.environ['BOT_TOKEN']
#TOKEN = '190572241:AAFHhCpgk49I-hxKkcNLKsczLUN_tGx5rqA'
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
        bot.send_chat_action(update.message.chat_id,action=ChatAction.TYPING)
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

def get_petrol_price():
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
    return 'This is the Latest ⛽️ Petrol Price %s.\n\n%s' %(info[0],details)
    
@thinking        
def petrol_price(bot,update):
    btns = [InlineKeyboardButton('Refresh',callback_data='petrol')]
    update.message.reply_text(get_petrol_price(),reply_markup = InlineKeyboardMarkup(build_menu(btns, n_cols=1)))

def handle_petrol_callback(bot,update):
    btns = [InlineKeyboardButton('Refresh',callback_data='petrol')]
    bot.edit_message_text(get_petrol_price(),chat_id=update.callback_query.message.chat_id,message_id=update.callback_query.message.message_id, reply_markup = InlineKeyboardMarkup(build_menu(btns, n_cols=1)),parse_mode=ParseMode.MARKDOWN)    

def luck(bot,update):
    zodiacs = zodiac.zodiac_json()
    button_list = [InlineKeyboardButton('%s %s' %(zodiacs[x]['symbol'],zodiacs[x]['zh']), callback_data=x) for x in zodiac.zodiac_simple_list()]
    update.message.reply_text("Zodiac Luck for Today",reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3)))

def handle_luck_callback(bot,update):
    data = update.callback_query.data
    logger.info('callback data: %s' %data)
    if data == 'back':
        zodiacs = zodiac.zodiac_json()
        button_list = [InlineKeyboardButton('%s %s' %(zodiacs[x]['symbol'],zodiacs[x]['zh']), callback_data=x) for x in zodiac.zodiac_simple_list()]
        bot.edit_message_text("Zodiac Luck for Today",chat_id=update.callback_query.message.chat_id,message_id=update.callback_query.message.message_id,reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3)))
    elif '1' in data:
        btns = [InlineKeyboardButton('Today\'s Luck',callback_data=data.split('^')[-1]),InlineKeyboardButton('Back',callback_data='back'),]
        msg = str(zodiac.get_zodiac_luck(data.split('^')[-1],1))
        bot.edit_message_text(msg,chat_id=update.callback_query.message.chat_id,message_id=update.callback_query.message.message_id, reply_markup = InlineKeyboardMarkup(build_menu(btns, n_cols=1)),parse_mode=ParseMode.MARKDOWN)
    else:
        btns = [InlineKeyboardButton('Tomorrow\'s Luck',callback_data='1^'+data),InlineKeyboardButton('Back',callback_data='back')]
        msg = str(zodiac.get_zodiac_luck(data))
        bot.edit_message_text(msg,chat_id=update.callback_query.message.chat_id,message_id=update.callback_query.message.message_id, reply_markup = InlineKeyboardMarkup(build_menu(btns, n_cols=1)),parse_mode=ParseMode.MARKDOWN)
    bot.answer_callback_query(update.callback_query.id)
    
@thinking      
def start(bot, update):
    update.message.reply_text('Hi, %s! 😃\nSend a picture contain text to begin OCR or use /help to see more' %str(update.message.from_user.first_name))

@thinking      
def help(bot, update):
    update.message.reply_text('Hi, %s!\n' %str(update.message.from_user.first_name) +HELP_MSG)

@thinking    
def echo(bot, update):
    update.message.reply_text(update.message.text)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def updatePetrolPrice():
    logger.info('Running schedule job...')
    bot.sendMessage(chat_id='@msiapetrol', text=get_petrol_price())    
    
# Write your handlers here


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    logger.info('Starting...')
    
    #schedule.every().wednesday.at("18:15").do(updatePetrolPrice) #M'sia time (UTC +8)
    schedule.every().thursday.at("02:15").do(updatePetrolPrice) #UTC time (UTC + 0)
    
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
        dp.add_handler(CommandHandler("luck", luck))
        dp.add_handler(CallbackQueryHandler(handle_luck_callback,pattern = r'(?!petrol)(.*)'))
        dp.add_handler(CallbackQueryHandler(handle_petrol_callback,pattern = r'petrol'))

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
