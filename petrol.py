from bs4 import BeautifulSoup
import requests,json

class Petrol:
    def __init__(self,type,price,diff):
        self.type=type
        self.price=price
        self.diff=diff
    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

url='http://petrolpricemalaysia.info/'       
type_text='rpt_title'
price_text='rpt_price'
diff_text='rpt_subtitle'

def get_petrol_info():
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    last_update = soup.find('h1',{"class":""})
    
    soup=soup.find('div',id='rpt_pricr')
    type = soup.findAll('div',{'class': type_text})
    price = soup.findAll('div',{'class': price_text})
    diff = soup.findAll('div',{'class': diff_text})
    
    petrols = []
    for i in range(0,3):
        petrols.append(Petrol(type[i].get_text(),price[i].get_text(),diff[i].get_text()))
    return last_update.get_text(),petrols

