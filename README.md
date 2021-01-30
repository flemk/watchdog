# watchdog
The goal of this project is to notify the user, when there is unusual process-activity happening - this includes heavy write-usage, process-occupation and filesystem activity. This repository includes a python module for displaying information-windows.

Currently works only on windows.

Python library ```watchdog``` is used.

## ```filedog.py```
This is a very crude and basic watchdog for the local filesystem. based on the ```watchdog``` library.

## ```processdog.py```
This module allows to minitor the processes and gives alert when unusual activity is happening. Works currently only on windows, and is applied for write-use.

Use it as follows:
```python
# create a new observer instance
observer = CustomProcessObserver()
    
# load whitelist file
observer._read_whitelist_file()

# add some to whitelist if desired
observer._add_to_whitelist('python.exe')
observer._export_whitelist_file()

observer.start()
```

## ```messagebox.py```
Contains the MessageBox class.

## Problems so far
- System appears to take an unusual high amount of computing power. This might be due to treads of graphical display.
- There is only write-usage considered so far.