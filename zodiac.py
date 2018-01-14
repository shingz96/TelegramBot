from bs4 import BeautifulSoup
import requests,json,re

class ZodiacLuck:
    def __init__(self,general,love,work,wealth,health,color,num,match,desc,last_update):
        self.general = general
        self.love = love
        self.work = work
        self.wealth = wealth
        self.health = health
        self.color = color
        self.num = num
        self.match = match
        self.desc = desc
        self.last_update = last_update
    def __repr__(self):
        gd = self.general.split('^')[0] 
        gr = star(self.general.split('^')[1])
        ld = self.love.split('^')[0] 
        lr = star(self.love.split('^')[1])
        wkd = self.work.split('^')[0] 
        wkr = star(self.work.split('^')[1])
        wld = self.wealth.split('^')[0] 
        wlr = star(self.wealth.split('^')[1])
        hd = self.health.split('^')[0] 
        hr = star(self.health.split('^')[1])
        return '`%s`\n\n`综合运势` - %s\n%s\n\n`爱情运势` - %s\n%s\n\n`事业学业` - %s\n%s\n\n`财富运势` - %s\n%s\n\n`健康运势` - %s\n%s\n\n`幸运颜色`: %s\n`幸运数字`: %s\n`速配星座`: %s\n`短评`: %s\n' %(self.last_update,gr,gd,lr,ld,wkr,wkd,wlr,wld,hr,hd,self.color,self.num,self.match,self.desc)
    def __str__(self):
        gd = self.general.split('^')[0] 
        gr = star(self.general.split('^')[1])
        ld = self.love.split('^')[0] 
        lr = star(self.love.split('^')[1])
        wkd = self.work.split('^')[0] 
        wkr = star(self.work.split('^')[1])
        wld = self.wealth.split('^')[0] 
        wlr = star(self.wealth.split('^')[1])
        hd = self.health.split('^')[0] 
        hr = star(self.health.split('^')[1])
        return '`%s`\n\n`综合运势` - %s\n%s\n\n`爱情运势` - %s\n%s\n\n`事业学业` - %s\n%s\n\n`财富运势` - %s\n%s\n\n`健康运势` - %s\n%s\n\n`幸运颜色`: %s\n`幸运数字`: %s\n`速配星座`: %s\n`短评`: %s\n' %(self.last_update,gr,gd,lr,ld,wkr,wkd,wlr,wld,hr,hd,self.color,self.num,self.match,self.desc)

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

def star(percent):
    p = int(percent)
    if p > 80:
        s = '⭐️⭐️⭐️⭐️⭐️'
    elif p > 60:
        s = '⭐️⭐️⭐️⭐️'
    elif p > 40:
        s = '⭐️⭐️⭐️'
    elif p > 20:
        s = '⭐️⭐️'
    else:
        s = '⭐️'
    return s
    
def zodiac_simple_list():
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
    return json.loads(json.dumps(zodiacs))

def regex(pattern,input,result_index):
    result = re.findall(pattern,input)
    return result[result_index]
    
def get_zodiac_luck(zodiac):
    url = 'http://www.xzw.com/fortune/'  + zodiac
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    last_update = soup.h4.get_text().replace(soup.h4.small.get_text(),' - %s' %soup.h4.small.get_text())

    misc = [x.get_text() for x in soup.findAll('dd')[-1].findAll('li')]   
    color=misc[-4].split('：')[-1]
    num=misc[-3].split('：')[-1]
    match=misc[-2].split('：')[-1]
    desc=misc[-1].split('：')[-1]
    
    rates = regex(r'(cd=\[{){1}(.*\w\s\t\r\n)*(.*}];){1}', soup.find('div',{'class':'chart'}).script.get_text(),0)
    rates = ''.join([x for x in rates if x.strip() != ''])
    rates = ''.join([x+'},' for x in rates.split(',zIndex:7},')[:-1]])[:-1]
    rates = json.loads(rates.replace('cd=','').replace('name','"name"').replace('data','"data"')+']')    
    soup=soup.find('div',{'class': 'c_cont'})
    lucks = soup.findAll('p')

    general= '%s^%g'  %(lucks[0].span.get_text().strip().replace(':',''), rates[0]['data'][6]/5*100) 
    love= '%s^%g'  %(lucks[1].span.get_text().strip().replace(':',''), rates[1]['data'][6]/5*100)
    work='%s^%g'  %(lucks[2].span.get_text().strip().replace(':',''), rates[2]['data'][6]/5*100)
    wealth='%s^%g'  %(lucks[3].span.get_text().strip().replace(':',''), rates[3]['data'][6]/5*100)
    health='%s^%g'  %(lucks[4].span.get_text().strip().replace(':',''), rates[4]['data'][6]/5*100)

    return ZodiacLuck(general,love,work,wealth,health,color,num,match,desc,last_update)