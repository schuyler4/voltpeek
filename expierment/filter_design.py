import numpy as np
import matplotlib.pyplot as plt
N = 2
n_samples = 100
hh = np.array([1/N for _ in range(0, N)])
step = np.ones(n_samples)
response = np.convolve(step, hh)
