import time

import usb.core
import usb.util

dev = usb.core.find(idVendor=0xCAFE,idProduct=0x4004)

if dev is None:
    raise ValueError('Newt Scope Not Connected')

i = dev[0].interfaces()[0].bInterfaceNumber

dev.reset()

if dev.is_kernel_driver_active(i):
    dev.detach_kernel_driver(i)

dev.set_configuration()

config = dev.get_active_configuration()
interface = config[(0, 0)]

def out_endpoint_match(e):
    return usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT

def in_endpoint_match(e):
    return usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN

endpoint_out = usb.util.find_descriptor(interface, custom_match=out_endpoint_match)
endpoint_in = usb.util.find_descriptor(interface, custom_match=in_endpoint_match)

assert endpoint_in is not None
assert endpoint_out is not None

start_time = time.time()
for _ in range(0, 20):
    ret = dev.write(endpoint_out, 'f')
    ret2 = dev.read(endpoint_in, 64)
print(time.time() - start_time)
print(ret2)

