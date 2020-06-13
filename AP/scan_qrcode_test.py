from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import unittest

class Test(unittest.TestCase):
    """
    This module contains the code to test the QR code scanning feature for the Engineer where the user will be asked to start the recording the barcode and the information will be stored in a CSV file.
    """
    def call(self):
        while True:
            selection = input("Press 0 when you finish repairing the car: ")
            print()

            if(selection == "0"):
                self.QRScan()
                break
            else:
                print("Invalid input - please try again.")
                self.assertTrue(selection == '0')             #Assertion Error for invalid input
    
    def QRScan(self):
        print("To Engineer, please present your QR code to record your visit")
        #vs = VideoStream(src=0).start()  #Uncomment this if you are using Webcam
        vs = VideoStream(usePiCamera=True).start()  # For Starting stream of Pi Camera
        time.sleep(2.0)
        csv = open("barcodes.csv", "w")         #initializing the csv file for storing QR codes

        self.assertIsNotNone(csv)  # Assertion error if the csv file could not be read
        found = set()                   #Setting the found variable

        while True:
            frame = vs.read()

            self.assertIsNotNone(frame)             #Assertion error if The Frame is not detected

            frame = imutils.resize(frame, width=400)    #Reading a frame and resizing it
            barcodes = pyzbar.decode(frame)             #Decoding the frame to extract QR Code

            for barcode in barcodes:
                (x, y, w, h) = barcode.rect             #Drawing rectangle around the QR Code
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                barcodeData = barcode.data.decode("utf-8")          #Decoding the strings in QR code to UTF-8
                barcodeType = barcode.type

                self.assertIsNotNone(barcodeData)  # Assertion error if the barcode data is None i.e the Engineer's id and name is not there
                self.assertIsNotNone(barcodeType)   #Assertion error if the barcode type is None

                text = "{} ({})".format(barcodeData, barcodeType)   #Selecting the QR Code type i.e text in our case
                print(text)
                cv2.putText(frame, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)      #Displaying Text around the scanned QR Code in frame

                # if the barcode text is currently not in our CSV file, write
                # the timestamp + barcode to disk and update the set
                if barcodeData not in found:
                    csv.write("{}\n{}\n".format(datetime.datetime.now(),
                                               barcodeData))
                    csv.flush()
                    found.add(barcodeData)
                    break

            cv2.imshow("Barcode Reader", frame)             #Showing the frame in the seperate window
            key = cv2.waitKey(1) & 0xFF

            # if the `s` key is pressed, break from the loop
            if key == ord("s"):
                break

        print("[INFO] cleaning up...")
        csv.close()                             #Closing the CSV file that we opened for editing
        cv2.destroyAllWindows()                 #Destroying all windows
        vs.stop()

if __name__ == '__main__':
    Test().call()
