import unittest
import socket
import threading

from werkzeug.debug import console

# change the host if needed, will listern to any if leave blank
PORT = 65000
HOST = ""
ADDRESS = (HOST, PORT)

class MyTestCase(unittest.TestCase):

    """
    A dummy server is created and run in a background thread,
    the dummy server will then listern indefinetly untill it
    receives a connection request from the client
    """

    def run_dummy_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(0)
            conn, addr = s.accept()
            with conn:
                print("Connected to {}".format(addr))
            while True:
                # Receive message and check if it's empty
                message = conn.recv(4096)  # 4096 is the buffersize
                if (not message):
                    break

                print("Received {} bytes of data decoded to: '{}'".format(len(message),
                                                                        message.decode()))


    def testConect(self):
        # Start test server in background thread
        server_thread = threading.Thread(target=self.run_dummy_server)
        server_thread.start()
        print(console)


        server_thread.join()


    """
    The test was eventually carried out manually using two Pi/ multiple shells to mock server and client,
    since the unit test will just run with no response. Since the potential time required to build this
    unit test can be lengthy, all the tests were done manually during the project development.
    """

if __name__ == '__main__':
    unittest.main()
