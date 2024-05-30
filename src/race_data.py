import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

# current endpoint for use in Ottawa, not sure if this changes
SPORTSTATS_AWS_GATEWAY_ENDPOINT = '5b8btxj9jd'

class Sportstats:

    def __init__(self, gateway_endpoint):
        self.gateway_endpoint = gateway_endpoint
        self.base_url = f'https://{gateway_endpoint}.execute-api.us-west-2.amazonaws.com/public/'


    def _get(self, url, params):
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    
     
    def search_events(self, search_term, limit_count=20, limit_offset=0):
        url = f'{self.base_url}eventsearch'
        params = {
            'limitcount': limit_count,
            'limitoffset': limit_offset,
            'lbl': search_term
        }
        return self._get(url, params=params)
    

    def get_leaderboard_results(self, race_id, event_id, mid, page=0, page_size=10, sort='', category='', gender='', search_data=''):
        url = f'{self.base_url}results'
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
        return self._get(url, params=params)
    

    def get_event_race_list(self, slug_name):
        # need to figure out where code in url comes from 
        # ottawa-race-weekend.json?slug=ottawa-race-weekend
        base_url = 'https://sportstats.one/_next/data/jsw_cJQFRdZTth-22YQKv/en/event/'
        url_w_json = base_url + slug_name + '.json'
        params = {'slug': slug_name}
        response = requests.get(url_w_json, params=params)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()['pageProps']['last_event']['races']


def convert_segment_time(time_ms):
    return time_ms / 60000.0


def label_race_splits(race_splits):
    '''
    split_config section of request results contains summary for splits.
    We can use this information to infer readable names for data columns.
    Example split - not sure what all keys mean
        "splitconfig": [
        {
            "cid": 381034, # split id?
            "rid": 140564, # race id
            "lbl": "time", 
            "ct": "7", 
            "cf": "1",
            "cd": "10000", # 10000 meters = 10k
            "co": "3", # 3.1 miles
            "cho": "11",
            "cao": null,
            "fc": 1,
            "pf": 0,
            "tf": "hh:mm:ss" # time format 
        },

    '''
    race_split_names = {}
    for split in race_splits:
        split_description = f'{split['cd']}m'
        race_split_names[split["cid"]] = split_description
    return race_split_names


def leaderboard_to_dataframe():
    return None

######
if __name__ == "__main__":
    api = Sportstats(SPORTSTATS_AWS_GATEWAY_ENDPOINT)

    # Search for events
    events = api.search_events("ottawa", limit_count=2, limit_offset=0)
    print(events)

    # Get event race list
    race_list = api.get_event_race_list('ottawa-race-weekend')
    print(race_list)

    # Example usage
    # data = get_leaderboard_results(rid=140564, eid=41996, mid=1370, page=0, page_size=600)
    # # print(data)

    # with open('10k_test.json', 'w') as f:
    #     json.dump(data, f)

    # race_info = data['pageInfo']
    # split_info = data['splitconfig']
    # leader_board = data['results']

    # total_athletes = data['pageInfo']['total_athletes']
    # total_pages = data['pageInfo']['total_pages']

    # # will omit names from data 

    # segments = label_race_splits(split_info)

    # # 1. send request to get total # of entries
    # # "pageInfo": {
    # #         "total_athletes": 6899,
    # #         "total_pages": 690,
    # #         "page": "0",
    # #         "pageSize": "10",    

    # race_entries = []
    # for entry in leader_board:

    #     entry_data= {
    #         "pid": entry["pid"],
    #         "age": entry["pa"],
    #         "overall_rank": entry["rtro"],
    #         "gender_rank": entry["rtrg"],
    #         "category_rank": entry["rtrc"],
    #         "bib": entry["bib"],
    #         "gender": entry["pg"],
    #         "category": entry["pc"]
    #     }

    #     for race_segment in segments.keys():

    #         split = entry['data'][str(race_segment)]
    #         segment_label = segments[race_segment]
    #         split_data = {
    #             f"{segment_label}_tod":split["tod"],
    #             f"{segment_label}_rt":split["rt"],
    #             f"{segment_label}_kph":split['pace']["kph"],
    #             f"{segment_label}_pkm":split['pace']["pkm"]

    #         }
    #         entry_data.update(split_data)
    #     race_entries.append(entry_data)

    # df_results = pd.DataFrame(race_entries)
    # plt.hist(df_results['10000m_rt'])
    # plt.show()

    