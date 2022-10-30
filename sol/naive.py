from task import local


class Hotel:
    def __init__(self, height, width):
        self._height = height
        self._width = width
        self._resrvs = [[[] for _ in range(width)] for _ in range(height)]

    def _is_room_reservable(self, floor, index, amount, in_date, out_date):
        for room in self._resrvs[floor][index : index+amount]:
            for resrv_in_date, resrv_out_date in room:
                if not(resrv_out_date <= in_date or out_date <= resrv_in_date):
                    return False
        return True

    class CouldNotFindEmptyRooms(ValueError):
        pass

    def _find_empty_rooms(self, amount, in_date, out_date):
        for floor in range(self._height):
            for index in range(self._width - amount):
                if self._is_room_reservable(floor, index, amount, in_date, out_date):
                    return floor, index
        raise Hotel.CouldNotFindEmptyRooms()

    def reserve(self, amount, in_date, out_date):
        try:
            floor, index = self._find_empty_rooms(amount, in_date, out_date)
        except Hotel.CouldNotFindEmptyRooms:
            raise
        for room in self._resrvs[floor][index : index+amount]:
            room.append((in_date, out_date))
        return floor, index


class Solver:
    def __init__(self, task_no):
        self._task = local.Task(task_no)

    def solve(self):
        task = self._task
        params = task.params
        hotel = Hotel(params['hotel_height'], params['hotel_width'])

        accepted_requests = []
        while not task.finished():
            reqs = task.get_new_requests()
            replies = []
            for req in reqs:
                amount = req['amount']
                in_date = req['check_in_date']
                out_date = req['check_out_date']
                try:
                    floor, index = hotel.reserve(amount, in_date, out_date)
                except Hotel.CouldNotFindEmptyRooms:
                    replies.append({
                        'id': req['id'],
                        'reply': 'refused'})
                    continue
                room_no = 1000 * (floor + 1) + (index + 1)
                accepted_requests.append({
                    'id': req['id'],
                    'check_in_date': req['check_in_date'],
                    'room_no': room_no})
                replies.append({
                    'id': req['id'],
                    'reply': 'accepted'})
            task.put_reply(replies)
            current_turn_requests = [req for req in accepted_requests
                                     if req['check_in_date'] == task.get_turn()]
            room_assign = [{
                'id': req['id'],
                'room_number': req['room_no']}
                for req in current_turn_requests]
            task.simulate(room_assign)

        print(task.get_score())


if __name__ == '__main__':
    Solver(1).solve()
    Solver(2).solve()
