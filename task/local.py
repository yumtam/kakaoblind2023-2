import os
import copy
import ast

import params


class Task:
    def __init__(self, task_no):
        self._turn = 0
        filtered_params = [p for p in params.task_params
                           if p['task_no'] == task_no]
        if not filtered_params:
            raise ValueError(f"Invalid {task_no=}, see params.py")
        self._params = filtered_params.pop()
        filename = f'../resources/{task_no}.in'
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'r') as fp:
            raw = fp.readline()
            self._reqs = ast.literal_eval(raw)
        self._pending_reqs = []
        self._accepted_reqs = []
        self._score_handler = ScoreHandler(self._reqs)
        self._hotel = Hotel(self._params['hotel_height'], self._params['hotel_width'])
        self._enlist_pending_reqs()

    def get_turn(self):
        return self._turn + 1

    def get_new_requests(self):
        if self._turn < len(self._reqs):
            return copy.deepcopy(self._reqs[self._turn])
        return []

    def get_score(self):
        return self._score_handler.get_score()

    def put_reply(self, replies):
        for reply in replies:
            filtered_reqs = [req for req in self._pending_reqs
                             if req['id'] == reply['id']]
            if not filtered_reqs:
                continue
            req = filtered_reqs.pop()
            self._pending_reqs.remove(req)
            if reply['reply'] == 'accepted':
                self._accepted_reqs.append(req)
                continue
            if reply['reply'] == 'refused':
                self._score_handler.update_refused(req)
                continue

    def _enlist_pending_reqs(self):
        reqs = self.get_new_requests()
        for req in reqs:
            req['received_date'] = self.get_turn()
            self._pending_reqs.append(req)

    def _refuse_overdue_reqs(self):
        overdue_reqs = [req for req in self._pending_reqs
                        if (req['check_in_date'] >= self.get_turn()
                            or req['received_date'] + 14 >= self.get_turn())]

        for req in overdue_reqs:
            self._score_handler.update_refused(req)
            self._pending_reqs.remove(req)

    def _accepted_reqs_delete_by_id(self, id):
        filtered_reqs = [req for req in self._accepted_reqs
                         if req['id'] == id]
        if not filtered_reqs:
            return
        req = filtered_reqs.pop()
        self._accepted_reqs.remove(req)

    def _process_room_assignments(self, room_assign):
        current_turn_reqs = [req for req in self._accepted_reqs
                             if req['check_in_date'] == self.get_turn()]
        for assign in room_assign:
            filtered_reqs = [req for req in current_turn_reqs
                             if req['id'] == assign['id']]
            if not filtered_reqs:
                continue
            req = filtered_reqs.pop()
            room_no = assign['room_number']
            amount = req['amount']
            check_out_date = req['check_out_date']
            if self._hotel.put_peeps(room_no, amount, check_out_date):
                current_turn_reqs.remove(req)
                self._accepted_reqs_delete_by_id(req['id'])
        for req in current_turn_reqs:
            self._score_handler.update_failed(req)

    def simulate(self, room_assign):
        self._hotel.process_checkout(self.get_turn())
        self._refuse_overdue_reqs()
        self._process_room_assignments(room_assign)
        self._turn += 1
        self._enlist_pending_reqs()


class ScoreHandler:
    def __init__(self, reqs):
        self._refused_req_cnt = 0
        self._refused_req_peeps = 0
        self._failed_peeps = 0
        self._total_req_cnt = sum(map(len, reqs))
        self._total_req_peeps = sum((sum(req['amount'] for req in day) for day in reqs))

    def get_score(self):
        penalty = 0
        penalty += 4500 * self._failed_peeps / self._total_req_peeps
        penalty += 500 * self._refused_req_peeps / self._total_req_peeps
        penalty += 90 * self._refused_req_cnt / self._total_req_cnt
        return penalty, (self._failed_peeps, self._refused_req_peeps, self._refused_req_cnt)

    def update_refused(self, req):
        self._refused_req_cnt += 1
        self._refused_req_peeps += req['amount']

    def update_failed(self, req):
        self._failed_peeps += req['amount']


class Hotel:
    def __init__(self, height, width):
        self._height = height
        self._width = width
        self._array = [[0] * width for _ in range(height)]

    def put_peeps(self, room_no, amount, check_out_date) -> bool:
        floor = room_no // 1000 - 1
        start_idx = room_no % 1000 - 1

        if self._array[floor][start_idx : start_idx+amount] == [0] * amount:
            self._array[floor][start_idx : start_idx+amount] = [check_out_date] * amount
            return True

        return False

    def process_checkout(self, turn):
        for i in range(self._height):
            for j in range(self._width):
                if self._array[i][j] <= turn:
                    self._array[i][j] = 0


task: Task


def start(problem_no):
    global task
    task = Task(problem_no)


def get_turn():
    return task.get_turn()


def get_new_requests() -> list[dict[str, int]]:
    return task.get_new_requests()


def reply(replies):
    task.put_reply(replies)


def simulate(room_assign):
    task.simulate(room_assign)


def get_score():
    return task.get_score()


__all__ = ["get_turn", "start", "get_new_requests", "reply", "simulate", "get_score"]
