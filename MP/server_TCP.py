#!/usr/bin/env python3

import socket
import requests
import json

def loginWithCredentials(username, password):
    """After the credentials are sent from the Agent Pi via TCP socket. The TCP server will trigger this function to log the user in via Flask API.
    A POST request will be sent to the API. If the credentials are valid, an User ID will be returned and send back to the Agent Pi via TCP socket.
    
    Arguments:
        username {str} -- User's username
        password {str} -- User's password

    Returns:
        int -- User ID if successfully login. None for the otherwise
    """
    data = {
        'username' : username,
        'password' : password 
    }

    # Send the POST request to the API
    response = requests.post("http://127.0.0.1:5000/ap_login", data)

    # Examine the response from the API
    if response.status_code == 200:
        return response.text # Return User ID
    elif response.status_code == 404:
        return None # No User ID is returned


def unlockCar(user_id, car_id, begin_time):
    """This function will make a request to unlock the car via the Flask API.
    This function will trigger flask_api.unlockCar().
    This function is called from a TCP client from the Agent Pi.

    Arguments:
        user_id {int} -- User ID of the user who has made the booking
        car_id {int} -- Car ID of the booked car
        begin_time {datetime} -- The beginning date and time of the booking

    Returns:
        str -- Content of the reponse from the API
    """

    data = {
        'user_id'   : user_id,
        'car_id'    : car_id,
        'begin_time': begin_time   
    }

    # Send a request to Flask API
    response = requests.put("http://127.0.0.1:5000/car/unlock", data)


    # Examine the response from the API
    if response.status_code == 200:
        return response.text # Return "unlocked"
    elif response.status_code == 404:
        return None # No string is returned


def lockCar(user_id, car_id):
    """This function will make a request to lock the car via the Flask API.
    This function will trigger flask_api.lockCar().
    This function is called from a TCP client from the Agent Pi.

    Arguments:
        user_id {int} -- User ID of the user who has made the booking
        car_id {int} -- Car ID of the booked car

    Returns:
        str -- Content of the reponse from the API
    """

    data = {
        'user_id'   : user_id,
        'car_id'    : car_id
    }

    # Send a request to Flask API
    response = requests.put("http://127.0.0.1:5000/car/lock", data)

    # Examine the response from the API
    if response.status_code == 200:
        return response.text # Return "locked"
    elif response.status_code == 404:
        return None # No string is returned

# New function for A3
def getMACs():
    """This function will make a request to get a list of the Engineers' Bluetooth MAC addresses so that it can be sent to the Agent Pi for scanning and automatically unlocking the car.
    This function will trigger flask_api.getMACs().
    This function is called from a TCP client from the Agent Pi.

    Returns:
        list of str -- A list of Engineers' trusted Bluetooth MAC addresses
    """
    response = requests.get("http://127.0.0.1:5000/user/engineer/device")


    # Examine the response from the API
    if response.status_code == 200:
        return response.text # Return list of MAC addresses
    elif response.status_code == 404:
        return None # Nothing is returned

# ----------------------------------------------------------------------------------------
"""The code below is for launching the TCP server and listen for connection.
Once there is a connection and a message, the message will be examine with the leading tag to indicate which request to send to the Flask API.
"""
if __name__ == '__main__':
    HOST = ""    # Empty string means to listen on all IP's on the machine, also works with IPv6.
                # Note "0.0.0.0" also works but only with IPv4.
    PORT = 65000 # Port to listen on (non-privileged ports are > 1023).
    ADDRESS = (HOST, PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(ADDRESS)
        s.listen()

        while True:
            print("Listening on {}...".format(ADDRESS))
            conn, addr = s.accept()
            with conn:
                print("Connected to {}".format(addr))

                while True:
                    # Receive message and check if it's empty
                    message = conn.recv(4096) # 4096 is the buffersize
                    if(not message):
                        break

                    print("Received {} bytes of data decoded to: '{}'".format(  len(message), 
                                                                                message.decode()))
                    
                    # Check message tag to identify which function to trigger
                    tag = message.decode().split()[0]
                    reply = ""

                    # For message with credentials tag
                    if (tag == "credentials"): 
                        # Data handling - message = "credentials username password"
                        username = message.decode().split()[1]
                        password = message.decode().split()[2]
                        print("Received: {}, {}".format(username, password))

                        # Trigger the right function to send request
                        reply = loginWithCredentials(username, password)
                    
                    # For message with unlock tag
                    elif (tag == "unlock"): 
                        # Data handling - message = "unlock user_id car_id begin_time"
                        user_id     = message.decode().split()[1]
                        car_id      = message.decode().split()[2]
                        begin_time  = message.decode().split(" ", 3)[3]
                        
                        # Trigger the right function to send request
                        reply = unlockCar(user_id, car_id, begin_time)

                    # For message with lock tag
                    elif (tag == "lock"): 
                        # Data handling - message = "lock user_id car_id"
                        user_id     = message.decode().split()[1]
                        car_id      = message.decode().split()[2]
                        
                        # Trigger the right function to send request
                        reply = lockCar(user_id, car_id)

                    # For message with bluetooth tag
                    elif (tag == "bluetooth"):                     
                        # Trigger the right function to send request
                        addresses = json.loads(getMACs()) # list of MAC addresses

                        # if addresses is not None:
                        #     # Convert list to str
                        #     reply = " " 

                        #     reply = reply.join(addresses)

                        if addresses is not None:
                            # Convert list to str
                            for addr in addresses:
                                reply += addr + " "

                    if reply is not None:
                        print("Sending reply.")
                        conn.sendall(reply.encode())
                    else: break
                
                print("Disconnecting from client.")
            print("Closing listening socket.")
            print()
    print("Done.")