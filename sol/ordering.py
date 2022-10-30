import os
import ast

from task import local as interactor
from sol.naive import Hotel


def largest_request_first(req):
    amount = req['amount']
    return amount


def solve(task_no):
    interactor.start(task_no)

    params = interactor.get_params()
    hotel = Hotel(params['hotel_height'], params['hotel_width'])

    filename = f'../resources/{task_no}.in'
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'r') as fp:
        raw = fp.readline()
        daliy_requests = ast.literal_eval(raw)

    all_requests = [req for requests in daliy_requests for req in requests]
    all_requests.sort(key=largest_request_first)

    accepted_requests = []
    for req in all_requests:
        amount = req['amount']
        in_date = req['check_in_date']
        out_date = req['check_out_date']
        try:
            floor, index = hotel.reserve(amount, in_date, out_date)
        except Hotel.CouldNotFindEmptyRooms:
            continue
        room_no = 1000 * (floor + 1) + (index + 1)
        accepted_requests.append({
            'id': req['id'],
            'check_in_date': req['check_in_date'],
            'room_no': room_no})

    while not interactor.finished():
        reqs = interactor.get_new_requests()
        replies = []

        for req in reqs:
            accept = any(req['id'] == accepted_req['id'] for accepted_req in accepted_requests)
            replies.append({
                'id': req['id'],
                'reply': 'accepted' if accept else 'refused'})
        interactor.reply(replies)
        current_turn_requests = [req for req in accepted_requests
                                 if req['check_in_date'] == interactor.get_turn()]
        room_assign = [{
            'id': req['id'],
            'room_number': req['room_no']}
                for req in current_turn_requests]
        interactor.simulate(room_assign)

    print(interactor.get_score())


if __name__ == '__main__':
    solve(1)
    solve(2)
    