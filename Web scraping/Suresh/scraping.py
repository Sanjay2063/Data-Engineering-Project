import requests
import time
import openpyxl


def extractValues(data,keys):
    dic ={}
    def extract(data,keys,dic):
        if isinstance(data,dict):
            for k,val in data.items():
                if k in keys and k not in dic:
                    dic[k]=val
                elif isinstance(val,(list,dict)):
                    extract(val,keys,dic)
        elif isinstance(data,list):
            for i in data:
               extract(i,keys,dic)
        return dic 
    return extract(data,keys,dic)

def fetchData(id,pages,sheet,keys):
    url = f"https://api-gateway.juno.lenskart.com/v2/products/category/{id}" # api endpoint url
    for i in range(0,pages):
        response = requests.get(url, params={"page-size": "15","page":f"{i}"})
        if response.status_code == 200 :
            result = response.json()
            data = result["result"]["product_list"]
            print(len(data))
            for j in range(0,len(data)):
                dic = extractValues(data[j],keys)
                ls = []
                for key in keys:
                    if key in dic:
                        ls.append(dic.get(key))
                    else:
                        ls.append('None')
                sheet.append(ls)
        else:
            print(response.status_code)
        time.sleep(1)
    


wb = openpyxl.load_workbook('filename.xlsx')
sheet = wb.active
sheet.append(['id','name','url','price','size','width'])
keys=['id','brand_name','product_url','price','size','width']

fetchData(8080,53,sheet,keys) # 8080 is port number , 53 is Total Number of products / 15


wb.save('filename.xlsx')

