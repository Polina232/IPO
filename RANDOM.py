import numpy as np
from states import *
#рандомим возможные состояния окнечных устройств
def get_random_state(probabilities):
    last_probability = 1.0 - sum(probabilities)
    probabilities.append(last_probability)
    rand = np.random.choice(np.arange(1, len(probabilities) + 1), p=probabilities) #Случайная выборка из значений заданного одномерного массива
    if rand == 1:
        return DeviceState.GENERATOR
    elif rand == 2:
        return DeviceState.DENIAL
    elif rand == 3:
        return DeviceState.FAILURE
    elif rand == 4:
        return DeviceState.BUSY
    else:
        return DeviceState.WORKING