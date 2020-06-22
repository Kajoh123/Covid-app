import urllib.request, json
import pprint, datetime
from pymongo import MongoClient

URL = 'https://api.covid19api.com/dayone/country/'

class CountryEvents:
    def __init__(self, country):
        self.country = country
        self.events = []

    def read_data(self):
        self.events = DataReader(URL, self.country).filter_data()
        return self.events

class Day:
    def __init__(self, country, date, confirmed, deaths, recovered, active):
        self.country = country
        self.date = date
        self.confirmed = confirmed
        self.deaths = deaths
        self.recovered = recovered
        self.active = active

class DataReader:
    def __init__(self, url, country):
        self.url = url
        self.country = country
        self.url += self.country
    
    def read_from_api(self):
        json_url = urllib.request.urlopen(self.url)
        data = json.loads(json_url.read())
        return data

    def filter_data(self):
        new_list = []
        data = self.read_from_api()
        for day in data:
            new_list.append({
                'date': datetime.datetime.strptime(day['Date'].split('T')[0], '%Y-%m-%d'),
                'deaths': day['Deaths'],
                'active': day['Active'],
                'cases': day['Confirmed'],
                'recovered': day['Recovered']
            })
        return new_list

    def filter_by_date(self, start_date, end_date):
        data = self.filter_data()
        new_data = []
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')        
        for day in data:
            if start_date <= day['date'] and end_date >= day['date']:
                new_data.append(day)
        return new_data

class DatabaseHandler:
    def __init__(self):
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client['covid_db']
        self.country = self.db.country
        self.check_is_update_necessary()

    def check_is_update_necessary(self):      
        for c in self.country.find({}):
            if c['events'][-1]['date'].day + 1 < datetime.datetime.now().day or c['events'][-1]['date'].month < datetime.datetime.now().month:
                tmp_cntry = CountryEvents(c['name'])
                tmp_cntry.read_data()
                self.country.update_one({'name': c['name']}, {'$set': {'events': tmp_cntry.events}})

    def add_country(self):
        inp = str(input("Give country name (reference) "))
        ctr = CountryEvents(inp)
        try:
            ctr.read_data()
        except urllib.error.HTTPError:
            print("Country with this id does not exist!")
            return None
        new_country = {
            'name': ctr.country,
            'events': ctr.events
        }
        self.country.insert_one(new_country)

    def show_data(self):
        for c in self.country.find({}):
            print(c['name'])
            pprint.pprint(c['events'])

def menu():
    terminator = 0
    dh = DatabaseHandler()
    while not terminator:
        choice = str(input('What do you want to do? print - prints all data, add - adds new country, quit - quits app '))
        if choice == 'add':
            dh.add_country()
        if choice == 'print':
            dh.show_data()
        if choice == 'quit':
            terminator = 1
        dh.check_is_update_necessary()

# data = DataReader('https://api.covid19api.com/dayone/country/', 'poland')

# pprint.pprint(data.filter_by_date('2020-05-14', '2020-06-25'))
menu()