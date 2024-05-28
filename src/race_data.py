import requests
import json


def get_leaderboard_results(rid, eid, mid, page=0, pageSize=10, sort='', category='', gender='', searchData=''):
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
    print(data)

    with open('10k_test.json', 'w') as f:
        json.dump(data, f)

    # 1. send request to get total # of entries
    # "pageInfo": {
    #         "total_athletes": 6899,
    #         "total_pages": 690,
    #         "page": "0",
    #         "pageSize": "10",    