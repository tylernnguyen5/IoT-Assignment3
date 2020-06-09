#!/usr/bin/env python3

import socket
import getpass

class ClientTCP:
    """This module will be imported to menu.py to the Agent Pi the ability to connect to the TCP Server and send messages
    """

    HOST = input("Enter IP address of Carshare server: ")   # The server's hostname or IP address

    PORT = 65000       # The port used by the server
    ADDRESS = (HOST, PORT)

    def credentialsCheck(self):
        """This function will ask the user to enter their username and password.
        The credentials will be sent to the Master Pi via TCP socket once there is a connection to it.

        Returns:
            int -- User ID if the credentials are valid to indicate successful login. None if the credentials are invalid.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting to {}...".format(self.ADDRESS))
            s.connect(self.ADDRESS)
            print("Connected.")

            while True:
                username = input("Enter your username: ")
                password = getpass.getpass("Enter your password: ")
                if(not username or not password): # if blank input, will break the loop
                    break
                
                # Send credentials 
                credentials = "credentials {} {}".format(username, password)
                s.sendall(credentials.encode())


                # Receive data, which is a user ID if validated
                data = s.recv(4096) # 4096 is the buffersize
                print("Received {} bytes of data decoded to: '{}'".format(  len(data), 
                                                                            data.decode()))
                return data.decode()
            
            print("Disconnecting from server.")
        print("Done.")
        print()

    def unlockCar(self, user_id):
        """This function is triggered when the user choose to unlock the car via menu.py.
        The unlocking details will be sent to the TCP server in a string. The string is constructed the "unlock" tag at the beginning.
        User will be asked to enter the booked car ID and beginning time of the booking for verification in the Bookings table on the Google Cloud SQL Carshare datbase.


        Arguments:
            user_id {int} -- User ID. This is sent when the user logs in from Menu 1 via menu.py

        Returns:
            str -- Message reply from the TCP server. "unlocked" if successful
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting to {}...".format(self.ADDRESS))
            s.connect(self.ADDRESS)
            print("Connected.")

            while True:
                user_id     = user_id
                car_id      = input("Enter your car ID: ")
                begin_time  = input("Enter your begin time (YYYY-MM-DD HH:MM:SS): ")
                if(not user_id or not car_id or not begin_time): # if blank input, will break the loop
                    break
                
                # Send unlock details 
                details = "unlock {} {} {}".format(user_id, car_id, begin_time)
                s.sendall(details.encode())


                # Receive data, which is string saying unlocked
                data = s.recv(4096) # 4096 is the buffersize
                print("Received {} bytes of data decoded to: '{}'".format(  len(data), 
                                                                            data.decode()))
                return data.decode()
            
            print("Disconnecting from server.")
        print("Done.")
        print()


    def lockCar(self, user_id):
        """This function is triggered when the user choose to lock the car via menu.py.
        The locking details will be sent to the TCP server in a string. The string is constructed the "lock" tag at the beginning.
        User will be asked to enter the booked car ID for verification in the Bookings table on the Google Cloud SQL Carshare datbase.


        Arguments:
            user_id {int} -- User ID. This is sent when the user logs in from Menu 1 via menu.py

        Returns:
            str -- Message reply from the TCP server. "unlocked" if successful
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting to {}...".format(self.ADDRESS))
            s.connect(self.ADDRESS)
            print("Connected.")

            while True:
                user_id     = user_id
                car_id      = input("Enter your car ID: ")
                if(not user_id or not car_id): # if blank input, will break the loop
                    break
                
                # Send lock details 
                details = "lock {} {}".format(user_id, car_id)
                s.sendall(details.encode())


                # Receive data, which is a user ID if validated
                data = s.recv(4096) # 4096 is the buffersize
                print("Received {} bytes of data decoded to: '{}'".format(  len(data), 
                                                                            data.decode()))
                return data.decode()
            
            print("Disconnecting from server.")
        print("Done.")
        print()
    
    # New function for A3
    def getTrustedDeviceAddresses(self):
        """This function is triggered when the Engineer chooses to unlock the car with Bluetooth via menu.py.
        This will send a request to the TCP server get a list of trusted Bluetooth MAC addresses for Engineers' devices.

        Returns:
            str -- Message reply from the TCP server. "unlocked" if successful
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting to {}...".format(self.ADDRESS))
            s.connect(self.ADDRESS)
            print("Connected.")

            while True:              
                # Send lock details 
                tag = "bluetooth"
                s.sendall(tag.encode())

                # Receive data, which is a user ID if validated
                data = s.recv(4096) # 4096 is the buffersize
                print("Received {} bytes of data decoded to: '{}'".format(  len(data), 
                                                                            data.decode()))
                return data.decode()
            
            print("Disconnecting from server.")
        print("Done.")
        print()