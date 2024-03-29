import sys
import os
import time
import datetime
import numpy as np
import pandas as pd
import pickle

import matplotlib.pyplot as plt
sys.path.append(os.path.abspath('.'))
from source.constants import TMPDIR, PROJECTDIR
from copy import deepcopy
from source.market_interface import MarketInterface
from source.broker import ProsumerBroker
from source.prosumer import Prosumer
import concurrent.futures
from functools import partial


df = pd.read_csv(TMPDIR + 'all_customers.csv')

N = 50
T = 48
B0 = 0
BMIN = 0
BMAX = 3
EC = 0.95
ED = 0.95
DM = 1
Dm = -1
seed=69

PRICE_B1 = np.ones(T) * 15.0
PRICE_B1[: T // 2] = 10.0
PRICE_S1 = np.ones(T) * 5.0

def get_one_day_data(df, day):
    nextday = datetime.timedelta(days=1) + day
    mask_day = df['date'].between(str(day), str(nextday))
    tmp = df[mask_day]
    tmp = pd.pivot_table(tmp, index='date', columns='customer', values='power')
    return tmp


if __name__ == '__main__':

    UPDATE_TYPE = sys.argv[1]
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    day = int(sys.argv[4])

    day_ = datetime.date(year, month, day)
    data = get_one_day_data(df, day_)

    start = time.time()

    r = np.random.RandomState(seed)
    prosumers = []
    brokers = []
    mid_p = 0.5 * (PRICE_B1 + PRICE_S1)
    for i in range(N):
        LOAD = data.iloc[:, i + 1].values.copy()
        pro = Prosumer(i, BMAX, BMIN, EC, ED, DM, Dm, PRICE_B1, PRICE_S1, LOAD, PRICE_B1, PRICE_S1, UPDATE_TYPE)
        prosumers.append(pro)
        broker = ProsumerBroker(pro,'truthful', r=r)
        brokers.append(broker)

    market_sequence_1 = []
    for t in range(T):
        mi = MarketInterface()
        for i in range(N):
            mi.accept_bid(brokers[i].market_bid(t), brokers[i].market_callback)
        tr = mi.clear('muda', r=r)
        market_sequence_1.append(deepcopy(mi))

    end = time.time()


    NAME = f"simres_{UPDATE_TYPE}_1day_{year}_{month}_{day}.pkl"
    with open(TMPDIR + NAME, "wb") as fh: pickle.dump([prosumers, brokers, market_sequence_1], fh)


    print('Elapsed time ', end - start)
