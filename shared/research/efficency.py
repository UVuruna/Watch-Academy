import time
import functools


class measure:
    def __init__(self, METHOD: callable):
        self.METHOD = METHOD

    @staticmethod
    def methodEfficency(
        measure_methods: iter = (time.time_ns, time.monotonic_ns,
                                 time.perf_counter_ns, time.thread_time_ns, time.process_time_ns)
    ):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_process = []
                end_process = []
                timings = dict()
                names = []
                for meth in measure_methods:
                    name = str(meth).split(' ')[-1]
                    name = name[:-1].replace('_', ' ')
                    names.append(name.title())
                for meth in measure_methods:
                    start_process.append(meth())
                result = func(*args, **kwargs)
                for meth in measure_methods:
                    end_process.append(meth())
                for n, (s, e) in zip(names, zip(start_process, end_process)):
                    timings[n] = (e-s) / 10**6
                return result, timings
            return wrapper
        return decorator

    def measuringOverTime(
        self,
        seconds: float,
        measuring: callable = time.perf_counter_ns
    ):
        START = time.time()
        Time = []
        while time.time()-START < seconds:
            start = measuring()
            self.METHOD()
            Time.append((measuring()-start) / 10**6)
        return {
            'Total Iterations':len(Time),
            'Average execution': sum(Time)/len(Time),
            'Longest execution': max(Time),
            'Shortest execution': min(Time)
            }


if __name__ == '__main__':

    def time_test():
        x = 0
        y = 0
        SUM = 0
        for _ in range(10**6):
            x += 1
            y -= 1
            SUM *= x/y
            SUM /= x*y
            SUM += x-y
            SUM -= x+y

    decoratedFUNC = measure.methodEfficency()(time_test)
    print(decoratedFUNC())
    
    test = measure(time_test)
    print(test.measuringOverTime(4))
