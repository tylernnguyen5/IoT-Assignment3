# LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 vocie_car_search.py

# Requires PyAudio and PySpeech.
import speech_recognition as sr
import json, requests

class Speech_Recognition:
    def main(self):
        """
        This module is for the Admin to use Voice Recognition to send a request to the Flask API for car search.

        The user will speak into the mic a string of keywords. The string will be submitted via POST request to the "/car/search/voice" endpoint.

        The result of cars found will be printed to the console.
        """
        while True:
            # Creating a Speech recognition object
            r = sr.Recognizer()

            with sr.Microphone() as source:     #Using the default microphone as source
                print("Say something!")
                audio = r.listen(source)        #Listening to input from the microphone

                # Speech recognition using Google Speech Recognition
                try:
                    print("You said: " + r.recognize_google(audio))

                except sr.UnknownValueError:    #If the speech could not be understood by the user
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:    #If there was a connectivity issue in sending request to Google Speech Recognition Service
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))

            keywords = r.recognize_google(audio)       #Printing the conveted Text
            print(keywords)

            # # Make a search request with the recorded keywords to the API
            # data = {
            #     "keywords" : keywords
            # }

            # response = requests.post("http://127.0.0.1:5000/car/search/voice", data)

            # # Examine the response from the API
            # if response.status_code == 200:
            #     print(response.text) # Return a jsonified objects of cars
            # elif response.status_code == 404:
            #     print("[ERROR] Nothing was returened")

        #REMOVE WHILE LOOP FOR DOING SPEECH RECOGNITION ONCE

if __name__ == '__main__':
    Speech_Recognition().main()