import numpy as np

def data_average(preamble, experiment, datasets):
    for i, item in enumerate(datasets):
        item = str(item)
        if len(item) < 5:
            item = (5 -len(item))*'0' + item
        temp = np.loadtxt(preamble + item  + ' - ' + experiment + '.csv', delimiter=',')
        if i != 0:
            prev_y = temp[:,1] + prev_y
        else:
            x_values = temp[:,0]
            prev_y = temp[:,1]
    y_values = prev_y/len(datasets)
    return [x_values, y_values]

def get_data(preamble, experiment, data_set):
    data_set = str(data_set)
    if len(data_set) < 5:
        data_set = (5 -len(data_set))*'0' + data_set
    temp = np.loadtxt(preamble + data_set  + ' - ' + experiment + '.csv', delimiter=',')
    x_values = temp[:,0]
    y_values = temp[:,1]
    return [x_values, y_values]
