# import libraries
from bs4 import BeautifulSoup
import os
import pandas as pd
import json
import sqlite3

# list all files in rumah123 folder
files = os.listdir('rumah123')

# iterate all files in rumah123 folder
# then convert to json
for index,file in enumerate(files):
    print(file, '-', index+1,'/',len(files))
    filepath = 'rumah123/' + file
    with open(filepath,'r') as f:
        soup = BeautifulSoup(f)
    # if this file is a house, indicated by propery area info
    if soup.find('div',class_='property-areas-info'):
        properties_data = []

        price = soup.find('div',class_='property-price').get_text()
        price = 'Harga:'+price
        properties_data.append(price)

        address = soup.find('span',class_='property-address').get_text()
        address = 'Alamat:'+address
        properties_data.append(address)

        area_info = soup.find('div',class_='property-areas-info').find_all('li')
        for info in area_info:
            properties_data.append(info.get_text())

        property_features = soup.find('ul','property-features')

        if property_features:
            bedroom = property_features.find('i',class_='property-bed')
            bedroom = 'Bedroom:'+bedroom.next if bedroom else 'Bedroom:N/A'
            properties_data.append(bedroom)

            bathroom = property_features.find('i',class_='property-bath')
            bathroom = 'Bathroom:'+bathroom.next if bathroom else 'Bathroom:N/A'
            properties_data.append(bathroom)

            carport = property_features.find('i',class_='property-car')
            carport = 'Carport:'+carport.next if carport else 'Carport:N/A'
            properties_data.append(carport)

        details = soup.find_all('div',class_='container')[-1].find_all('div')[1:]
        for detail in details:
            if ((':' in detail.get_text()) and (detail.get_text()[-1] != ':')):
                properties_data.append(detail.get_text())

        free_text = soup.find(class_='listing-description')
        free_text = 'free_text:'+free_text.get_text() if free_text else 'free_text:'+'N/A'
        properties_data.append(free_text)

        properties_key = []
        properties_value = []
        for data in properties_data:
            data = data.split(':')
            properties_key.append(data[0].strip())
            properties_value.append(data[1].strip())
        properties_data = dict(zip(properties_key,properties_value))

        json_name = filepath.replace('txt','json')
        json_name = json_name.replace('rumah123','rumah123_json')
        with open(json_name,'w') as f:
            json.dump(properties_data,f)
            
con = sqlite3.connect('db.sqlite3')

df = pd.DataFrame()
filelist = os.listdir('rumah123_json')
for index,file in enumerate(filelist):
    filepath = 'rumah123_json/'+file
    series_ = pd.read_json(filepath,typ='series')
    df = df.append(pd.DataFrame([series_]),
                   ignore_index=True, sort=False)

df.to_sql('rumah123_listing',con)
