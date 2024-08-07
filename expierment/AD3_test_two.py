from threading import Thread

import sys
sys.path.append('..')

from voltpeek.scopes import AD3

def scope_thread():
    print('starting')
    ad3 = AD3()
    ad3.connect()
    print(ad3.get_scope_force_trigger_data(1))

thread: Thread = Thread(target=scope_thread)   
thread.start()