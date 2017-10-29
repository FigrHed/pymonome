#! /usr/bin/env python3
#
# based on life64.ck monome app by tehn

import asyncio
import monome
import copy, itertools, random

class Life(monome.App):
    def __init__(self):
        super().__init__() # TODO: prefix
        self.alive = True

    def on_grid_ready(self):
        self.world = [[0 for col in range(self.grid.width)] for row in range(self.grid.height)]
        self.randomize()
        self.task = asyncio.async(self.begin())

    def on_grid_disconnect(self):
        self.task.cancel()

    def on_grid_key(self, x, y, s):
        if x == self.grid.width - 1 and y == 0 and s == 1:
            self.alive = not self.alive
            self.grid.led_set(self.grid.width - 1, 0, int(not self.alive))
            return
        if s == 1:
            row, col = y, x
            self.world[row][col] ^= 1
            self.grid.led_set(x, y, self.world[row][col])

    def quit(self):
        self.task.cancel()

    async def begin(self):
        try:
            while True:
                if self.alive:
                    self.update()
                    for i, row in enumerate(self.world):
                        self.grid.led_row(0, i, row)
                await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            pass

    def update(self):
        def neighbors(x, y):
            result = 0
            for dx, dy in [d for d in itertools.product([-1, 0, 1], repeat=2) if d != (0, 0)]:
                row = (y + dy) % self.grid.height
                col = (x + dx) % self.grid.width
                result += self.world[row][col]
            return result

        new_world = copy.deepcopy(self.world)
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                n = neighbors(x, y)
                row, col = y, x
                if n == 3:
                    new_world[row][col] = 1
                elif (n < 2 or n > 3):
                    new_world[row][col] = 0
        self.world = copy.deepcopy(new_world)

    def randomize(self):
        for row in range(self.grid.height):
            for col in range(self.grid.width):
                self.world[row][col] = random.randint(0, 1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    life_app = Life()
    asyncio.async(monome.SerialOsc.create(loop=loop, autoconnect_app=life_app))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        life_app.quit()
