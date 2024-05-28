import numpy as np

def average(signal:list[float]) -> float: return round(sum(signal)/len(signal), 4)
def rms(signal:list[float]) -> float: return round(np.sqrt(np.sum(np.square(signal))/len(signal)), 4)