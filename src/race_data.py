# to do 
# 1. determine best latency for page requests
# 2. leaderboard results data Model
# 3. separate race adapter from api class
# 4. add excceptions
# 5. add logging

import requests
from typing import Dict, List
import re, json
from bs4 import BeautifulSoup

# current endpoint for use in Ottawa, not sure if this changes
SPORTSTATS_AWS_GATEWAY_ENDPOINT = '5b8btxj9jd'




# {
#             "pid": 1,
#             "ssuid": null,
#             "pt": null,
#             "pa": 28,
#             "rtro": 1,
#             "rtrg": 1,
#             "rtrc": 1,
#             "bib": "1",
#             "pcid": null,
#             "ptid": null,
#             "pnf": "Lee",
#             "pnl": "Wesselius",
#             "pdn": "Lee Wesselius",
#             "lo1": "Mountain",
#             "lo2": "ON",
#             "lo3": "CAN",
#             "pg": "m",
#             "pc": "M25-29",
#             "ps": null,
#             "dn": "Lee Wesselius",
#             "data": {
#                 "333890": {
#                     "cd": 920000,
#                     "rt": 920000,
#                     "st": 920000,
#                     "tod": 27923000,
#                     "pace": {
#                         "kph": 19.57,
#                         "mph": 12.16,
#                         "pkm": "3:04.2",
#                         "pmi": "4:55.8",
#                         "p100": "00:18"
#                     },
#                     "stro": 1,
#                     "rtro": 1,
#                     "strg": 1,
#                     "rtrg": 1,
#                     "strc": 1,
#                     "rtrc": 1
#                 },
#                 "333891": {
#                     "cd": 1792000,
#                     "rt": 1792000,
#                     "st": 0,
#                     "tod": 28794000,
#                     "pace": {
#                         "kph": 20.09,
#                         "mph": 12.48,
#                         "pkm": "2:59.4",
#                         "pmi": "4:48.6",
#                         "p100": "00:17"
#                     },
#                     "stro": 0,
#                     "strg": 0,
#                     "strc": 0,
#                     "rtro": 1,
#                     "rtrg": 1,
#                     "rtrc": 1
#                 }
#             },
#             "ot": 1792000,
#             "ldc": 0,
#             "ldg": 0,
#             "ldo": 0,
#             "rank": 1
#         },

class RaceResult:
    def __init__(self, pid:int, bib:str, pa:int, pg:str, pc:str, data: Dict, rank: int, **kwargs) -> None:
        self.pid = pid
        self.bib = bib
        self.age = pa
        self.gender = pg
        self.category = pc
        self.race_data = data
        self.rank = rank
        self.__dict__.update(kwargs)

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


    def get_leaderboard_results(self, race_id:str, event_id:str, mid:str, page:int=0, page_size:int=10,
                                 sort:str='', category:str='', gender:str='', search_data:str=''):
        params = {
            'rid': race_id,  
            'eid': event_id,
            'mid': mid, # ?
            'page': page,
            'pageSize': page_size,
            'sort': sort,
            'category': category,
            'gender': gender,
            'searchData': search_data
        }
        return self._rest_adapter.get(endpoint='results', ep_params=params)
    

    def get_full_leaderboard(self, race_id:str, event_id:str, mid:str, category:str='', gender:str='', search_data:str='', page_size:int=10, max_amount:int=100):
        leaderboard = []
        current_page = 0
        last_page = 0
        total_athletes_in_board = 0
        total_athletes_requested = 0

        while current_page <= last_page:
            request = api.get_leaderboard_results(race_id, event_id, mid, page=current_page, page_size=page_size,
                                                  category=category, gender=gender, search_data=search_data).data
            page_info = request['pageInfo']
            last_page = page_info['total_pages']
            total_athletes_in_board = page_info['total_athletes'] # will log later

            for entry in request['results']:
                leaderboard.append(RaceResult(**entry))
                total_athletes_requested += 1
                if total_athletes_requested >max_amount:
                    last_page = 0
                    break
            current_page += 1


        return leaderboard
        

if __name__ == "__main__":
    api = SportStatsApi()
    event_id = api.search_event("ottawa", 2, 0).data[1]['eid'] # gives eid - event id, will need slug
    print(event_id)
    mid, ottawa_races = (api.get_races_at_event('ottawa-race-weekend'))
    for race in ottawa_races:
        print(f'race name:{race["lbl"]}  rid:{race["rid"]}, mid:{mid}')

    leaderboard = []
    for entry in api.get_leaderboard_results('140564', event_id, '1370').data['results']:
        leaderboard.append(RaceResult(**entry))

    print([print(str(x)) for x in leaderboard])

    api.get_full_leaderboard('140564', event_id, '1370', page_size=100, max_amount=200)


    



# def convert_segment_time(time_ms):
#     return time_ms / 60000.0


# def label_race_splits(race_splits):
#     '''
#     split_config section of request results contains summary for splits.
#     We can use this information to infer readable names for data columns.
#     Example split - not sure what all keys mean
#         "splitconfig": [
#         {
#             "cid": 381034, # split id?
#             "rid": 140564, # race id
#             "lbl": "time", 
#             "ct": "7", 
#             "cf": "1",
#             "cd": "10000", # 10000 meters = 10k
#             "co": "3", # 3.1 miles
#             "cho": "11",
#             "cao": null,
#             "fc": 1,
#             "pf": 0,
#             "tf": "hh:mm:ss" # time format 
#         },

#     '''
#     race_split_names = {}
#     for split in race_splits:
#         split_description = f'{split['cd']}m'
#         race_split_names[split["cid"]] = split_description
#     return race_split_names



#     # with open('10k_test.json', 'w') as f:
#     #     json.dump(data, f)

#     # race_info = data['pageInfo']
#     # split_info = data['splitconfig']
#     # leader_board = data['results']

#     # total_athletes = data['pageInfo']['total_athletes']
#     # total_pages = data['pageInfo']['total_pages']

#     # # will omit names from data 

#     # segments = label_race_splits(split_info)

#     # # 1. send request to get total # of entries
#     # # "pageInfo": {
#     # #         "total_athletes": 6899,
#     # #         "total_pages": 690,
#     # #         "page": "0",
#     # #         "pageSize": "10",    

#     # race_entries = []
#     # for entry in leader_board:

#     #     entry_data= {
#     #         "pid": entry["pid"],
#     #         "age": entry["pa"],
#     #         "overall_rank": entry["rtro"],
#     #         "gender_rank": entry["rtrg"],
#     #         "category_rank": entry["rtrc"],
#     #         "bib": entry["bib"],
#     #         "gender": entry["pg"],
#     #         "category": entry["pc"]
#     #     }

#     #     for race_segment in segments.keys():

#     #         split = entry['data'][str(race_segment)]
#     #         segment_label = segments[race_segment]
#     #         split_data = {
#     #             f"{segment_label}_tod":split["tod"],
#     #             f"{segment_label}_rt":split["rt"],
#     #             f"{segment_label}_kph":split['pace']["kph"],
#     #             f"{segment_label}_pkm":split['pace']["pkm"]

#     #         }
#     #         entry_data.update(split_data)
#     #     race_entries.append(entry_data)

#     # df_results = pd.DataFrame(race_entries)
#     # plt.hist(df_results['10000m_rt'])
#     # plt.show()


#     # TO DO 
#     # - search race events using base url instead of url with json in it
#     # - move data reformat to dataframe from main to separate function
#     # - test getting full leaderboard through pagination
#     # - test getting single runner results from leaderboard
#     # - plot percentile of single runner within race time distribution