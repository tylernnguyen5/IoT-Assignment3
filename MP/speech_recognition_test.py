# Requires PyAudio and PySpeech.
import speech_recognition as sr
import unittest

class Speech_Recognition(unittest.TestCase):
    """
    This module contains the code to test the voice recognition feature where the Admin speak a string of keywords to the mic and the string will be asserted.
    """
    def test_func(self):
        
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

        keywords = r.recognize_google(audio)       #Printing the conveted Text
        self.assertIsNotNone(keywords)     #Generates an assertion error if the post request is None


if __name__ == '__main__':
    Speech_Recognition().test_func()

