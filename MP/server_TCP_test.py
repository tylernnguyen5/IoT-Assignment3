import unittest
import server_TCP


""" 
To run the test use command:  python -m unittest SocketTest.py
This command pass the test case to the unittest module
All the test cases must be named in a fashion of "test_xxx" or the unittest module will skip the test, 
so be sure to look at the output to see how many tests have ran to make sure all the tests have performed
"""
class MyTestCase(unittest.TestCase):
    def test_loginWithCredentials(self):
        # Arguments:
        #         username {str} -- User's username
        #         password {str} -- User's password
        # Returns:
        #         int -- User ID if successfully login. None for the otherwise

        self.assertEqual(server_TCP.loginWithCredentials("", ""), "")
        self.assertEqual(server_TCP.loginWithCredentials("", ""), "")


    def test_UnlockCar(self):
        # Arguments:
        #         user_id {int} -- User ID of the user who has made the booking
        #         car_id {int} -- Car ID of the booked car
        #         begin_time {datetime} -- The beginning date and time of the booking
        # Returns:
        #         str -- Content of the reponse from the API
        self.assertEqual(server_TCP.unlockCar("", "", ""), "")
        self.assertEqual(server_TCP.unlockCar("", "", ""), "")

    def test_lockCar(self):
        # Arguments:
        #         user_id {int} -- User ID of the user who has made the booking
        #         car_id {int} -- Car ID of the booked car
        #
        #     Returns:
        #         str -- Content of the reponse from the API
        self.assertEqual((server_TCP.lockCar("", "")), "")
        self.assertEqual((server_TCP.lockCar("", "")), "")

if __name__ == '__main__':
    unittest.main()
