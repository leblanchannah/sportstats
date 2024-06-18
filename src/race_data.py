import requests
from typing import Dict, List
import re, json
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# current endpoint for use in Ottawa, not sure if this changes
SPORTSTATS_AWS_GATEWAY_ENDPOINT = '5b8btxj9jd'


class RaceResult:
    def __init__(self, pid:int, bib:str, pa:int, pg:str, pc:str, data: Dict, rank: int, split_config: Dict, **kwargs) -> None:
        self.pid = pid
        self.bib = bib
        self.age = pa
        self.gender = pg
        self.category = pc
        self.split_config = self.split_lookup(split_config)
        self.race_data = data
        self.rank = rank
        self.__dict__.update(kwargs)


    def split_lookup(self, split_config: Dict):
        splits = {}
        for split in split_config:
            splits[split['cid']] = split['cd']
        return splits


    def __str__(self):
        return f'Bib:{self.bib}, Age:{self.age}, Gender:{self.gender}, Category:{self.category}, Place:{self.rank}'


class RequestResult:
    def __init__(self, status_code: int, message: str = '', data: List[Dict] = None):
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []


class RestAdapter:

    def __init__(self, hostname):
        self.base_url = hostname


    def _do(self, http_method: str, endpoint: str, ep_params: Dict = None, data: Dict = None) -> RequestResult:
        full_url = self.base_url + endpoint
        try:
            response = requests.request(method=http_method, url=full_url, params=ep_params, json=data)
            data_out = response.json()
            return RequestResult(response.status_code, message=response.reason, data=data_out)
        except requests.exceptions.RequestException as e:
            raise Exception(data_out["message"])
        

    def get(self, endpoint: str, ep_params: Dict=None):
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params)
    

class SportStatsApi:
    def __init__(self, hostname: str = 'https://5b8btxj9jd.execute-api.us-west-2.amazonaws.com/public/'):
        self._rest_adapter = RestAdapter(hostname)
    

    def search_event(self, search: str, limit_count: int, limit_offset: int):
        params = {
            'limitcount': limit_count,
            'limitoffset': limit_offset,
            'lbl': search
        }
        return self._rest_adapter.get(endpoint='eventsearch', ep_params=params)
    

    def get_races_at_event(self, event_slug_name: str):
        soup = BeautifulSoup(requests.get(f'https://sportstats.one/event/{event_slug_name}').text, "html.parser")
        event_script = json.loads(soup.find('script', id="__NEXT_DATA__").text)
        mid = event_script["props"]["pageProps"]["mid"]
        races = event_script["props"]["pageProps"]["last_event"]["races"]
        return mid, races
    
    
    def get_leaderboard_results(self, race_id:str, event_id:str, mid:str, category:str='', gender:str='', search_data:str='', page:int=0, page_size:int=10, max_amount:int=-1):
        leaderboard = []
        last_page = 0
        total_athletes_in_board = 0
        total_athletes_requested = 0

        params = {
            'rid': race_id,  
            'eid': event_id,
            'mid': mid,
            'page': page,
            'pageSize': page_size,
            # 'sort': sort,
            'category': category,
            'gender': gender,
            'searchData': search_data
        }
        
        while params['page'] <= last_page:
            
            request = self._rest_adapter.get(endpoint='results', ep_params=params).data
            page_info = request['pageInfo']
            last_page = page_info['total_pages']
            total_athletes_in_board = page_info['total_athletes'] # will log later, will be helpful to confirm I got all leaderboard entries

            for entry in request['results']:
                entry['split_config'] = request['splitconfig']
                leaderboard.append(RaceResult(**entry))
                total_athletes_requested += 1
                if total_athletes_requested >= max_amount and max_amount!=-1:
                    last_page = 0
                    break
            params['page'] += 1

        return leaderboard
        

def convert_segment_time(time_ms):
    return time_ms / 60000.0

if __name__ == "__main__":
    # api = SportStatsApi()
    # event_id = api.search_event("ottawa", 2, 0).data[1]['eid'] # gives eid - event id, will need slug
    # print(event_id)
    # mid, ottawa_races = (api.get_races_at_event('ottawa-race-weekend'))
    # for race in ottawa_races:
    #     print(f'race name:{race["lbl"]}  rid:{race["rid"]}, mid:{mid}')

    # json_string = json.dumps([ob.__dict__ for ob in api.get_leaderboard_results('140564', event_id, '1370', page_size=100, max_amount=-1)])
    # with open('../data/10k_test.json', 'w') as f:
    #     f.write(json_string)

    
    with open('../data/10k_test.json') as f:
        d = json.load(f)
        df = pd.json_normalize(d)

    # print(df.columns)
    # print(df.head())
    df = df[df['gender']=='f']
    df['race_data.381034.rt'] = convert_segment_time(df['race_data.381034.rt'])
    print(df.columns)
    print(df['race_data.381034.rt'].describe(percentiles=[0.01, 0.05, 0.1]))

    # my_time = df[df['bib']=='30482']['race_data.381034.rt'].values
    # n, bins, patches = plt.hist(df['race_data.381034.rt'], bins=60)
    # my_bin = (bins<my_time).sum()
    # # Change the color of the third bin (index 2)
    # patches[my_bin].set_facecolor('red')
    # plt.title('Ottawa Race Weekend 10k, Female')
    # plt.xlabel('Time (Mins)')
    # plt.ylabel('Count')

    # plt.savefig('../figures/ottawa_race_weekend_10k_female_hist.png')
    # plt.show()
    # # 381034 = 10k

    # heatmap 
    # x = race_data.381035.pace.pkm
    # y = race_data.381034.pace.pkm
    # determine bin width, 5 seconds? min and max
    # how to put paces into datetime format 

