import sys
import os
import time
import datetime
sys.path.append(os.path.abspath('..'))

import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt

from source.market_interface import MarketInterface
from source.broker import ProsumerBroker
from source.prosumer import Prosumer

import concurrent.futures
from functools import partial

from source.constants import TMPDIR

df = pd.read_csv(TMPDIR + 'all_customers.csv')

def get_one_day_data(df, year, month, day):
    day = datetime.date(year, month, day)
    nextday = datetime.timedelta(days=1) + day
    mask_day = df['date'].between(str(day), str(nextday))
    tmp = df[mask_day]
    tmp = pd.pivot_table(tmp, index='date', columns='customer', values='power')
    return tmp

def simulation_run(seed, strategy):

    r = np.random.RandomState(seed)
    prosumers = []
    brokers = []
    mid_p = 0.5 * (PRICE_B1 + PRICE_S1)
    for i in range(N):
        LOAD = data.iloc[:, i + 1].values.copy()
        pro = Prosumer(i, BMAX, BMIN, EC, ED, DM, Dm, PRICE_B1, PRICE_S1, LOAD, mid_p, mid_p)
        prosumers.append(pro)
        broker = ProsumerBroker(pro, strategy, r=r)
        brokers.append(broker)

    market_sequence_1 = []
    for t in range(T):
        #print('--'*20)
        mi = MarketInterface()
        for i in range(N):
            mi.accept_bid(brokers[i].market_bid(t), brokers[i].market_callback)
        tr = mi.clear('muda', r=r)
        market_sequence_1.append(tr)
        
    return prosumers, brokers, market_sequence_1

data = get_one_day_data(df, 2012, 8, 6)

N = 20
T = 48
B0 = 0
BMIN = 0
BMAX = 3
EC = 0.95
ED = 0.95
DM = 1
Dm = -1

PRICE_B1 = np.ones(T) * 15.0
PRICE_B1[: T // 2] = 10.0
PRICE_S1 = np.ones(T) * 5.0



truth = partial(simulation_run, strategy='truthful')

start = time.time()

with concurrent.futures.ProcessPoolExecutor() as executor:
        res = list(executor.map(truth, range(1)))
        with open('res_new.pkl', 'wb') as fh:
            pickle.dump(res, fh)

end = time.time()

print('Elapsed time ', end - start)
