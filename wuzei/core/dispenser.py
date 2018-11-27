from random import shuffle, randrange


class Dispenser:
    def __init__(self, things: list, shuffled: bool = False, delta: int = 1):
        self._things = sorted(things)
        self._shuffled = shuffled
        self._delta = delta
        self._pos, self._max = 0, len(things)
        if shuffled:
            self.shuffle()

    @property
    def current(self):
        return self._things[self._pos]

    @property
    def things(self):
        return self._things

    @things.setter
    def things(self, items):
        current = self.current
        self._things = items
        try:
            self._pos = self._things.index(current)
            return
        except ValueError:
            pass

        if self._shuffled:
            self._pos = randrange(self._max)
        else:
            self._pos = 0

    def random(self):
        self._pos = randrange(self._max)
        return self._things[self._pos]

    def shuffle(self):
        temp = self._things[self._pos]
        shuffle(self._things)
        self._pos = self._things.index(temp)
        self._shuffled = True

    def unshuffle(self):
        temp = self._things[self._pos]
        self._things = sorted(self._things)
        self._pos = self._things.index(temp)
        self._shuffled = False

    def _move(self, delta: int):
        pos = self._pos + delta
        if pos >= self._max:
            pos %= self._max
        elif pos < 0:
            pos += self._max
        self._pos = pos

    def __add__(self, delta: int):
        self._move(delta)
        return self.current

    def __sub__(self, delta: int):
        self._move(-delta)
        return self.current

    def __len__(self):
        return len(self._things)

    def __getitem__(self, i):
        return self._things[i]
