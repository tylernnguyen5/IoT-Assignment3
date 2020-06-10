# Requires PyAudio and PySpeech.
import speech_recognition as sr

class Speech_Recognition:
    def main(self):
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

            post_request = r.recognize_google(audio)       #Printing the conveted Text
            print(post_request)

        #REMOVE WHILE LOOP FOR DOING SPEECH RECOGNITION ONCE

if __name__ == '__main__':
    Speech_Recognition().main()