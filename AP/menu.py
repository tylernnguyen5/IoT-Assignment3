# LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 menu.py

from client_TCP import ClientTCP
import requests
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os

class Menu:
    """This class consists of 2 menus. One for logging in and the other one is for unlock/lock the car.
    Only when the user has logged in that he/she can unlock/lock the car in the second menu.

    There is a variable called user_id, which will be set once the user logged in. This is also a proof that the user is authenticated.
    
    This class imports client_TCP.py module to send messages to the TCP for specific request.
    """
    user_id = None

    clientTCP = ClientTCP()

    id_names = {"Fahim":1, "Tyler":2, "Vinh":3}   # Created according to our current dataset (for facial recognition)

    def main(self):
        """This function will start running the first menu, which is for logging in.
        """
        self.runMenu1()


    def runMenu1(self):
        """This menu is for the user to choose whether to enter credentials or to use facial recognition for logging in.
        Once the user logged in, the second menu will let the user decide whether to unlock or lock the car. Also, an User ID will be set in order to trigger unlock/lock car function.

        Option 1: Login with credentials
        Option 2: Login with facial recognition

        Enter 0 to quit
        """
        while(True):
            print()
            print("MENU 1")
            print("1. Login with credentials")
            print("2. Login with facial recognition")
            print("0. Quit")
            selection = input("Select an option: ")
            print()

            if(selection == "1"): # Login with credentials
                self.user_id = self.login()
                
                if self.user_id != "": 
                    print("You logged in! Your user ID: {}".format(self.user_id))
                    self.runMenu2()
                else: print("Invalid Credentials!")
            elif(selection == "2"): # Login with facial recognition
                self.user_id = self.face_recognition()

                if self.user_id != "":
                    print("You logged in! Your user ID: {}".format(self.user_id))
                    self.runMenu2()
                else: print("Invalid Credentials!")
            elif(selection == "0"): # Quit app
                print("--- Goodbye! ---")
                break
            else:
                print("Invalid input - please try again.")


    def runMenu2(self):
        """This menu is when the user has logged in and the user_id has been set.
        This menu is for the user to unlock/lock the booked car.

        Option 1: Unlock Car
        Option 2: Lock Car

        Enter 0 to log out 
        """
        while(True):
            print()
            print("MENU 2")
            print("1. Unlock Car")
            print("2. Lock Car")
            print("0. Log out")
            selection = input("Select an option: ")
            print()

            if(selection == "1"): # Unlock car
                unlocked = self.unlockCar()

                if unlocked == "unlocked": print("Car Unlocked!")
                else: print("Unlocking Failed!")
            elif(selection == "2"): # Lock car
                locked = self.lockCar()

                if locked == "locked": print("Car Locked!")
                else: print("Locking Failed!")
            elif(selection == "0"): # Log out
                print("--- Logging out! ---")
                self.user_id = None
                break
            else:
                print("Invalid input - please try again.")


    def login(self):
        """This function will trigger client_TCP.credentialsCheck() and ask the user to enter their credentials to log in.
        
        Returns:
            int -- an User ID if the credentials are valid and None if they are invalid
        """
        print("--- Login ---")
        user_id = self.clientTCP.credentialsCheck()
        return user_id


    def unlockCar(self):
        """This function will trigger client_TCP.unlockCar() and ask the user to enter their details to unlock.
        
        Returns:
            str -- "unlocked" if successful
        """
        print("--- Unlock Car ---")
        unlocked = self.clientTCP.unlockCar(self.user_id)
        return unlocked


    def lockCar(self):
        """This function will trigger client_TCP.lockCar() and ask the user to enter their details to lock.
        
        Returns:
            str -- "locked" if successful
        """
        print("--- Lock Car ---")
        locked = self.clientTCP.lockCar(self.user_id)
        return locked


    def face_recognition(self):
        """This function will called with the user chooses to login with facial recognition from Menu 1. It will try to recognise the user from the camera with its dataset.
        The process was adapted from the following source: https://www.pyimagesearch.com/2018/09/24/opencv-face-recognition/

        The general steps are:
        - Load our serialized face detector from disk
        - Load our serialized face embedding model from disk
        - Load the actual face recognition model along with the label encoder
        - Loop over frames from the video file stream, detect faces and filter out weak detections
        - If it recognises an user, the loop will break and return the user ID that matches in the dataset

        Returns:
            int -- An User ID if facial recognition succeeds. None for the otherwise
        """    
        flag = 0        #For break condition
        args = {
            "detector": "face_detection_model",
            "embedding_model": "openface_nn4.small2.v1.t7",         #Initializing Parameters
            "recognizer": "output/recognizer.pickle",
            "le": "output/le.pickle",
            "confidence": 0.5
        }

        # load our serialized face detector from disk
        print("[INFO] loading face detector...")
        protoPath = os.path.sep.join([args["detector"], "deploy.prototxt"])
        modelPath = os.path.sep.join([args["detector"],
                                    "res10_300x300_ssd_iter_140000.caffemodel"])
        detector = cv2.dnn.readNetFromCaffe("face_detection_model/deploy.prototxt", "face_detection_model/res10_300x300_ssd_iter_140000.caffemodel")

        # load our serialized face embedding model from disk
        print("[INFO] loading face recognizer...")
        embedder = cv2.dnn.readNetFromTorch(args["embedding_model"])

        # load the actual face recognition model along with the label encoder
        recognizer = pickle.loads(open(args["recognizer"], "rb").read())
        le = pickle.loads(open(args["le"], "rb").read())

        # initialize the video stream, then allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        time.sleep(2.0)

        # start the FPS throughput estimator
        fps = FPS().start()

        # loop over frames from the video file stream
        while True:
            # grab the frame from the threaded video stream
            frame = vs.read()

            # resize the frame to have a width of 600 pixels (while
            # maintaining the aspect ratio), and then grab the image
            # dimensions
            frame = imutils.resize(frame, width=600)
            (h, w) = frame.shape[:2]

            # construct a blob from the image
            imageBlob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)), 1.0, (300, 300),
                (104.0, 177.0, 123.0), swapRB=False, crop=False)

            # apply OpenCV's deep learning-based face detector to localize
            # faces in the input image
            detector.setInput(imageBlob)
            detections = detector.forward()

            # loop over the detections
            for i in range(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                confidence = detections[0, 0, i, 2]

                # filter out weak detections
                if confidence > args["confidence"]:
                    # compute the (x, y)-coordinates of the bounding box for
                    # the face
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # extract the face ROI
                    face = frame[startY:endY, startX:endX]
                    (fH, fW) = face.shape[:2]

                    # ensure the face width and height are sufficiently large
                    if fW < 20 or fH < 20:
                        continue

                    # construct a blob for the face ROI, then pass the blob
                    # through our face embedding model to obtain the 128-d
                    # quantification of the face
                    faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                                                    (96, 96), (0, 0, 0), swapRB=True, crop=False)
                    embedder.setInput(faceBlob)
                    vec = embedder.forward()

                    # perform classification to recognize the face
                    preds = recognizer.predict_proba(vec)[0]
                    j = np.argmax(preds)
                    proba = preds[j]
                    name = le.classes_[j]

                    # draw the bounding box of the face along with the
                    # associated probability
                    text = "{}: {:.2f}%".format(name, proba * 100)
                    y = startY - 10 if startY - 10 > 10 else startY + 10
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                                (0, 0, 255), 2)
                    cv2.putText(frame, text, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

                    if (proba*100 > 60):            #If accuracy is greater than 60 percent
                        print("Detected Person's Name is : " + str(name))
                        if(str(name) in self.id_names):      #See if the detected name is valid
                            flag = 1
                            detected_id = self.id_names[str(name)]       #Storing the id for the person
                            break

            if (flag==1):
                break
            
            # update the FPS counter
            fps.update()

            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()
        flag = 0

        return detected_id


if __name__ == "__main__":
    Menu().main()
