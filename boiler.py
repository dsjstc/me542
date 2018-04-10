import pandas as pd

# The boiler is about what you'd expect.  Features
# -- 100% efficient
# -- Max load 10 kW, which I haven't bothered with.

class Boiler:
    def apply(self, data):
        df = self.df = data
        df.cons = df.cons + df.rload
        df.rload = 0
