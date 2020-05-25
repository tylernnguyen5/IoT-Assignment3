# LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 face_rec_test.py
import unittest
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os

class FaceRecTest(unittest.TestCase):
    """This test will run the face recognition function and then compare
    the face with known IDs.

    Assertion: For each case (each face) that it recognizes, it will compare the detected_id with known IDs using assertTrue()
    """
    id_names = {"Fahim":1, "Tyler":2, "Vinh":3}

    def test_face_recog(self):
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

        # Assertion
        if (detected_id == 1):
            self.assertTrue(id_names["Fahim"] == detected_id)
        elif (detected_id == 2):
            self.assertTrue(id_names["Tyler"] == detected_id)
        elif (detected_id == 3):
            self.assertTrue(id_names["Vinh"] == detected_id)
        else:
            self.assertFalse(id_names["Fahim"] == detected_id)

if __name__ == '__main__':
    unittest.main()