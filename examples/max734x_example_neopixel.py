# SPDX-FileCopyrightText: 2025 Roman Ondráček
#
# SPDX-License-Identifier: MIT

"""
This example shows how to use this library with the neopixel library to show
the pressed buttons on the neopixel strip.
"""

import board
import digitalio
import neopixel
import max734x

try:
    # This import is only for type checking
    from typing import Optional
    import microcontroller
except ImportError:
    pass


def init_keyboard(
    i2c_bus: board.I2C,
    int_pin: microcontroller.Pin,
) -> tuple[max734x.MAX734X, digitalio.DigitalInOut]:
    """
    Initialize the keyboard controller and the interrupt pin.
    :param i2c_bus: I2C bus
    :param int_pin: Keyboard interrupt pin
    :return: Keyboard controller driver and the interrupt pin object
    """
    # Keyboard controller initialization
    int_input = digitalio.DigitalInOut(pin=int_pin)
    controller = max734x.MAX734X(i2c_bus=i2c_bus)
    # Disable all GPO to enable 8x8 button matrix, debounce interval 40 ms
    controller.write_debounce(max734x.Debounce(time_ms=40, outputs=0))
    # Enable key-scan interrupts
    controller.write_interrupt(max734x.Interrupt(assent_on_debounce_cycles=1))
    # Enable the keyboard controller
    controller.write_configuration(max734x.Configuration(shutdown=False))
    return controller, int_input


def init_neopixel(pin: microcontroller.Pin) -> neopixel.NeoPixel:
    """
    Initialize the neopixel strip.
    :return: NeoPixel object
    """
    pixel = neopixel.NeoPixel(pin, 64, pixel_order=neopixel.GRB)
    clear_neopixel(pixel)
    return pixel


def clear_neopixel(pixel: neopixel.NeoPixel) -> None:
    """
    Clear the neopixel strip.
    :param pixel: NeoPixel object
    """
    for i in range(0, 64):
        pixel[i] = (0, 0, 0)


def main() -> None:
    print("Initializing hardware...")
    i2c = board.I2C()
    kb_controller, kb_int = init_keyboard(i2c_bus=i2c, int_pin=board.D5)
    pixel = init_neopixel(pin=board.D13)
    print("Hardware initialized.")
    print("Press Ctrl+C to exit.")
    print("Press a button...")
    try:
        # Read all pending pressed keys
        while True:
            keys = kb_controller.read_keys()
            if keys.last and keys.key == 0:
                break
        led: Optional[int] = None
        while True:
            if kb_int.value:
                continue
            keys = kb_controller.read_keys()
            if not keys.last:
                continue
            if led is not None:
                pixel[led] = (0, 0, 0)
            led = (keys.row * 8) + keys.column
            pixel[led] = (255, 0, 0)
            print(keys)
    except KeyboardInterrupt:
        clear_neopixel(pixel)
        exit(0)


if __name__ == "__main__":
    main()
