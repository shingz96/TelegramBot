from bs4 import BeautifulSoup
import requests,json

class ZodiacLuck:
    def __init__(self,details):
        self.details = details
    def __repr__(self):
        string = ''
        for i in self.details:
            string = string + '*%s*\n%s\n\n' %(i['title'],i['desc'])
        return string   
    def __str__(self):
        string = ''
        for i in self.details:
            string = string + '*%s*\n%s\n\n' %(i['title'],i['desc'])
        return string

class Zodiac:
    def __init__(self,name,symbol,zh,range):
        self.name = name
        self.symbol = symbol
        self.zh = zh
        self.range = range
    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)        

url='http://www.xzw.com/fortune/'       

zodiac = [
    'Aries',
    'Taurus',
    'Gemini',
    'Cancer',
    'Leo',
    'Virgo',
    'Libra',
    'Scorpio',
    'Sagittarius',
    'Capricorn',
    'Aquarius',
    'Pisces'
    ]

def zodiac_simple_list(index):
    return zodiac

def zodiac_json():
    zodiacs = {'Aries':{'symbol':'♈','zh':'白羊座','range':'3.21-4.19'},
    'Taurus':{'symbol':'♉','zh':'金牛座','range':'4.20-5.20'},
    'Gemini':{'symbol':'♊','zh':'双子座 ','range':'5.21-6.21'},
    'Cancer':{'symbol':'♋','zh':'巨蟹座','range':'6.22-7.22'},
    'Leo':{'symbol':'♌','zh':'狮子座','range':'7.23-8.22'},
    'Virgo':{'symbol':'♍','zh':'处女座','range':'8.23-9.22'},
    'Libra':{'symbol':'♎','zh':'天秤座','range':'9.23-10.23'},
    'Scorpio':{'symbol':'♏','zh':'天蝎座','range':'10.24-11.22'},
    'Sagittarius':{'symbol':'♐','zh':'射手座','range':'11.23-12.21'},
    'Capricorn':{'symbol':'♑','zh':'摩羯座','range':'12.22-1.19'},
    'Aquarius':{'symbol':'♒','zh':'水瓶座','range':'1.20-2.18'},
    'Pisces':{'symbol':'♓','zh':'双鱼座','range':'2.19-3.20'}
    }
    return json.loads(json.dumps(zodiac))
 
def get_zodiac_luck(zodiac):
    global url
    url = url + zodiac
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    last_update = soup.h4.small

    soup=soup.find('div',{'class': 'c_cont'})
    lucks = soup.findAll('p')

    details = []
    for luck in lucks:
        raw = {'title': luck.strong.get_text().strip(), 'desc': luck.span.get_text().strip().replace(':','')}
        details.append(json.loads(json.dumps(raw)))
    
    return ZodiacLuck(details)