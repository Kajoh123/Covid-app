import urllib.request, json
import pprint, datetime

URL = 'https://api.covid19api.com/dayone/country/'

class Country:
    def __init__(self, name):
        self.name = name

class CountryEvents:
    def __init__(self, country):
        self.country = country
        self.events = []

    def read_data(self):
        self.events = DataReader(URL, country).filter_data()

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


data = DataReader('https://api.covid19api.com/dayone/country/', 'poland')

pprint.pprint(data.filter_by_date('2020-05-14', '2020-06-17'))