from random import uniform


def random_sleep_time(min_time: float = 1, max_time: float = 5) -> float:
    return round(uniform(min_time, max_time), 4)
