# Requires PyAudio and PySpeech.
import speech_recognition as sr
import unittest

class Speech_Recognition(unittest.TestCase):
    def test_func(self):
        while True:
            # Creating a Speech recognition object
            r = sr.Recognizer()
            self.assertIsNotNone(r)  # Generates an assertion error if Speech recognition object could not be made
            with sr.Microphone() as source:     #Using the default microphone as source
                print("Say something!")
                audio = r.listen(source)        #Listening to input from the microphone
                self.assertIsNotNone(audio)     #Generates an assertion error if the audio could not be understood
                # Speech recognition using Google Speech Recognition
                try:
                    print("You said: " + r.recognize_google(audio))
                    self.assertIsNotNone(r.recognize_google(audio))     #Generates an assertion error if the recognition could not be performed
                except sr.UnknownValueError:    #If the speech could not be understood by the user
                    print("Google Speech Recognition could not understand audio")
                    self.assertIsNotNone(audio)
                except sr.RequestError as e:    #If there was a connectivity issue in sending request to Google Speech Recognition Service
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                    self.assertIsNotNone(r.recognize_google(audio))     #Generates an assertion error if the recognition could not be performed

            post_request = r.recognize_google(audio)       #Printing the conveted Text
            print(post_request)
            self.assertIsNotNone(post_request)     #Generates an assertion error if the post request is None

        #REMOVE WHILE LOOP FOR DOING SPEECH RECOGNITION ONCE

if __name__ == '__main__':
    Speech_Recognition().test_func()
