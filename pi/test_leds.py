"""Light each status LED in turn to check the station wiring.

    python3 pi/test_leds.py            # 2 seconds per LED
    python3 pi/test_leds.py --seconds 5
"""
import argparse
import time

import RPi.GPIO as GPIO

# Same pins as python/realtime_inspect.py (BCM numbering)
LEDS = [("red (defective)", 17), ("green (normal)", 22), ("yellow (manual inspection)", 27)]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seconds", type=float, default=2)
    args = p.parse_args()

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    try:
        for name, pin in LEDS:
            print(f"GPIO {pin}: {name}")
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, True)
            time.sleep(args.seconds)
            GPIO.output(pin, False)
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
