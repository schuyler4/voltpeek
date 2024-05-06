import sys
sys.path.append('..')

import time

from voltpeek.reconstruct import reconstruct
from voltpeek.pixel_vector import quantize_vertical, FIR_filter, resample_horizontal
from voltpeek.scope_specs import scope_specs

xx = [200 for _ in range(0, scope_specs['memory_depth'])]

start_time = time.time()
amplitude_reconstructed_signal = reconstruct(xx, scope_specs, 10)
filtered_signal = FIR_filter(amplitude_reconstructed_signal)
display_reconstructed_signal = quantize_vertical(filtered_signal, 10)
display_signal = resample_horizontal(display_reconstructed_signal, 0.001, scope_specs['sample_rate'])

print(time.time() - start_time)