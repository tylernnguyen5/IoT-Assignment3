#!/usr/bin/env python3
import bluetooth
import os
import time

# Discover devices via Bluetooth
def main():
    """
    This module is for discovering new Bluetooth devices so that we can record the MAC addresses and add them to Agent Pi's program.

    It will start scanning for the Bluetooth devices every 3 seconds and print their MAC addresses and names to the ternimal.

    After we configure the Agent Pi's with the right MAC adresses for the Engineers, the cars will be unlocked automactically when the device is nearby.
    """
    while True:
        # Display current time
        dt = time.strftime("%a, %d %b %y %H:%M:%S", time.localtime())
        print("\nCurrently: {}\n".format(dt))

        time.sleep(3) #Sleep three seconds 

        # Discover devices
        nearby_devices = bluetooth.discover_devices()

        # Scanning for devices loop
        for mac_address in nearby_devices:
            print("Found: {}".format(mac_address))
            print("Name: {}".format(bluetooth.lookup_name(mac_address, timeout=5)))
            print()


#Execute program
main()
