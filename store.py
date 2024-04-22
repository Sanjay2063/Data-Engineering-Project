from bs4 import BeautifulSoup
import requests
import openpyxl
import json
import time

def parse(jsonData,key):
    for k, val in jsonData.items():
        if type(val)==dict and k != key:
           return parse(val,key)
        else:
            if k == key:
                return val
            if type(val)==dict:
                return parse(val,key)

def getStoredetails(url):
    storeDetails=[]
    response=requests.get(url)
    if response.status_code == 200:
        data=BeautifulSoup(response.text,'html.parser')
        scripttag = data.find(id='__NEXT_DATA__')
        content = scripttag.string
        jsonData = json.loads(content)
        result = parse(jsonData,'data')
        for i in result:
            storeDetails.append([i.get('alt_store_name_catch'),i.get('address_full'),i.get('store_phone'),i.get('single_interface_sto')])
    return storeDetails
            


wb = openpyxl.load_workbook('store_data.xlsx')
sheet = wb.active
sheet.append(['store_area_name','address','phone','url'])
response = requests.get('https://www.lenskart.com/stores')
result = BeautifulSoup(response.text,'html.parser')

locationlist = result.find(class_='AvailableStates_stateContainer__1_HiQ').contents

for i in locationlist:
    url = i.get('href')
    data = getStoredetails(f'https://www.lenskart.com/{url}')
    for j in data:
        sheet.append(j)
    time.sleep(1)


wb.save('store_data.xlsx')



