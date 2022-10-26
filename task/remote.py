import requests

url = 'https://68ecj67379.execute-api.ap-northeast-2.amazonaws.com/api'

with open("../resources/token.txt", 'r') as fp:
    token = fp.readline()

auth_key = None
turn = 1


def start(problem_no):
    global auth_key, turn

    header = {'X-Auth-Token': token}
    data = {'problem': problem_no}

    res = requests.post(url + '/start', headers=header, json=data)
    res = res.json()

    auth_key = res['auth_key']
    turn = 1


def get(path, identifier=None):
    header = {'Authorization': auth_key}

    res = requests.get(url + path, headers=header)
    res = res.json()
    if identifier is not None:
        res = res[identifier]

    return res


def get_new_requests() -> list[dict[str, int]]:
    return get(path='/new_requests', identifier='reservations_info')


def reply(replies):
    header = {'Authorization': auth_key}

    data = {'replies': replies}
    requests.put(url + '/reply', headers=header, json=data)


def simulate(room_assign):
    global turn

    header = {'Authorization': auth_key}
    data = {'room_assign': room_assign}

    res = requests.put(url + '/simulate', headers=header, json=data)
    res = res.json()

    turn += 1

    return res


def get_score():
    return get(path='/score')


__all__ = ["start", "get_new_requests", "reply", "simulate", "get_score"]
