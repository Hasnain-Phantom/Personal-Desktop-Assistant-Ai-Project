import pyttsx3
import speech_recognition as sr
import datetime
import cv2
import wikipedia
import webbrowser
import pywhatkit
import datetime
import smtplib
import pytz
from email import message
import webbrowser
from numpy import tile
import speech_recognition
import requests
from bs4 import BeautifulSoup
import pyautogui
import random
from plyer import notification
from pygame import mixer
import speedtest
import os 
import webbrowser
from playsound import playsound


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(audio):
    print(audio)
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 17:
        speak("Good Afternoon!")
    elif 17 <= hour < 20:
        speak("Good Evening!")
    else:
        speak("Good Night!")
    speak("Welcome back. i am your personal desktop assistent. how may i help you!")

def alarm(query):
    timehere = open("Alarmtext.txt","a")
    timehere.write(query)
    timehere.close()
    os.startfile("alarm.py")


def open_weather_notebook():
    os.startfile("Weather_Prediction.ipynb")
















def take_command():
    r = sr.Recognizer()
    retries = 0
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print(e)
        retries += 1
        if retries < 3:
            speak("Sorry, I couldn't understand that. Can you please repeat?")
            return take_command()
        else:
            speak("Sorry, I couldn't understand that. Please try again later.")
            return "None"
    return query.lower()





    #===============notepad====================#




if __name__ == "__main__":
    wish()
    while True:
        query = take_command()
        if "open notepad" in query:
            path = "C:\\WINDOWS\\system32\\notepad.exe"
            os.startfile(path)

        elif "open calculator" in query:
            path = "C:\\Windows\\system32\\calc.exe"
            os.startfile(path)

        elif "open visual studio" in query:
            path = "C:\\Users\\hp\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            os.startfile(path)

        elif "open command prompt" in query:
            os.system("start cmd")

        elif "open camera" in query:
            cap = cv2.VideoCapture(0)
            while True:
                ret, img = cap.read()
                cv2.imshow('webcam', img)
                k = cv2.waitKey(50)
                if k == 27:
                    break
            cap.release()
            cv2.destroyAllWindows()

        elif "search wikipedia for" in query:
            speak("Searching Wikipedia...")
            search_query = query.replace("search wikipedia for", "")
            results = wikipedia.summary(search_query, sentences=2)
            speak("According to Wikipedia")
            speak(results)


        elif "open youtube" in query:
            webbrowser.open("https://www.youtube.com")

        elif "open google" in query:
            webbrowser.open("https://www.google.com")

        elif "google" in query:
            from SearchNow import searchGoogle
            searchGoogle(query)
        elif "youtube" in query:
            from SearchNow import searchYoutube
            searchYoutube(query)
        elif "wikipedia" in query:
            from SearchNow import searchWikipedia
            searchWikipedia(query)

                




        elif "exit" in query:
            speak("Exiting. Goodbye!")
            break


        elif "open" in query:
            from Dictapp import openappweb
            openappweb(query)
        elif "close" in query:
            from Dictapp import closeappweb
            closeappweb(query)


        elif "predict weather jarvis" in query:
            speak("Opening weather prediction notebook")
            open_weather_notebook()

            




#==================================Search on google+================================#

        elif "search on google" in query:
            speak("What should I want to search in google...")
            cm=take_command().lower()
            webbrowser.open(f"{cm}")

#==================================Search on yt+================================#

        elif "search on youtube" in query:
            speak("What do you want to search on YouTube?")
            search_query = take_command().lower()
            pywhatkit.playonyt(search_query)

#==================================Time+================================#

        elif "the time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M")    
            speak(f"Sir, the time is {strTime}")

#==================================ALARM+================================#


        elif "set an alarm" in query:
            print("input time example:- 10 and 10 and 10")
            speak("Set the time")
            a = input("Please tell the time :- ")
            alarm(a)
            speak("Done,sir")
                           
      
        elif "finally sleep" in query:
            speak("Going to sleep,sir")
            exit()




        elif "screenshot" in query:
            import pyautogui #pip install pyautogui
            im = pyautogui.screenshot()
            speak("Done Sir")
            im.save("ss.jpg")
            

        elif "click my picture" in query:
            pyautogui.press("super")
            pyautogui.typewrite("camera")
            pyautogui.press("enter")
            pyautogui.sleep(2)
            speak("SMILE")
            pyautogui.press("enter")


        elif "translate" in query:
            from Translator import translategl
            query = query.replace("jarvis","")
            query = query.replace("translate","")
            translategl(query)






#==================================Turn OFF+================================#

        elif "turn off jarvis" in query:
            speak("Going to sleep,sir")
            exit()


#==================================REMEMBER+================================#

        elif "remember that" in query:
            rememberMessage = query.replace("remember that","")
            rememberMessage = query.replace("jarvis","")
            speak("You told me to"+rememberMessage)
            remember = open("Remember.txt","a")
            remember.write(rememberMessage)
            remember.close()
        elif "what do you remember" in query:
            remember = open("Remember.txt","r")
            speak("You told me to" + remember.read())


#========================================SHUTDOWN====================================#

        elif "shutdown system" in query:
            speak("Are You sure you want to shutdown")
            shutdown = input("Do you wish to shutdown your computer? (yes/no)")
            if shutdown == "yes":
               os.system("shutdown /s /t 1")

            elif shutdown == "no":
               break
          


        #----------------------TALKING---------------------------#

        elif "hello" in query:
            speak("Hello sir, how are you ?")
        elif "i am fine" in query:
            speak("that's great, sir")
        elif "how are you" in query:
            speak("Perfect, sir")
        elif "thank you" in query:
            speak("you are welcome, sir")
                
        elif "tired" in query:
            speak("Playing your favourite songs, sir")
            webbrowser.open("https://www.youtube.com/watch?v=U935BSVJIM0")
                    

        elif "pause" in query:
            pyautogui.press("k")
            speak("video paused")
        elif "play" in query:
            pyautogui.press("k")
            speak("video played")
        elif "mute" in query:
            pyautogui.press("m")
            speak("video muted")
                


        elif "volume up" in query:
                    from keyboard import volumeup
                    speak("Turning volume up,sir")
                    volumeup()
        elif "volume down" in query:
                    from keyboard import volumedown
                    speak("Turning volume down, sir")
                    volumedown()

          



        elif "casual my day" in query:
                    tasks = [] #Empty list 
                    speak("Do you want to clear old tasks (Plz speak YES or NO)")
                    query = take_command().lower()
                    if "yes" in query:
                        file = open("tasks.txt","w")
                        file.write(f"")
                        file.close()
                        no_tasks = int(input("Enter the no. of tasks :- "))
                        i = 0
                        for i in range(no_tasks):
                            tasks.append(input("Enter the task :- "))
                            file = open("tasks.txt","a")
                            file.write(f"{i}. {tasks[i]}\n")
                            file.close()



        elif "no" in query:
                        i = 0
                        no_tasks = int(input("Enter the no. of tasks :- "))
                        for i in range(no_tasks):
                            tasks.append(input("Enter the task :- "))
                            file = open("tasks.txt","a")
                            file.write(f"{i}. {tasks[i]}\n")
                            file.close()

        elif "show my schedule" in query:
                    file = open("tasks.txt","r")
                    content = file.read()
                    file.close()
                    mixer.init()
                    mixer.music.load("notification.mp3")
                    mixer.music.play()
                    notification.notify(
                        title = "My schedule :-",
                        message = content,
                        timeout = 15
                    )



        elif "focus mode" in query:
                    a = int(input("Are you sure that you want to enter focus mode :- [1 for YES / 2 for NO "))
                    if (a==1):
                        speak("Entering the focus mode....")
                        os.startfile("FocusMode.py")
                        exit()

                    
                    else:
                        pass

        elif "show my focus" in query:
                    from FocusGraph import focus_graph
                    focus_graph()


                     
        elif "tell me my internet speed" in query:
                    wifi  = speedtest.Speedtest()
                    upload_net = wifi.upload()/1048576        
                    download_net = wifi.download()/1048576
                    print("Wifi Upload Speed is", upload_net)
                    print("Wifi download speed is ",download_net)
                    speak(f"Wifi download speed is {download_net}")
                    speak(f"Wifi Upload speed is {upload_net}")
                       



        #=================WHATSAPP========================#



        elif "send message" in query:
            speak("Who would you like to send a message to?")
            recipient_name = take_command().lower()
            speak(f"What message would you like to send to {recipient_name}?")
            message_content = take_command().lower()
            speak("Please provide the recipient's phone number.")
            recipient_number = take_command()
            speak(f"Sending message to {recipient_name}")

            # Get current time
            current_time = datetime.datetime.now()
            hour = current_time.hour
            minute = current_time.minute

            # Use current time to send the message
            pywhatkit.sendwhatmsg(recipient_number, message_content, hour, minute + 1)  # Adding 1 to the minute to send message in the next minute

            # Initialize recognizer
recognizer = sr.Recognizer()





# Function to listen to speech and write it to Notepad
def listen_and_write_to_notepad():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")

        # Open Notepad and write the text
        os.system(f"echo {text} | clip")  # Copy text to clipboard
        os.system("start notepad")  # Open Notepad
        os.system("cmd /c \"echo.|set /p=%clipboard%|clip\"")  # Paste text from clipboard to Notepad
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
    except sr.RequestError as e:
        print(f"Error: {e}")



# Call the function to start listening and write to Notepad
listen_and_write_to_notepad()

        