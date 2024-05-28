import requests
import json


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
        split_description = f'{split['cd']}m_'
        race_split_names[split["cid"]] = split_description
    return race_split_names


def get_leaderboard_results(rid, eid, mid, page=0, pageSize=10, sort='', category='', gender='', searchData=''):

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
        'pageSize': pageSize,
        'sort': sort,
        'category': category,
        'gender': gender,
        'searchData': searchData
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

if __name__ == "__main__":
    # Example usage
    data = get_leaderboard_results(rid=140564, eid=41996, mid=1370)
    # print(data)

    with open('10k_test.json', 'w') as f:
        json.dump(data, f)

    race_info = data['page_info']
    split_info = data['split_config']
    leader_board = data['results']

    total_athletes = data['page_info']['total_athletes']
    total_pages = data['page_info']['total_pages']

    # will omit names from data 

    print(label_race_splits(data['split_config']))

    # 1. send request to get total # of entries
    # "pageInfo": {
    #         "total_athletes": 6899,
    #         "total_pages": 690,
    #         "page": "0",
    #         "pageSize": "10",    