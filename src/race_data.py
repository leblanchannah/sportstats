import requests
import json
import pandas as pd
import matplotlib.pyplot as plt


SPORTSTATS_AWS_GATEWAY_ENDPOINT = '5b8btxj9jd'

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


def search_events(search_term, limit_count=20, limit_offset=0):

    # example output [
    # {
    #     "eid": "41994",
    #     "dy": "2024",
    #     "dts": "2024-06-01 04:00:00",
    #     "slug": "defi-entreprises-ottawa-gatineau",
    #     "dme": "6",
    #     "tz": "America\/Toronto",
    #     "eik": "41994_6639426f5a2a4.png",
    #     "dye": "2024",
    #     "lo1": "Gatineau",
    #     "lbl": "Defi Entreprises Ottawa Gatineau",
    #     "lo3": "CAN",
    #     "sid": "",
    #     "dte": "2024-06-01 04:00:00",
    #     "lo2": "QC",
    #     "dm": "6",
    #     "mid": "455"
    # },

    base_url = 'https://5b8btxj9jd.execute-api.us-west-2.amazonaws.com/public/eventsearch'
    params = {
        'limitcount': limit_count,
        'limitoffset': limit_offset,
        'lbl': search_term
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    return response.json()



def get_event_race_list(slug):
    # ottawa-race-weekend.json?slug=ottawa-race-weekend
    base_url = 'https://sportstats.one/_next/data/jsw_cJQFRdZTth-22YQKv/en/event/'
    url_w_json = base_url + slug + '.json'
    params = {'slug': slug}
    response = requests.get(url_w_json, params=params)
    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    return response.json()['pageProps']['last_event']['races']







def get_leaderboard_results(rid, eid, mid, page=0, page_size=10, sort='', category='', gender='', search_data=''):

    '''
    TODO
    - get base url for sportsstats
    - test filters
    - test sort
    - test search
    '''
    base_url = "https://5b8btxj9jd.execute-api.us-west-2.amazonaws.com/public/results"
    params = {
        'rid': rid,  # race id?
        'eid': eid, # event id?
        'mid': mid, # ?
        'page': page,
        'pageSize': page_size,
        'sort': sort,
        'category': category,
        'gender': gender,
        'searchData': search_data
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

######
if __name__ == "__main__":

    print(search_events("ottawa", limit_count=20, limit_offset=0))


    print(get_event_race_list('ottawa-race-weekend'))
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

    