import speech_recognition as sr
import warnings
import os
import datetime
import calendar
import wikipedia
import webbrowser
import subprocess
import pyjokes
import time
import logging
from threading import Thread
from gtts import gTTS

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(filename='voice_assistant.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class SpeechInterface:
    def talk(self, audio):
        logging.info(f"Talking: {audio}")
        print(f"Alex says: {audio}")
        tts = gTTS(text=audio, lang='en')
        tts.save("response.mp3")
        os.system("mpg123 response.mp3")  # Requires mpg123 or use ffplay

    def rec_audio(self, timeout=5, phrase_time_limit=5):
        recog = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio = recog.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                data = recog.recognize_google(audio)
                print("You said: " + data)
                logging.info(f"Recognized: {data}")
                return data
            except sr.UnknownValueError:
                logging.error("Could not understand audio")
                self.talk("Sorry, I didn't catch that. Could you please repeat?")
                return ""
            except sr.RequestError as e:
                logging.error(f"Request error from Google Speech Recognition: {e}")
                self.talk("Sorry, I couldn't connect to the speech service.")
                return ""
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                self.talk("An error occurred. Please try again.")
                return ""

class Utilities:
    def today_date(self):
        now = datetime.datetime.now()
        date_now = datetime.datetime.today()
        week_now = calendar.day_name[date_now.weekday()]
        month_now = now.month
        day_now = now.day
        month = [
            "January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"
        ]
        ordinals = [
            "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th",
            "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th",
            "20th", "21st", "22nd", "23rd", "24th", "25th", "26th", "27th", "28th",
            "29th", "30th", "31st"
        ]
        return f'Today is {week_now}, {month[month_now-1]} the {ordinals[day_now-1]}.'

    def open_app(self, app_name):
        paths = {
            "chrome": "/usr/bin/google-chrome",
            "firefox": "/usr/bin/firefox",
            "code": "/usr/bin/code",
            "terminal": "/usr/bin/gnome-terminal"
        }
        path = paths.get(app_name.lower())
        if path and os.path.exists(path):
            subprocess.Popen([path])
        else:
            logging.error(f"Application {app_name} not found or path does not exist.")
            self.speech_interface.talk(f"Application {app_name} not found or path does not exist.")

    def note_taking(self, note_text):
        note_file = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "-note.txt"
        with open(note_file, "w") as f:
            f.write(note_text)
        subprocess.Popen(["gedit", note_file])  # or use another text editor
        logging.info(f"Note taken: {note_text}")

    def sleep_for_seconds(self, seconds):
        logging.info(f"Sleeping for {seconds} seconds")
        time.sleep(seconds)

class CommandProcessor:
    def __init__(self, speech_interface, utilities):
        self.speech_interface = speech_interface
        self.utilities = utilities

    def process_command(self, text):
        text = text.lower()
        if "date" in text or "day" in text or "month" in text:
            return self.utilities.today_date()

        if "time" in text:
            now = datetime.datetime.now()
            meridien = "p.m" if now.hour >= 12 else "a.m"
            hour = now.hour - 12 if now.hour > 12 else now.hour
            hour = 12 if hour == 0 else hour
            minute = f"{now.minute:02d}"
            return f"It is {hour}:{minute} {meridien}."

        if "who is" in text or "wikipedia" in text:
            person = text.split("who is ")[-1] if "who is" in text else text.split("wikipedia ")[-1]
            try:
                wiki = wikipedia.summary(person, sentences=2)
                return wiki
            except wikipedia.exceptions.DisambiguationError:
                return f"There are multiple entries for {person}, please be more specific."
            except wikipedia.exceptions.PageError:
                return f"I could not find any information on {person}."

        if "who are you" in text or "define yourself" in text:
            return "Hello, I am Alex, your personal assistant. You can command me to perform various tasks like opening applications or searching the web."

        if "your name" in text:
            return "My name is Alex."

        if "why do you exist" in text or "why did you come" in text:
            return "I exist to assist you with daily tasks and provide information at your command."

        if "how are you" in text:
            return "I am fine, thank you. How can I assist you today?"

        if "fine" in text or "good" in text:
            return "It is good to know that you are fine."

        if "open" in text:
            app_name = text.split("open ")[-1]
            return self.utilities.open_app(app_name)

        if "youtube" in text:
            search_query = text.split("youtube ")[-1]
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}")
            return f"Searching YouTube for {search_query}."

        if "search" in text or "google" in text:
            search_query = text.split("search ")[-1] if "search" in text else text.split("google ")[-1]
            webbrowser.open(f"https://www.google.com/search?q={search_query.replace(' ', '+')}")
            return f"Searching Google for {search_query}."

        if "empty recycle bin" in text:
            os.system("rm -rf ~/.local/share/Trash/*")
            return "Recycle bin emptied."

        if "note" in text or "remember this" in text:
            self.speech_interface.talk("What would you like me to write down?")
            note_text = self.speech_interface.rec_audio()
            if note_text:
                self.utilities.note_taking(note_text)
                return "I have made a note of that."

        if "joke" in text or "jokes" in text:
            return pyjokes.get_joke()

        if "where is" in text:
            location = text.split("where is ")[-1]
            url = f"https://www.google.com/maps/place/{location.replace(' ', '+')}"
            webbrowser.open(url)
            return f"This is where {location} is."

        if "don't listen" in text or "stop listening" in text or "do not listen" in text:
            self.speech_interface.talk("For how many seconds do you want me to sleep?")
            sleep_time = self.speech_interface.rec_audio()
            try:
                sleep_time = int(sleep_time)
                Thread(target=self.utilities.sleep_for_seconds, args=(sleep_time,)).start()
                return f"Sleeping for {sleep_time} seconds."
            except ValueError:
                return "I did not understand the number of seconds. Please try again."

        if "exit" in text or "quit" in text:
            return "Goodbye!"

        return "I don't know that."

class VoiceAssistant:
    def __init__(self):
        self.speech_interface = SpeechInterface()
        self.utilities = Utilities()
        self.command_processor = CommandProcessor(self.speech_interface, self.utilities)

    def run(self):
        while True:
            try:
                text = self.speech_interface.rec_audio()
                if not text:
                    continue

                response = self.command_processor.process_command(text)
                if response:
                    self.speech_interface.talk(response)
                if response == "Goodbye!":
                    break
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                self.speech_interface.talk("An error occurred. Please try again.")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
