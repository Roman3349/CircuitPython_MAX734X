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

from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

try:
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
_REG_KEYS = const(0x00)
_REG_DEBOUNCE = const(0x01)
_REG_AUTOREPEAT = const(0x02)
_REG_INTERRUPT = const(0x03)
_REG_CONFIGURATION = const(0x04)
_REG_PORT = const(0x05)
_REG_KEY_SOUND = const(0x06)
_REG_ALERT_SOUND = const(0x07)

#
# Keys FIFO register definitions
#

# Keys FIFO
_KEYS_FIFO_OVERFLOW_MASK = const(0b10000000)
_KEYS_FIFO_NOT_OVERFLOW = const(0b00000000)
_KEYS_FIFO_OVERFLOW = const(0b10000000)

_KEYS_FIFO_LAST_MASK = const(0b01000000)
_KEYS_FIFO_NOT_LAST = const(0b00000000)
_KEYS_FIFO_LAST = const(0b01000000)

_KEYS_FIFO_KEY_MASK = const(0b00111111)

#
# Debounce register definitions
#

# Debounce port enable
_DEBOUNCE_OUTPUT_ENABLE_MASK = const(0b11100000)
_DEBOUNCE_OUTPUT_DISABLE = const(0b00000000)
_DEBOUNCE_OUTPUT_ENABLE_PORT7 = const(0b00100000)
_DEBOUNCE_OUTPUT_ENABLE_PORT67 = const(0b01000000)
_DEBOUNCE_OUTPUT_ENABLE_PORT567 = const(0b01100000)
_DEBOUNCE_OUTPUT_ENABLE_PORT4567 = const(0b10000000)
_DEBOUNCE_OUTPUT_ENABLE_PORT34567 = const(0b10100000)
_DEBOUNCE_OUTPUT_ENABLE_PORT234567 = const(0b11100000)
_DEBOUNCE_OUTPUT_ENABLE_DEFAULT = _DEBOUNCE_OUTPUT_ENABLE_PORT234567

# Debounce time in milliseconds
_DEBOUNCE_TIME_MASK = const(0b00011111)
_DEBOUNCE_TIME_MIN = const(9)
_DEBOUNCE_TIME_MAX = const(40)
_DEBOUNCE_TIME_DEFAULT = 40

#
# Auto-repeat register definitions
#

# Auto-repeat enable
_AUTOREPEAT_ENABLE_MASK = const(0b10000000)
_AUTOREPEAT_ENABLE = const(0b10000000)
_AUTOREPEAT_DISABLE = const(0b00000000)

# Auto-repeat frequency in debounce cycles
_AUTOREPEAT_FREQUENCY_MASK = const(0b01110000)
_AUTOREPEAT_FREQUENCY_4 = const(0b00000000)
_AUTOREPEAT_FREQUENCY_8 = const(0b00010000)
_AUTOREPEAT_FREQUENCY_12 = const(0b00100000)
_AUTOREPEAT_FREQUENCY_16 = const(0b00110000)
_AUTOREPEAT_FREQUENCY_20 = const(0b01000000)
_AUTOREPEAT_FREQUENCY_24 = const(0b01010000)
_AUTOREPEAT_FREQUENCY_28 = const(0b01100000)
_AUTOREPEAT_FREQUENCY_32 = const(0b01110000)

# Auto-repeat delay in debounce cycles
_AUTOREPEAT_DELAY_MASK = const(0b00001111)
_AUTOREPEAT_DELAY_8 = const(0b00000000)
_AUTOREPEAT_DELAY_16 = const(0b00000001)
_AUTOREPEAT_DELAY_24 = const(0b00000010)
_AUTOREPEAT_DELAY_32 = const(0b00000011)
_AUTOREPEAT_DELAY_40 = const(0b00000100)
_AUTOREPEAT_DELAY_48 = const(0b00000101)
_AUTOREPEAT_DELAY_56 = const(0b00000110)
_AUTOREPEAT_DELAY_64 = const(0b00000111)
_AUTOREPEAT_DELAY_72 = const(0b00001000)
_AUTOREPEAT_DELAY_80 = const(0b00001001)
_AUTOREPEAT_DELAY_88 = const(0b00001010)
_AUTOREPEAT_DELAY_96 = const(0b00001011)
_AUTOREPEAT_DELAY_104 = const(0b00001100)
_AUTOREPEAT_DELAY_112 = const(0b00001101)
_AUTOREPEAT_DELAY_120 = const(0b00001110)
_AUTOREPEAT_DELAY_128 = const(0b00001111)

#
# Interrupt register definitions
#
_INTERRUPT_KEY_SCAN_INT_FREQ_MASK = const(0b00011111)
_INTERRUPT_KEY_SCAN_EVENT_MASK = const(0b00100000)
_INTERRUPT_ALERT_EVENT_MASK = const(0b01000000)
_INTERRUPT_INT_STATUS_MASK = const(0b10000000)

#
# Configuration register definitions
#

# Serial interface bus timeout
_CONFIGURATION_BUS_TIMEOUT_MASK = const(0b00000001)
_CONFIGURATION_BUS_TIMEOUT_ENABLE = const(0b00000000)
_CONFIGURATION_BUS_TIMEOUT_DISABLE = const(0b00000001)

# Sounder status
_CONFIGURATION_SOUNDER_STATUS_MASK = const(0b00000110)
CONFIGURATION_SOUNDER_OFF = const(0b00000000)
CONFIGURATION_SOUNDER_SERIAL = const(0b00000010)
CONFIGURATION_SOUNDER_DEBOUNCE = const(0b00000100)
CONFIGURATION_SOUNDER_ALERT = const(0b00000110)

# Alert IRQ event
_CONFIGURATION_ALERT_IRQ_EVENT_MASK = const(0b00001000)
_CONFIGURATION_ALERT_IRQ_EVENT_ASSERTED_ON_KEY_SCAN = const(0b00000000)
_CONFIGURATION_ALERT_IRQ_EVENT_ASSERTED_IMMEDIATELY = const(0b00001000)

# Alert IRQ enable
_CONFIGURATION_ALERT_IRQ_ENABLE_MASK = const(0b00010000)
_CONFIGURATION_ALERT_IRQ_ENABLE = const(0b00010000)
_CONFIGURATION_ALERT_IRQ_DISABLE = const(0b00000000)

# Alert sound enable
_CONFIGURATION_ALERT_SOUND_ENABLE_MASK = const(0b00100000)
_CONFIGURATION_ALERT_SOUND_DISABLE = const(0b00000000)
_CONFIGURATION_ALERT_SOUND_ENABLE = const(0b00100000)

# Key sound enable
_CONFIGURATION_KEY_SOUND_ENABLE_MASK = const(0b01000000)
_CONFIGURATION_KEY_SOUND_DISABLE = const(0b00000000)
_CONFIGURATION_KEY_SOUND_ENABLE = const(0b01000000)

# Shutdown
_CONFIGURATION_MODE_MASK = const(0b10000000)
_CONFIGURATION_MODE_SHUTDOWN = const(0b00000000)
_CONFIGURATION_MODE_NORMAL = const(0b10000000)


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
_SOUNDER_BUFFER_MASK = const(0b00000001)

# Sounder output
_SOUNDER_OUTPUT_FREQUENCY_MASK = const(0b00011110)
SOUNDER_OUTPUT_ACTIVE_LOW = const(0b00000000)
SOUNDER_OUTPUT_ACTIVE_HIGH = const(0b00000010)
SOUNDER_OUTPUT_FREQUENCY_C5 = const(0b00000100)
SOUNDER_OUTPUT_FREQUENCY_D5 = const(0b00000110)
SOUNDER_OUTPUT_FREQUENCY_E5 = const(0b00001000)
SOUNDER_OUTPUT_FREQUENCY_F5 = const(0b00001010)
SOUNDER_OUTPUT_FREQUENCY_G5 = const(0b00001100)
SOUNDER_OUTPUT_FREQUENCY_A5 = const(0b00001110)
SOUNDER_OUTPUT_FREQUENCY_B5 = const(0b00010000)
SOUNDER_OUTPUT_FREQUENCY_C6 = const(0b00010010)
SOUNDER_OUTPUT_FREQUENCY_E6 = const(0b00010100)
SOUNDER_OUTPUT_FREQUENCY_G6 = const(0b00010110)
SOUNDER_OUTPUT_FREQUENCY_A6 = const(0b00011000)
SOUNDER_OUTPUT_FREQUENCY_C7 = const(0b00011010)
SOUNDER_OUTPUT_FREQUENCY_D7 = const(0b00011100)
SOUNDER_OUTPUT_FREQUENCY_E7 = const(0b00011110)
SOUND_OUTPUT_FREQUENCY_DEFAULT = SOUNDER_OUTPUT_ACTIVE_LOW

# Sounder duration
_SOUND_DURATION_MASK = const(0b11100000)
SOUND_DURATION_CONTINUOUS = const(0b00000000)
SOUND_DURATION_15625MS = const(0b00100000)
SOUND_DURATION_3125MS = const(0b01000000)
SOUND_DURATION_625MS = const(0b01100000)
SOUND_DURATION_125MS = const(0b10000000)
SOUND_DURATION_250MS = const(0b10100000)
SOUND_DURATION_500MS = const(0b11000000)
SOUND_DURATION_1000MS = const(0b11100000)
SOUND_DURATION_DEFAULT = SOUND_DURATION_CONTINUOUS


class Configuration:
    """
    Configuration register.

    :param bool bus_timeout_enabled: Serial interface bus timeout.
    :param int active_sounder_output: Active sounder output is set by ...
    :param bool alert_irq_enabled: Alert input IRQ enable.
    :param bool alert_irq_immediately: Alert input IRQ is asserted immediately.
    :param bool alert_sound_enabled: Alert sound enable.
    :param bool key_sound_enabled: Key sound enable.
    :param bool shutdown: Shutdown mode.
    """

    def __init__(
        self,
        bus_timeout_enabled: bool = True,
        active_sounder_output: int = CONFIGURATION_SOUNDER_OFF,
        alert_irq_enabled: bool = False,
        alert_irq_immediately: bool = False,
        alert_sound_enabled: bool = False,
        key_sound_enabled: bool = False,
        shutdown: bool = False,
    ) -> None:
        self.bus_timeout_enabled = bus_timeout_enabled
        self.active_sounder_output = active_sounder_output
        self.alert_irq_enabled = alert_irq_enabled
        self.alert_irq_immediately = alert_irq_immediately
        self.alert_sound_enabled = alert_sound_enabled
        self.key_sound_enabled = key_sound_enabled
        self.shutdown = shutdown

    def __repr__(self) -> str:
        """
        Return a string representation of the configuration object.
        :return: String representation of the configuration object.
        """
        if self.active_sounder_output == CONFIGURATION_SOUNDER_OFF:
            active_sounder_output = "off"
        elif self.active_sounder_output == CONFIGURATION_SOUNDER_SERIAL:
            active_sounder_output = "serial interface"
        elif self.active_sounder_output == CONFIGURATION_SOUNDER_DEBOUNCE:
            active_sounder_output = "key press"
        elif self.active_sounder_output == CONFIGURATION_SOUNDER_ALERT:
            active_sounder_output = "alert event"
        else:
            active_sounder_output = "unknown"
        return (
            f"<MAX734XConfiguration bus_timeout_enabled={self.bus_timeout_enabled} "
            + f"active_sounder_output={active_sounder_output} "
            + f"alert_irq_enabled={self.alert_irq_enabled} "
            + f"alert_irq_immediately={self.alert_irq_immediately} "
            + f"alert_sound_enabled={self.alert_sound_enabled} "
            + f"key_sound_enabled={self.key_sound_enabled} "
            + f"shutdown={self.shutdown}>"
        )

    @staticmethod
    def from_register(value: int):
        """
        Create a new MAX734X configuration object from the register value.

        :param int value: The value of the register.
        :return: The new MAX734X configuration object.
        """
        return Configuration(
            bus_timeout_enabled=bool(value & _CONFIGURATION_BUS_TIMEOUT_MASK),
            active_sounder_output=value & _CONFIGURATION_SOUNDER_STATUS_MASK,
            alert_irq_enabled=bool(value & _CONFIGURATION_ALERT_IRQ_ENABLE_MASK),
            alert_irq_immediately=bool(value & _CONFIGURATION_ALERT_IRQ_EVENT_MASK),
            alert_sound_enabled=bool(value & _CONFIGURATION_ALERT_SOUND_ENABLE_MASK),
            key_sound_enabled=bool(value & _CONFIGURATION_KEY_SOUND_ENABLE_MASK),
            shutdown=not bool(value & _CONFIGURATION_MODE_MASK),
        )

    def to_register(self) -> int:
        """
        Convert the configuration object to the register value.

        :return: Register interpretation of the configuration object.
        """
        return (
            (self.bus_timeout_enabled << 0)
            | self.active_sounder_output
            | (self.alert_irq_enabled << 3)
            | (self.alert_irq_immediately << 4)
            | (self.alert_sound_enabled << 5)
            | (self.key_sound_enabled << 6)
            | ((not self.shutdown) << 7)
        )


class Debounce:
    """
    Debounce register.

    :param int time_ms: Debounce time in milliseconds (from 9 to 40).
    :param int outputs: Number of GPO to enable (from 0 to 6).
    """

    def __init__(
        self,
        time_ms: int = 40,
        outputs: int = 6,
    ) -> None:
        if time_ms < 9 or time_ms > 40:
            raise ValueError("Debounce time must be between 9 and 40 milliseconds.")
        if outputs < 0 or outputs > 6:
            raise ValueError("Number of GPO to enable must be between 0 and 6.")
        self.time_ms = time_ms
        self.outputs = outputs

    def __repr__(self) -> str:
        """
        Return a string representation of the object.

        :return: String representation of the object.
        """
        if self.outputs == 0:
            outputs = "disabled"
        elif self.outputs == 1:
            outputs = "GPO7"
        elif self.outputs == 2:
            outputs = "GPO6+GPO7"
        elif self.outputs == 3:
            outputs = "GPO5+GPO6+GPO7"
        elif self.outputs == 4:
            outputs = "GPO4+GPO5+GPO6+GPO7"
        elif self.outputs == 5:
            outputs = "GPO3+GPO4+GPO5+GPO6+GPO7"
        elif self.outputs == 6:
            outputs = "GPO2+GPO3+GPO4+GPO5+GPO6+GPO7"
        else:
            outputs = "unknown"
        return f"<Debounce time_ms={self.time_ms} outputs={outputs}>"

    @staticmethod
    def from_register(value: int):
        """
        Create a new debounce configuration object from the register value.

        :param int value: The value of the register.
        :return: The new debounce configuration object.
        """
        return Debounce(
            time_ms=(value & _DEBOUNCE_TIME_MASK) + 9,
            outputs=(value & _DEBOUNCE_OUTPUT_ENABLE_MASK) >> 5,
        )

    def to_register(self) -> int:
        """
        Convert the configuration object to the register value.

        :return: Register interpretation of the configuration object.
        """
        return (self.outputs << 5) | ((self.time_ms - 9) & _DEBOUNCE_TIME_MASK)


class Interrupt:
    """
    Interrupt register.

    :param int assent_on_debounce_cycles: Key-scan INT is asserted at
    the end of every N debounce cycles, if new key(s) is debounced
    :param bool asserted_by_key_scan: Key-scan event asserted the INT
    :param bool asserted_by_alert: Alert event asserted the INT
    :param bool is_asserted: INT status
    """

    def __init__(
        self,
        assent_on_debounce_cycles: int = 0,
        asserted_by_key_scan: bool = False,
        asserted_by_alert: bool = False,
        is_asserted: bool = False,
    ):
        if assent_on_debounce_cycles < 0 or assent_on_debounce_cycles > 31:
            raise ValueError("Number of debounce cycles must be between 0 and 31.")
        self.assent_on_debounce_cycles = assent_on_debounce_cycles
        self.asserted_by_key_scan = asserted_by_key_scan
        self.asserted_by_alert = asserted_by_alert
        self.is_asserted = is_asserted

    def __repr__(self) -> str:
        """
        Return a string representation of the object.

        :return: String representation of the object.
        """
        return (
            f"<Interrupt assent_on_debounce_cycles={self.assent_on_debounce_cycles}"
            + f" asserted_by_key_scan={self.asserted_by_key_scan}"
            + f" asserted_by_alert={self.asserted_by_alert}"
            + f" is_asserted={self.is_asserted}>"
        )

    @staticmethod
    def from_register(value: int):
        """
        Create a new interrupt object from the register value.

        :param int value: The value of the register.
        :return: The new interrupt object.
        """
        return Interrupt(
            assent_on_debounce_cycles=value & _INTERRUPT_KEY_SCAN_INT_FREQ_MASK,
            asserted_by_key_scan=value & _INTERRUPT_KEY_SCAN_EVENT_MASK,
            asserted_by_alert=value & _INTERRUPT_ALERT_EVENT_MASK,
            is_asserted=value & _INTERRUPT_INT_STATUS_MASK,
        )

    def to_register(self) -> int:
        """
        Convert the interrupt configuration object to the register value.

        :return: Register interpretation of the interrupt configuration object.
        """
        return self.assent_on_debounce_cycles & _INTERRUPT_KEY_SCAN_INT_FREQ_MASK


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
        self.key = (row << 3) + column

    def __repr__(self) -> str:
        """
        Return a string representation of the object.
        :return: String representation of the object.
        """
        return (
            f"<KeysFiFo overflow={self.overflow} last={self.last} "
            + f"key={self.key} row={self.row} column={self.column}>"
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
            last=not bool(value & _KEYS_FIFO_LAST_MASK),
            column=(value & _KEYS_FIFO_KEY_MASK) >> 3,
            row=value & _KEYS_FIFO_KEY_MASK & 0x07,
        )


class Sounder:
    """
    Sounder register.

    :param bool buffer: Sound buffering.
    :param int frequency: Sound frequency.
    :param int duration: Sound duration.
    """

    def __init__(
        self,
        buffer: bool = False,
        frequency: int = SOUND_OUTPUT_FREQUENCY_DEFAULT,
        duration: int = SOUND_DURATION_DEFAULT,
    ) -> None:
        if (
            frequency < SOUNDER_OUTPUT_ACTIVE_LOW
            or frequency > SOUNDER_OUTPUT_FREQUENCY_E7
        ):
            raise ValueError("Output frequency must be between 0 and 14.")
        if duration < SOUND_DURATION_CONTINUOUS or duration > SOUND_DURATION_1000MS:
            raise ValueError("Duration must be between 0 and 7.")
        self.buffer = buffer
        self.frequency = frequency
        self.duration = duration

    def __repr__(self) -> str:
        """
        Return a string representation of the object.
        :return: String representation of the object.
        """
        frequency_strings: list[str] = [
            "active low",
            "active high",
            "C5",
            "D5",
            "E5",
            "F5",
            "G5",
            "A5",
            "B5",
            "C6",
            "E6",
            "G6",
            "A6",
            "C7",
            "D7",
            "E7",
        ]
        duration_strings: list[str] = [
            "continuous",
            "15625 ms",
            "3125 ms",
            "625 ms",
            "125 ms",
            "250 ms",
            "500 ms",
            "1000 ms",
        ]
        return (
            f"<Sounder buffer={self.buffer}"
            + f" frequency={frequency_strings[self.frequency >> 1]}"
            + f" duration={duration_strings[self.duration >> 5]}>"
        )

    @staticmethod
    def from_register(value: int):
        """
        Create a new Sounder object from the register value.

        :param int value: The value of the register.
        :return: The new Sounder object.
        """
        return Sounder(
            buffer=bool(value & _SOUNDER_BUFFER_MASK),
            frequency=value & _SOUNDER_OUTPUT_FREQUENCY_MASK,
            duration=value & _SOUND_DURATION_MASK,
        )

    def to_register(self) -> int:
        """
        Convert the interrupt configuration object to the register value.

        :return: Register interpretation of the interrupt configuration object.
        """
        return int(self.buffer) | self.frequency | self.duration


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
        self._i2c_keyboard = I2CDevice(i2c_bus, address)
        self._i2c_sounder = I2CDevice(i2c_bus, address + 1)

    def read_keys(self) -> KeysFiFo:
        """
        Read the keys FIFO register.

        :return KeysFiFo: The keys FIFO register.
        """
        buffer: bytearray = bytearray([_REG_KEYS])
        with self._i2c_keyboard as i2c:
            i2c.write_then_readinto(
                in_buffer=buffer, in_end=1, out_buffer=buffer, out_end=1
            )
        return KeysFiFo.from_register(buffer[0])

    def read_debounce(self) -> Debounce:
        """
        Read the debounce register.

        :return DebounceConfiguration: The debounce configuration object.
        """
        buffer: bytearray = bytearray([_REG_DEBOUNCE])
        with self._i2c_keyboard as i2c:
            i2c.write_then_readinto(
                in_buffer=buffer, in_end=1, out_buffer=buffer, out_end=1
            )
        return Debounce.from_register(buffer[0])

    def write_debounce(self, debounce: Debounce) -> None:
        """
        Write the debounce register.

        :param Debounce debounce: The debounce configuration object.
        """
        buffer: bytearray = bytearray([_REG_DEBOUNCE, debounce.to_register()])
        with self._i2c_keyboard as i2c:
            i2c.write(buffer)

    def read_configuration(self) -> Configuration:
        """
        Read the configuration register.

        :return MAX734XConfiguration: The configuration object.
        """
        buffer: bytearray = bytearray([_REG_CONFIGURATION])
        with self._i2c_keyboard as i2c:
            i2c.write_then_readinto(
                in_buffer=buffer, in_end=1, out_buffer=buffer, out_end=1
            )
        return Configuration.from_register(buffer[0])

    def write_configuration(self, configuration: Configuration) -> None:
        """
        Write the configuration register.

        :param Configuration configuration: The configuration object.
        """
        buffer: bytearray = bytearray([_REG_CONFIGURATION, configuration.to_register()])
        with self._i2c_keyboard as i2c:
            i2c.write(buffer)

    def read_interrupt(self) -> Interrupt:
        """
        Read the interrupt register.

        :return Interrupt: The interrupt object.
        """
        buffer: bytearray = bytearray([_REG_INTERRUPT])
        with self._i2c_keyboard as i2c:
            i2c.write_then_readinto(
                in_buffer=buffer, in_end=1, out_buffer=buffer, out_end=1
            )
        return Interrupt.from_register(buffer[0])

    def write_interrupt(self, interrupt: Interrupt) -> None:
        """
        Write the interrupt register.

        :param Interrupt interrupt: The interrupt object.
        """
        buffer: bytearray = bytearray([_REG_INTERRUPT, interrupt.to_register()])
        with self._i2c_keyboard as i2c:
            i2c.write(buffer)

    def read_key_sound(self) -> Sounder:
        """
        Read the key sound register.

        :return Sounder: The sounder object.
        """
        buffer: bytearray = bytearray([_REG_KEY_SOUND])
        with self._i2c_keyboard as i2c:
            i2c.write_then_readinto(
                in_buffer=buffer, in_end=1, out_buffer=buffer, out_end=1
            )
        return Sounder.from_register(buffer[0])

    def write_key_sound(self, sounder: Sounder) -> None:
        """
        Write the key sound register.

        :param Sounder sounder: The sounder object.
        """
        buffer: bytearray = bytearray([_REG_KEY_SOUND, sounder.to_register()])
        with self._i2c_keyboard as i2c:
            i2c.write(buffer)

    def read_alert_sound(self) -> Sounder:
        """
        Read the alert sound register.

        :return Sounder: The sounder object.
        """
        buffer: bytearray = bytearray([_REG_ALERT_SOUND])
        with self._i2c_keyboard as i2c:
            i2c.write_then_readinto(
                in_buffer=buffer, in_end=1, out_buffer=buffer, out_end=1
            )
        return Sounder.from_register(buffer[0])

    def write_alert_sound(self, sounder: Sounder) -> None:
        """
        Write the alert sound register.

        :param Sounder sounder: The sounder object.
        """
        buffer: bytearray = bytearray([_REG_ALERT_SOUND, sounder.to_register()])
        with self._i2c_keyboard as i2c:
            i2c.write(buffer)

    def play_sound(self, sounder: Sounder) -> None:
        """
        Play the sound.

        :param Sounder sounder: The sounder object.
        """
        buffer: bytearray = bytearray([sounder.to_register()])
        with self._i2c_sounder as i2c:
            i2c.write(buffer)
