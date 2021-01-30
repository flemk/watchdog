import numpy as np
import wmi
import pickle
import threading
import time

from messagebox import MsgBox

class CustomProcessObserver:
    def __init__(self):
        self._handler = wmi.WMI()
        self._last_state = {}
        self._whitelist = []
        self._whitelist_filename = './processdog_whitelist.pkl'
        self._interval = 120 # seconds

        # convert state-variable to int: state-int-converter
        self._sic = lambda value: int(value) if value is not None else 0

    def _get_state(self):
        ''' receives a set of currntly active processes and
        extracts particular informations about them and returns them
        '''
        r = {}
        for process in self._handler.Win32_Process():
            r[process.ProcessId] = {'name': process.Name,
                                    'creation_date': process.CreationDate,
                                    'max_working_size': process.MaximumWorkingSetSize,
                                    'min_working_size': process.MinimumWorkingSetSize,
                                    'priority': process.Priority,
                                    'private_page_count': process.PrivatePageCount,
                                    'quota_paged_pool_usage': process.QuotaPagedPoolUsage,
                                    'read_operation_count': process.ReadOperationCount,
                                    'read_transfer_count': process.ReadTransferCount,
                                    'thread_count': process.ThreadCount,
                                    'virtual_size': process.VirtualSize,
                                    'write_operation_count': process.WriteOperationCount,
                                    'write_transfer_count': process.WriteTransferCount
                                   }

        #self._last_state = r
        
        return r

    def _differentiate_states(self, last_state, current_state):
        ''' calculates the differences of PIDs in both states,
        the previous and the current one if PID is in both sets.

        Returns:
            - (np.array) r: array of processes which changed in any catecories,
                except 'pid' and 'name' with the differences as values.
        '''
        last_state_pid = [pid for pid, _ in last_state.items()]
        current_state_pid = [pid for pid, _ in current_state.items()]

        process = np.intersect1d(last_state_pid, current_state_pid)

        r = {}
        for pid in process:
            l = last_state[pid]
            c = current_state[pid]

            d = {
                'max_working_size': self._sic(l['max_working_size']) - self._sic(c['max_working_size']),
                'min_working_size': self._sic(l['min_working_size']) - self._sic(c['min_working_size']),
                'priority': self._sic(l['priority']) - self._sic(c['priority']),
                'private_page_count': self._sic(l['private_page_count']) - self._sic(c['private_page_count']),
                'quota_paged_pool_usage': self._sic(l['quota_paged_pool_usage']) - self._sic(c['quota_paged_pool_usage']),
                'read_operation_count': self._sic(l['read_operation_count']) - self._sic(c['read_operation_count']),
                'read_transfer_count': self._sic(l['read_transfer_count']) - self._sic(c['read_transfer_count']),
                'thread_count': self._sic(l['thread_count']) - self._sic(c['thread_count']),
                'virtual_size': self._sic(l['virtual_size']) - self._sic(c['virtual_size']),
                'write_operation_count': self._sic(l['write_operation_count']) - self._sic(c['write_operation_count']),
                'write_transfer_count': self._sic(l['write_transfer_count']) - self._sic(c['write_transfer_count'])
            }
            if not np.sum([v for _, v in d.items()]): continue

            r[pid] = {'name': c['name'],
                      'creation_date': 0 if l['creation_date'] == c['creation_date'] else c['creation_date'],

                      'max_working_size': d['max_working_size'],
                      'min_working_size': d['min_working_size'],
                      'priority': d['priority'],
                      'private_page_count': d['private_page_count'],
                      'quota_paged_pool_usage': d['quota_paged_pool_usage'],
                      'read_operation_count': d['read_operation_count'],
                      'read_transfer_count': d['read_transfer_count'],
                      'thread_count': d['thread_count'],
                      'virtual_size': d['virtual_size'],
                      'write_operation_count': d['write_operation_count'],
                      'write_transfer_count': d['write_transfer_count']
                     }
        # Now append to r the newly to current_state added processes
        for pid in current_state_pid:
            if pid in process: continue
            r[pid] = current_state[pid]
        
        return r
    
    def _evaluate_differences(self, difference):
        ''' returns suspicious changes in process-difference
        '''
        difference = self._apply_whitelist_file(difference)

        for k, v in difference.items():
            if self._sic(v['write_operation_count']) > 10:
                def alert(pid, process_name, write_operation_count):
                    b = MsgBox('watchog warning', '[PID:%s] Process %s write_count incremented by %i' % (pid, process_name, write_operation_count), 'alert')
                    b.show()
                x = threading.Thread(target=alert, args=(k, v['name'], self._sic(v['write_operation_count'])))
                x.start()

    def _apply_whitelist_file(self, state):
        ''' removes proces to ignore by self._whitelist by name

        Returns:
            - (dict) state: filtered state
        '''
        deletables = []
        for k, v in state.items():
            if v['name'] in self._whitelist:
                deletables.append(k)

        for pid in deletables:
            del state[pid]
        
        return state

    def _add_to_whitelist(self, process_name: str):
        ''' adds process_name to whitelist list 
        
        checks first if process_name is not already in list
        '''
        if not process_name in self._whitelist:
            self._whitelist.append(process_name)

    def _read_whitelist_file(self):
        ''' reads the processes ignote file

        this must be in the executable file path
        whitelist file must be named ./processdog_whitelist.pkl
        '''
        try:
            self._whitelist = pickle.load(open(self._whitelist_filename, 'rb'))
        except FileNotFoundError:
            print('File %s could not be found.' % (self._whitelist_filename))
            return 1

    def _export_whitelist_file(self):
        ''' exports process whitelist list
        '''
        with open(self._whitelist_filename, 'wb') as file:
            pickle.dump(self._whitelist, file, pickle.HIGHEST_PROTOCOL)

    def _read_state(self, filename: str):
        ''' reads last state and saves it in class instance
        '''
        try:
            self._last_state = pickle.load(open(filename, 'rb'))
        except FileNotFoundError:
            print('File %s could not be found.' % (filename))
            return 1

    def _export_state(self, filename: str):
        ''' exports last process read state as pkl file
        '''
        with open(filename, 'wb') as file:
            pickle.dump(self._last_state, file, pickle.HIGHEST_PROTOCOL)

    def start(self):
        ''' starts surveillance
        '''
        try:
            while True:
                current_state = self._get_state()
                differentiated_states = self._differentiate_states(self._last_state, current_state)
                
                self._evaluate_differences(differentiated_states)

                self._last_state = current_state
                observer._export_state('./_last_state.pkl')

                time.sleep(self._interval)
                print('DEBUG MESSAGE LOOP')
        except KeyboardInterrupt:
            print('Processdog interrupted')

if __name__ == '__main__':
    observer = CustomProcessObserver()
    
    # read ignore file
    observer._read_whitelist_file()

    # add to ignore
    #observer._add_to_whitelist('chrome.exe')
    #observer._add_to_whitelist('python.exe')
    #observer._add_to_whitelist('conhost.exe')
    #observer._export_whitelist_file()

    observer.start()