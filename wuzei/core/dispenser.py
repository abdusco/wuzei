from random import shuffle


class Dispenser:
    def __init__(self, things: list, shuffled: bool = False, delta: int = 1):
        self.things = sorted(things)
        self.shuffled = shuffled
        self.delta = delta
        self.pos, self.max = 0, len(things)
        if shuffled:
            self.shuffle()

    @property
    def current(self):
        return self.things[self.pos]

    def shuffle(self):
        temp = self.things[self.pos]
        shuffle(self.things)
        self.pos = self.things.index(temp)
        self.shuffled = True

    def unshuffle(self):
        temp = self.things[self.pos]
        self.things = sorted(self.things)
        self.pos = self.things.index(temp)
        self.shuffled = False

    def _move(self, delta: int):
        pos = self.pos + delta
        if pos >= self.max:
            pos %= self.max
        elif pos < 0:
            pos += self.max
        self.pos = pos

    def __add__(self, delta: int):
        self._move(delta)
        return self.current

    def __sub__(self, delta: int):
        self._move(-delta)
        return self.current

    def __len__(self):
        return len(self.things)

    def __getitem__(self, i):
        return self.things[i]
