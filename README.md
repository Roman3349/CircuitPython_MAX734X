# CircuitPython MAX7347/MAX7348/MAX7349 Library

CircuitPython driver for the MAX7347/MAX7348/MAX7349 keyboard and sounder controllers.

## Dependencies

This driver depends on:

 - [Adafruit CircuitPython](https://github.com/adafruit/circuitpython)
 - [Bus Device](https://github.com/adafruit/Adafruit_CircuitPython_BusDevice)
 - [Register](https://github.com/adafruit/Adafruit_CircuitPython_Register)

## Installing from PyPI

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally from [PyPI](https://pypi.org/project/circuitpython-max734x/).

To install in a virtual environment in your current project:
```bash
mkdir project-name && cd project-name
python3 -m venv venv
source venv/bin/activate
pip3 install circuitpython-max734x
```

## Usage Example


```python
import busio
import max734x

from board import *
i2c = board.I2C()   # uses board.SCL and board.SDA

controller = max734x.MAX734X(i2c)
```
