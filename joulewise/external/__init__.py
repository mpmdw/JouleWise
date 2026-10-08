"""External instruments that are not part of the claim path.

``km003c_usb`` talks to the ChargerLAB POWER-Z KM003C USB-C power meter that
sits between the wall adapter and the Mac (ctypes over libusb and macOS
CommonCrypto; no Python packages).  ``km003c_parse`` turns the JSON-lines
stream written by ``scripts/km003c_monitor.py`` into whole-machine DC-input
energy and the ``meter.*`` disclosure flags.  Everything here is a recorded
diagnostic: it never refuses a window and never produces a claim number.
"""
