from datetime import datetime
import os
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import schedule


 
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]




# url = '''https://search.kathem-re.com/api/1.0/listings?s=%7B%22limit%22%3A%2218%22%2C%22page%22%3A%222%22%2C%22propertyTypes%22%3A%5B%22house%22%2C%22condo%22%5D%2C%22locations%22%3A%5B%7B%22county%22%3A%22Maricopa%22%2C%22state%22%3A%22AZ%22%7D%5D%2C%22maxPrice%22%3A%22689250%22%2C%22minPrice%22%3A%22380000%22%7D'''

def job():
    try:
        # for sheet connections
        creds = ServiceAccountCredentials.from_json_keyfile_name("serviceFile.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("demo").sheet1
        url = '''https://search.kathem-re.com/api/1.0/mapsearch?s=%7B%22propertyTypes%22%3A%5B%22house%22%2C%22condo%22%5D%2C%22locations%22%3A%5B%7B%22county%22%3A%22Maricopa%22%2C%22state%22%3A%22AZ%22%7D%5D%2C%22maxPrice%22%3A%22689250%22%2C%22minPrice%22%3A%22380000%22%7D'''

        value = requests.get(url=url)
        # id=value.json()[0]['id']
        id=value.json()['listings'][0]['id']

        def next_available_row(worksheet):
            str_list = list(filter(None, worksheet.col_values(1)))
            return str(len(str_list)+1)

        link = f"https://search.kathem-re.com/search/detail/{id}"

        # checking the id in sheel
        if not sheet.find(f'{id}'):
            dataFetch = requests.get(f"https://search.kathem-re.com/api/1.0/listing/{id}")
            data = dataFetch.json()
            price = data['formattedPrice']
            Bathrooms = data['bathrooms']
            bedrooms = data['bedrooms']
            Size = str(data['livingAreaSqFt']) + 'SqFt'
            Address = data['addressString']
            build = data["yearBuilt"]
            # statement = f"{Address}\nBuilt {build} | {bedrooms} beds | {Bathrooms} baths | {Size}"

            next = next_available_row(sheet)
            sheet.update_cell(next,1,f"{id}")
            sheet.update_cell(next,2,"NEW")
            sheet.update_cell(next,10,f"{price}")
            sheet.update_cell(next,11,f"{Size}")
            sheet.update_cell(next,12,f"{bedrooms}")
            sheet.update_cell(next,13,f"{Bathrooms}")
            sheet.update_cell(next,14,f"{Address}")
            sheet.update_cell(next,16,f"{link}")

        # creating the log file
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            f= open("log.txt","a")
            f.write(str(dt_string)+"      "+str(id)+"\n")
            f.close()
            

            imageCell = 4

            for i in range(6):
                try:
                    sheet.update_cell(next,imageCell,f"https://{data['largeListingPhotos'][i+1][2:]}")
                    imageCell += 1
                except:
                    break
    except Exception as e:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f= open("log.txt","a")
        f.write(str(dt_string)+"   error occured"+str(e)+"\n")
        f.close()

        
schedule.every().day.at("21:29:10").do(job)
schedule.every().day.at("21:29:30").do(job)
schedule.every().day.at("21:30").do(job)
schedule.every(5).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
