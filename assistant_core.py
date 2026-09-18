"""
Core command logic for the Personal Desktop Assistant.

All the commands from `Personal Desktop Assistant.py` live here, but instead of
calling print()/input() directly they talk to a `UI` object. That lets the same
logic drive both the terminal version and the graphical app (`app.py`).

A UI must provide:
    say(text)            -> speak / display an assistant message
    ask(prompt) -> str   -> ask the user for a typed answer
    listen() -> str      -> capture a voice command (lower-cased, or "None")
    status(text)         -> update a small status indicator (optional)
"""

import datetime
import os
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _path(name):
    return os.path.join(BASE_DIR, name)


# ------------------------------------------------------------------ commands
# Each entry: (keywords that trigger it, short label, description)
# Used by the GUI to build the quick-action sidebar and help panel.
COMMANDS = [
    ("the time", "Time", "Tell the current time"),
    ("open notepad", "Notepad", "Open Notepad"),
    ("open calculator", "Calculator", "Open Calculator"),
    ("open command prompt", "Cmd", "Open Command Prompt"),
    ("open camera", "Camera", "Open the webcam preview"),
    ("screenshot", "Screenshot", "Save a screenshot to ss.jpg"),
    ("open youtube", "YouTube", "Open youtube.com"),
    ("open google", "Google", "Open google.com"),
    ("search wikipedia for", "Wikipedia", "Search Wikipedia for ..."),
    ("search on youtube", "Play on YT", "Play something on YouTube"),
    ("set an alarm", "Alarm", "Set an alarm"),
    ("remember that", "Remember", "Remember a note"),
    ("what do you remember", "Recall", "Read remembered notes"),
    ("show my schedule", "Schedule", "Show saved tasks"),
    ("tell me my internet speed", "Speed test", "Run an internet speed test"),
    ("volume up", "Vol +", "Raise the volume"),
    ("volume down", "Vol -", "Lower the volume"),
    ("translate", "Translate", "Translate text"),
    ("show my focus", "Focus graph", "Plot your focus time"),
    ("focus mode", "Focus mode", "Block distracting sites"),
    ("predict weather jarvis", "Weather", "Open weather notebook"),
    ("shutdown system", "Shutdown", "Shut down the computer"),
]


def greeting():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        return "Good Morning!"
    elif 12 <= hour < 17:
        return "Good Afternoon!"
    elif 17 <= hour < 20:
        return "Good Evening!"
    return "Good Night!"


class Assistant:
    def __init__(self, ui):
        self.ui = ui

    # -------------------------------------------------------------- helpers
    def say(self, text):
        self.ui.say(text)

    def ask(self, prompt):
        return self.ui.ask(prompt)

    def listen(self):
        return self.ui.listen()

    def _run(self, fn, *args):
        """Run a helper that needs an optional third-party package, reporting
        a friendly message instead of crashing when it's missing."""
        try:
            return fn(*args)
        except ImportError as e:
            self.say(f"That feature needs an extra package: {e.name}. "
                     f"Install it with: pip install {e.name}")
        except Exception as e:  # noqa: BLE001 - surface anything to the user
            self.say(f"Sorry, that didn't work: {e}")

    def wish(self):
        self.say(greeting())
        self.say("Welcome back. I am your personal desktop assistant. "
                 "How may I help you?")

    # ------------------------------------------------------------- dispatch
    def handle(self, query):
        """Handle one command. Returns False when the assistant should exit."""
        query = (query or "").lower().strip()
        if not query or query == "none":
            return True

        if "open notepad" in query:
            os.startfile("C:\\WINDOWS\\system32\\notepad.exe")

        elif "open calculator" in query:
            os.startfile("C:\\Windows\\system32\\calc.exe")

        elif "open visual studio" in query:
            os.system("start code")

        elif "open command prompt" in query:
            os.system("start cmd")

        elif "open camera" in query:
            self._run(self._camera)

        elif "search wikipedia for" in query:
            self._run(self._wikipedia, query.replace("search wikipedia for", ""))

        elif "open youtube" in query:
            webbrowser.open("https://www.youtube.com")

        elif "open google" in query:
            webbrowser.open("https://www.google.com")

        elif "search on google" in query:
            self.say("What should I search on Google?")
            cm = self.listen()
            if cm != "None":
                webbrowser.open(f"https://www.google.com/search?q={cm}")

        elif "search on youtube" in query:
            self.say("What do you want to search on YouTube?")
            cm = self.listen()
            if cm != "None":
                self._run(self._play_on_yt, cm)

        elif "google" in query:
            self._run(self._search_google, query)

        elif "youtube" in query:
            self._run(self._search_youtube, query)

        elif "wikipedia" in query:
            self._run(self._wikipedia, query.replace("wikipedia", ""))

        elif "exit" in query or "turn off jarvis" in query or "finally sleep" in query:
            self.say("Going to sleep. Goodbye!")
            return False

        elif "predict weather jarvis" in query:
            self.say("Opening weather prediction notebook")
            os.startfile(_path("Weather_Prediction.ipynb"))

        elif "the time" in query:
            self.say("Sir, the time is " + datetime.datetime.now().strftime("%H:%M"))

        elif "set an alarm" in query:
            a = self.ask("Alarm time (example: 10 and 10 and 10 for 10:10:10)")
            if a:
                with open(_path("Alarmtext.txt"), "a") as f:
                    f.write(a)
                os.startfile(_path("alarm.py"))
                self.say("Done, sir")

        elif "screenshot" in query:
            self._run(self._screenshot)

        elif "click my picture" in query:
            self._run(self._click_picture)

        elif "translate" in query:
            text = query.replace("jarvis", "").replace("translate", "").strip()
            self._run(self._translate, text)

        elif "remember that" in query:
            note = query.replace("remember that", "").replace("jarvis", "").strip()
            self.say("You told me to " + note)
            with open(_path("Remember.txt"), "a") as f:
                f.write(note + "\n")

        elif "what do you remember" in query:
            try:
                with open(_path("Remember.txt")) as f:
                    self.say("You told me to " + f.read())
            except FileNotFoundError:
                self.say("You haven't told me anything to remember yet.")

        elif "shutdown system" in query:
            ans = self.ask("Do you wish to shut down your computer? (yes/no)")
            if (ans or "").strip().lower() == "yes":
                os.system("shutdown /s /t 1")

        # ------------------------------------------------ small talk
        elif "hello" in query:
            self.say("Hello sir, how are you?")
        elif "i am fine" in query:
            self.say("That's great, sir")
        elif "how are you" in query:
            self.say("Perfect, sir")
        elif "thank you" in query:
            self.say("You are welcome, sir")
        elif "tired" in query:
            self.say("Playing your favourite songs, sir")
            webbrowser.open("https://www.youtube.com/watch?v=U935BSVJIM0")

        # ------------------------------------------------ media keys
        elif "pause" in query:
            self._run(self._press, "k")
            self.say("Video paused")
        elif "play" in query:
            self._run(self._press, "k")
            self.say("Video played")
        elif "mute" in query:
            self._run(self._press, "m")
            self.say("Video muted")
        elif "volume up" in query:
            self.say("Turning volume up, sir")
            self._run(self._volume, +1)
        elif "volume down" in query:
            self.say("Turning volume down, sir")
            self._run(self._volume, -1)

        # ------------------------------------------------ tasks / focus
        elif "casual my day" in query:
            self._schedule_day()

        elif "show my schedule" in query:
            self._show_schedule()

        elif "focus mode" in query:
            ans = self.ask("Enter focus mode? This blocks social sites until a "
                           "time you choose. (yes/no)")
            if (ans or "").strip().lower() == "yes":
                self.say("Entering focus mode...")
                os.startfile(_path("FocusMode.py"))

        elif "show my focus" in query:
            self._run(self._focus_graph)

        elif "tell me my internet speed" in query:
            self._run(self._speedtest)

        elif "send message" in query:
            self._run(self._whatsapp)

        # ------------------------------------------------ generic open/close
        elif "open" in query:
            self._run(self._open_app, query)
        elif "close" in query:
            self._run(self._close_app, query)

        else:
            self.say("Sorry, I don't know that command yet. Try the quick "
                     "actions on the left or type 'help'.")

        return True

    # ------------------------------------------------------ implementations
    def _camera(self):
        import cv2
        cap = cv2.VideoCapture(0)
        self.say("Opening camera. Press Esc in the camera window to close it.")
        while True:
            ret, img = cap.read()
            if not ret:
                break
            cv2.imshow("webcam", img)
            if cv2.waitKey(50) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def _wikipedia(self, topic):
        import wikipedia
        self.say("Searching Wikipedia...")
        results = wikipedia.summary(topic.strip(), sentences=2)
        self.say("According to Wikipedia: " + results)

    def _play_on_yt(self, q):
        import pywhatkit
        pywhatkit.playonyt(q)

    def _search_google(self, query):
        import pywhatkit
        import wikipedia
        q = query.replace("jarvis", "").replace("google search", "").replace("google", "")
        self.say("This is what I found on Google")
        pywhatkit.search(q)
        try:
            self.say(wikipedia.summary(q, 1))
        except Exception:
            self.say("No speakable output available")

    def _search_youtube(self, query):
        import pywhatkit
        q = query.replace("youtube search", "").replace("youtube", "").replace("jarvis", "")
        self.say("This is what I found for your search!")
        webbrowser.open("https://www.youtube.com/results?search_query=" + q)
        pywhatkit.playonyt(q)
        self.say("Done, sir")

    def _screenshot(self):
        import pyautogui
        im = pyautogui.screenshot()
        im.save(_path("ss.jpg"))
        self.say("Screenshot saved as ss.jpg")

    def _click_picture(self):
        import pyautogui
        pyautogui.press("super")
        pyautogui.typewrite("camera")
        pyautogui.press("enter")
        pyautogui.sleep(2)
        self.say("SMILE")
        pyautogui.press("enter")

    def _translate(self, text):
        import googletrans
        from googletrans import Translator
        if not text:
            text = self.ask("What should I translate?")
        lang = self.ask("Target language code (e.g. fr, ur, es, de)")
        if not text or not lang:
            return
        lang = lang.strip().lower()
        if lang not in googletrans.LANGUAGES:
            self.say("Unknown language code. Examples: "
                     + ", ".join(list(googletrans.LANGUAGES)[:12]) + " ...")
            return
        result = Translator().translate(text, src="auto", dest=lang).text
        self.say(result)
        try:
            from gtts import gTTS
            from playsound import playsound
            gTTS(text=result, lang=lang, slow=False).save(_path("voice.mp3"))
            playsound(_path("voice.mp3"))
            os.remove(_path("voice.mp3"))
        except Exception:
            pass

    def _press(self, key):
        import pyautogui
        pyautogui.press(key)

    def _volume(self, direction):
        from keyboard import volumeup, volumedown
        (volumeup if direction > 0 else volumedown)()

    def _schedule_day(self):
        self.say("Do you want to clear old tasks? (yes/no)")
        ans = self.ask("Clear old tasks? (yes/no)")
        mode = "w" if (ans or "").strip().lower() == "yes" else "a"
        try:
            n = int(self.ask("How many tasks?") or 0)
        except ValueError:
            self.say("That wasn't a number.")
            return
        with open(_path("tasks.txt"), mode) as f:
            for i in range(n):
                task = self.ask(f"Task {i + 1}:")
                if task:
                    f.write(f"{i}. {task}\n")
        self.say(f"Saved {n} task(s).")

    def _show_schedule(self):
        try:
            with open(_path("tasks.txt")) as f:
                content = f.read().strip()
        except FileNotFoundError:
            content = ""
        if not content:
            self.say("You have no tasks saved. Say 'casual my day' to add some.")
            return
        self.say("Here is your schedule:\n" + content)
        try:
            from plyer import notification
            notification.notify(title="My schedule :-", message=content, timeout=15)
        except Exception:
            pass

    def _focus_graph(self):
        from FocusGraph import focus_graph
        focus_graph()

    def _speedtest(self):
        import speedtest
        self.say("Testing your internet speed, this can take a minute...")
        wifi = speedtest.Speedtest()
        down = wifi.download() / 1048576
        up = wifi.upload() / 1048576
        self.say(f"Download speed is {down:.1f} Mbps")
        self.say(f"Upload speed is {up:.1f} Mbps")

    def _whatsapp(self):
        import pywhatkit
        name = self.ask("Who would you like to send a message to?")
        msg = self.ask(f"What message would you like to send to {name}?")
        number = self.ask("Recipient's phone number (with country code, e.g. +92...)")
        if not (name and msg and number):
            return
        self.say(f"Sending message to {name}")
        now = datetime.datetime.now()
        pywhatkit.sendwhatmsg(number, msg, now.hour, now.minute + 1)

    def _open_app(self, query):
        from Dictapp import openappweb
        openappweb(query)

    def _close_app(self, query):
        from Dictapp import closeappweb
        closeappweb(query)
