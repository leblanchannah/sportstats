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
        split_description = f'{split['cd']}m'
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

####
if __name__ == "__main__":
    # Example usage
    data = get_leaderboard_results(rid=140564, eid=41996, mid=1370)
    # print(data)

    with open('10k_test.json', 'w') as f:
        json.dump(data, f)

    race_info = data['pageInfo']
    split_info = data['splitconfig']
    leader_board = data['results']

    total_athletes = data['pageInfo']['total_athletes']
    total_pages = data['pageInfo']['total_pages']

    # will omit names from data 

    segments = label_race_splits(split_info)

    # 1. send request to get total # of entries
    # "pageInfo": {
    #         "total_athletes": 6899,
    #         "total_pages": 690,
    #         "page": "0",
    #         "pageSize": "10",    

    race_entries = []
    for entry in leader_board:

        entry_data= {
            "pid": entry["pid"],
            "age": entry["pa"],
            "overall_rank": entry["rtro"],
            "gender_rank": entry["rtrg"],
            "category_rank": entry["rtrc"],
            "bib": entry["bib"],
            "gender": entry["pg"],
            "category": entry["pc"]
        }

        for race_segment in segments.keys():

            split = entry['data'][str(race_segment)]['pace']
            segment_label = segments[race_segment]
            split_data = {
                # f"{segment_label}_time":split["tod"],
                f"{segment_label}_kph":split["kph"],
                f"{segment_label}_pkm":split["pkm"]

            }
            entry_data.update(split_data)
        race_entries.append(entry_data)

    print(race_entries)
    