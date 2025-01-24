# SPDX-FileCopyrightText: 2025 Roman Ondráček
#
# SPDX-License-Identifier: MIT

"""
`max734x`
================================================================================

CircuitPython driver for the MAX7347/MAX7348/MAX7349 keyboard and sounder
controllers.

* Author(s): Roman Ondráček

Implementation Notes
--------------------

**Hardware:**

* `MAX7347 <https://www.analog.com/en/products/max7347.html>`_
* `MAX7348 <https://www.analog.com/en/products/max7348.html>`_
* `MAX7349 <https://www.analog.com/en/products/max7349.html>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice

try:
    from digitalio import DigitalInOut
    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/Roman3349/CircuitPython_MAX734X.git"

#
# Device address and register addresses definitions
#

# Address of the device
ADDRESS_GND = const(0b0111000)
ADDRESS_VCC = const(0b0111010)
ADDRESS_SDA = const(0b0111100)
ADDRESS_SCL = const(0b0111110)

# Register addresses
_REG_KEYS          = const(0x00)
_REG_DEBOUNCE      = const(0x01)
_REG_AUTOREPEAT    = const(0x02)
_REG_INTERRUPT     = const(0x03)
_REG_CONFIGURATION = const(0x04)
_REG_PORT          = const(0x05)
_REG_KEY_SOUND     = const(0x06)
_REG_ALERT_SOUND   = const(0x07)

#
# Keys FIFO register definitions
#

# Keys FIFO
_KEYS_FIFO_OVERFLOW_MASK = const(0b10000000)
_KEYS_FIFO_NOT_OVERFLOW  = const(0b00000000)
_KEYS_FIFO_OVERFLOW      = const(0b10000000)

_KEYS_FIFO_LAST_MASK = const(0b01000000)
_KEYS_FIFO_NOT_LAST  = const(0b00000000)
_KEYS_FIFO_LAST      = const(0b01000000)

_KEYS_FIFO_KEY_MASK = const(0b00111111)

#
# Debounce register definitions
#

# Debounce port enable
_DEBOUNCE_ENABLE_MASK       = const(0b11100000)
_DEBOUNCE_DISABLE           = const(0b00000000)
_DEBOUNCE_ENABLE_PORT7      = const(0b00100000)
_DEBOUNCE_ENABLE_PORT67     = const(0b01000000)
_DEBOUNCE_ENABLE_PORT567    = const(0b01100000)
_DEBOUNCE_ENABLE_PORT4567   = const(0b10000000)
_DEBOUNCE_ENABLE_PORT34567  = const(0b10100000)
_DEBOUNCE_ENABLE_PORT234567 = const(0b11100000)
_DEBOUNCE_ENABLE_DEFAULT    = _DEBOUNCE_ENABLE_PORT234567

# Debounce time in milliseconds
_DEBOUNCE_TIME_MASK = const(0b00011111)
_DEBOUNCE_TIME_MIN     = const(9)
_DEBOUNCE_TIME_MAX     = const(40)
_DEBOUNCE_TIME_DEFAULT = 40

#
# Auto-repeat register definitions
#

# Auto-repeat enable
_AUTOREPEAT_ENABLE_MASK = const(0b10000000)
_AUTOREPEAT_ENABLE      = const(0b10000000)
_AUTOREPEAT_DISABLE     = const(0b00000000)

# Auto-repeat frequency in debounce cycles
_AUTOREPEAT_FREQUENCY_MASK = const(0b01110000)
_AUTOREPEAT_FREQUENCY_4    = const(0b00000000)
_AUTOREPEAT_FREQUENCY_8    = const(0b00010000)
_AUTOREPEAT_FREQUENCY_12   = const(0b00100000)
_AUTOREPEAT_FREQUENCY_16   = const(0b00110000)
_AUTOREPEAT_FREQUENCY_20   = const(0b01000000)
_AUTOREPEAT_FREQUENCY_24   = const(0b01010000)
_AUTOREPEAT_FREQUENCY_28   = const(0b01100000)
_AUTOREPEAT_FREQUENCY_32   = const(0b01110000)

# Auto-repeat delay in debounce cycles
_AUTOREPEAT_DELAY_MASK = const(0b00001111)
_AUTOREPEAT_DELAY_8    = const(0b00000000)
_AUTOREPEAT_DELAY_16   = const(0b00000001)
_AUTOREPEAT_DELAY_24   = const(0b00000010)
_AUTOREPEAT_DELAY_32   = const(0b00000011)
_AUTOREPEAT_DELAY_40   = const(0b00000100)
_AUTOREPEAT_DELAY_48   = const(0b00000101)
_AUTOREPEAT_DELAY_56   = const(0b00000110)
_AUTOREPEAT_DELAY_64   = const(0b00000111)
_AUTOREPEAT_DELAY_72   = const(0b00001000)
_AUTOREPEAT_DELAY_80   = const(0b00001001)
_AUTOREPEAT_DELAY_88   = const(0b00001010)
_AUTOREPEAT_DELAY_96   = const(0b00001011)
_AUTOREPEAT_DELAY_104  = const(0b00001100)
_AUTOREPEAT_DELAY_112  = const(0b00001101)
_AUTOREPEAT_DELAY_120  = const(0b00001110)
_AUTOREPEAT_DELAY_128  = const(0b00001111)

#
# Interrupt register definitions
#

# TODO: Implement interrupt register definitions

#
# Configuration register definitions
#

# Serial interface bus timeout
_CONFIGURATION_BUS_TIMEOUT_MASK    = const(0b00000001)
_CONFIGURATION_BUS_TIMEOUT_ENABLE  = const(0b00000000)
_CONFIGURATION_BUS_TIMEOUT_DISABLE = const(0b00000001)

# Sounder status
_CONFIGURATION_SOUNDER_STATUS_MASK = const(0b00000110)
_CONFIGURATION_SOUNDER_OFF         = const(0b00000000)
_CONFIGURATION_SOUNDER_SERIAL      = const(0b00000010)
_CONFIGURATION_SOUNDER_DEBOUNCE    = const(0b00000100)
_CONFIGURATION_SOUNDER_ALERT       = const(0b00000110)

# Alert IRQ event
_CONFIGURATION_ALERT_IRQ_EVENT_MASK                 = const(0b00001000)
_CONFIGURATION_ALERT_IRQ_EVENT_ASSERTED_ON_KEY_SCAN = const(0b00000000)
_CONFIGURATION_ALERT_IRQ_EVENT_ASSERTED_IMMEDIATELY = const(0b00001000)

# Alert IRQ enable
_CONFIGURATION_ALERT_IRQ_ENABLE_MASK = const(0b00010000)
_CONFIGURATION_ALERT_IRQ_ENABLE      = const(0b00010000)
_CONFIGURATION_ALERT_IRQ_DISABLE     = const(0b00000000)

# Alert sound enable
_CONFIGURATION_ALERT_SOUND_ENABLE_MASK = const(0b00100000)
_CONFIGURATION_ALERT_SOUND_DISABLE     = const(0b00000000)
_CONFIGURATION_ALERT_SOUND_ENABLE      = const(0b00100000)

# Key sound enable
_CONFIGURATION_KEY_SOUND_ENABLE_MASK = const(0b01000000)
_CONFIGURATION_KEY_SOUND_DISABLE     = const(0b00000000)
_CONFIGURATION_KEY_SOUND_ENABLE      = const(0b01000000)

# Shutdown
_CONFIGURATION_MODE_MASK     = const(0b10000000)
_CONFIGURATION_MODE_SHUTDOWN = const(0b00000000)
_CONFIGURATION_MODE_NORMAL   = const(0b10000000)


#
# Port register definitions
#

# TODO: Implement port register definitions

#
# Sounder register definitions
#

_SOUNDER_DISABLE = const(0b00000000)
_SOUNDER_DEFAULT = _SOUNDER_DISABLE

# Sounder buffer
_SOUNDER_BUFFER_MASK    = const(0b00000001)
_SOUNDER_BUFFER_DISABLE = const(0b00000000)
_SOUNDER_BUFFER_ENABLE  = const(0b00000001)
_SOUNDER_BUFFER_DEFAULT = _SOUNDER_BUFFER_DISABLE

# Sounder frequency
_SOUNDER_FREQUENCY_MASK     = const(0b00011110)
_SOUNDER_OUTPUT_ACTIVE_LOW  = const(0b00000000)
_SOUNDER_OUTPUT_ACTIVE_HIGH = const(0b00000010)
_SOUNDER_FREQUENCY_C5       = const(0b00000100)
_SOUNDER_FREQUENCY_D5       = const(0b00000110)
_SOUNDER_FREQUENCY_E5       = const(0b00001000)
_SOUNDER_FREQUENCY_F5       = const(0b00001010)
_SOUNDER_FREQUENCY_G5       = const(0b00001100)
_SOUNDER_FREQUENCY_A5       = const(0b00001110)
_SOUNDER_FREQUENCY_B5       = const(0b00010000)
_SOUNDER_FREQUENCY_C6       = const(0b00010010)
_SOUNDER_FREQUENCY_E6       = const(0b00010100)
_SOUNDER_FREQUENCY_G6       = const(0b00010110)
_SOUNDER_FREQUENCY_A6       = const(0b00011000)
_SOUNDER_FREQUENCY_C7       = const(0b00011010)
_SOUNDER_FREQUENCY_D7       = const(0b00011100)
_SOUNDER_FREQUENCY_E7       = const(0b00011110)
_SOUNDER_FREQUENCY_DEFAULT  = _SOUNDER_OUTPUT_ACTIVE_LOW

# Sounder duration
_SOUNDER_DURATION_MASK       = const(0b11100000)
_SOUNDER_DURATION_CONTINUOUS = const(0b00000000)
_SOUNDER_DURATION_15625MS    = const(0b00100000)
_SOUNDER_DURATION_3125MS     = const(0b01000000)
_SOUNDER_DURATION_625MS      = const(0b01100000)
_SOUNDER_DURATION_125MS      = const(0b10000000)
_SOUNDER_DURATION_250MS      = const(0b10100000)
_SOUNDER_DURATION_500MS      = const(0b11000000)
_SOUNDER_DURATION_1000MS     = const(0b11100000)
_SOUNDER_DURATION_DEFAULT    = _SOUNDER_DURATION_CONTINUOUS




class KeysFiFo:
    """
    Keys FIFO register.

    :param bool overflow: Overflow flag.
    :param bool last: Last key flag.
    :param int row: Row of the key.
    :param int column: Column of the key.
    """

    def __init__(
        self,
        overflow: bool,
        last: bool,
        row: int,
        column: int,
    ) -> None:
        self.overflow = overflow
        self.last = last
        self.row = row
        self.column = column


    def __repr__(self) -> str:
        """
        Return a string representation of the object.
        :return: String representation of the object.
        """
        return (
            f"<KeysFiFo overflow={self.overflow} last={self.last} "
            f"row={self.row} column={self.column}>"
        )

    @staticmethod
    def from_register(value: int):
        """
        Create a new KeysFiFo object from the register value.

        :param int value: The value of the register.
        :return: The new KeysFiFo object.
        """
        return KeysFiFo(
            overflow=bool(value & _KEYS_FIFO_OVERFLOW_MASK),
            last=bool(value & _KEYS_FIFO_LAST_MASK),
            row=(value & _KEYS_FIFO_KEY_MASK) >> 3,
            column=value & _KEYS_FIFO_KEY_MASK,
        )


class MAX734X:
    """
    CircuitPython driver for the MAX7347/MAX7348/MAX7349 keyboard and sounder
    controllers.

    :param I2C i2c_bus: The I2C bus the device is connected to.
    :param int address: The I2C address of the device. Default is 0x38.
    """

    def __init__(
        self,
        i2c_bus: I2C,
        address: int = ADDRESS_GND,
    ) -> None:
        self._i2c = I2CDevice(i2c_bus, address)


    def read_keys(self) -> KeysFiFo:
        """
        Read the keys FIFO register.

        """
        buffer: bytearray = bytearray(1)
        buffer[0] = _REG_KEYS
        with self._i2c as i2c:
            i2c.write_then_readinto(
                in_buffer=buffer,
                in_end=1,
                out_buffer=buffer,
                out_end=1,
            )
        return KeysFiFo.from_register(buffer[0])