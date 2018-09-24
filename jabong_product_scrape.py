from lxml import html
import csv,os,json
import requests
from exceptions import ValueError
from time import sleep

def AmzonParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url,headers=headers)
    print url
    while True:
        sleep(3)
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//*[@id="product-details-wrapper"]/div[1]/div[2]/div/div[1]/h1/span[3]//text()'
            XPATH_SALE_PRICE = '//*[@id="pdp-price-info"]/span[3]/text()'
            XPATH_ORIGINAL_PRICE = '//*[@id="pdp-price-info"]/span[2]/text()' 
            XPATH_CATEGORY = '//*[@id="content-wrapper"]/div[1]/div/div[1]/ol//text()'
            XPATH_SELLER = '//*[@id="seller-info"]/span//text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'

            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAw_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
            RAW_SELLER = doc.xpath(XPATH_SELLER)

            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAw_AVAILABILITY).strip() if RAw_AVAILABILITY else None
            SELLER = ''.join(RAW_SELLER).strip() if RAW_SELLER else None
            #if not ORIGINAL_PRICE:
             #   ORIGINAL_PRICE = SALE_PRICE

            if page.status_code!=200:
                print page.status_code
                raise ValueError('captha')
                continue
            data = {
                    'NAME':NAME,
                    'SALE_PRICE':SALE_PRICE,
                    'CATEGORY':CATEGORY,
                    'ORIGINAL_PRICE':ORIGINAL_PRICE,
                    'SELLER':SELLER,
                    'URL':url,
                    }

            return data
        except Exception as e:
            print e

def ReadAsin():
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    AsinList =['2057977',
'300035178',
'300035155',]
    extracted_data = []
    for i in AsinList:
        url = "http://www.jabong.com/"+str(i)+".html"
        print "Processing: "+url
        extracted_data.append(AmzonParser(url))
        sleep(5)
    f=open('jabong_output.json','w')
    json.dump(extracted_data,f,indent=4)


if __name__ == "__main__":
    ReadAsin()
