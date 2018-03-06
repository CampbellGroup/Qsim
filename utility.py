import numpy as np


def counts_to_hist(self, counts, repititions):
    data = np.column_stack((np.arange(repititions), counts))
    y = np.histogram(data[:, 1],
                     int(np.max([data[:, 1].max() - data[:, 1].min(), 1])))
    counts = y[0]
    bins = y[1][:-1]
    if bins[0] < 0:
        bins = bins + .5
        hist = np.column_stack((bins, counts))
    return hist
