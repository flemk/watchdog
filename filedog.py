import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

import threading
from messagebox import MsgBox

class CustomEventHandler(LoggingEventHandler):
    #def dispatch(self, event):
    #    print('something changed')
    
    def on_modified(self, event):
        print(event)
        b = MsgBox('wachtog wraning', event, 'alert')
        b.show()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    event_handler = CustomEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
