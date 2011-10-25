# O(n*log(n)) infinite version

from collections import deque
from itertools import takewhile
import sys

class Sieve:

    def __init__(self, n):
        self.n = n
        self.last = n

    def is_multiple(self, i):
        while self.last < i:
            self.last += self.n
        return (self.last == i)


def find_primes():
    sieves = deque()

    i = 2
    while True:
        if not any(s.is_multiple(i) for s in sieves):
            yield i
            sieves.append(Sieve(i))
        i += 1


if __name__ == '__main__':
    max_num = int(sys.argv[1])
    primes = [i for i in takewhile(lambda i: i < max_num,
                                   find_primes())]
    print(primes)
