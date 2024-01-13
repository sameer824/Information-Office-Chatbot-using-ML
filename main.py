import json
import pickle
import subprocess
import numpy as np
import pyttsx3
import speech_recognition as sr
import colorama
from colorama import Fore, Style
import tkinter as tk
from tkinter import scrolledtext, INSERT, END
from PIL import Image, ImageTk
import random
import threading
import socket
from keras.models import load_model
import nltk
from nltk.stem import WordNetLemmatizer
import database
from queue import Queue
import threading# Import the necessary modules and functions
import sqlite3
def is_internet_connected():
    try:
        host = socket.gethostbyname("www.google.com")
        socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

# Initialize colorama for colored output
colorama.init()

# Function to speak the bot's response
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("Text-to-speech error:", e)


# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load the model and other necessary data
model = load_model('chatbot_model.h5')
intents = json.loads(open('English.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)

    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1

    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []

    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})

    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ISP Chatbot")
        self.root.configure(bg="lightgray")
        self.max_len = 20
        # Create chat history area
        self.chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15, state='disabled')
        self.chat_history.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        
        # Configure grid weights for responsive resizing
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Create microphone icon button
        self.microphone_img = Image.open("microphone.png")  # Replace with your microphone icon image
        self.microphone_img = self.microphone_img.resize((50, 50), Image.ANTIALIAS)
        self.microphone_img = ImageTk.PhotoImage(self.microphone_img)
        self.microphone_btn = tk.Button(root, image=self.microphone_img, command=self.start_voice_input, bd=0, relief="flat", highlightthickness=0)
        self.microphone_btn.grid(row=1, column=0, padx=20, pady=10, sticky='w')
        # Create admin icon button
        self.admin_img = Image.open("admin.png")
        self.admin_img = self.admin_img.resize((50, 50), Image.LANCZOS)
        self.admin_img = ImageTk.PhotoImage(self.admin_img)
        self.admin_btn = tk.Button(root, image=self.admin_img, command=self.open_admin, bd=0, relief="flat", highlightthickness=0)
        self.admin_btn.grid(row=1, column=1, padx=20, pady=10, sticky='e')
        self.model = load_model('chatbot_model.h5')
        try:
            with open('English.json') as file:
                self.intents = json.load(file)
            self.words = pickle.load(open('words.pkl', 'rb'))
            self.classes = pickle.load(open('classes.pkl', 'rb'))
        except (FileNotFoundError, IOError):
            print("Failed to load data. Make sure the files exist.")
        self.add_message("Chatbot: Hello! How can I assist you")

    def add_message(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, message + "\n")
        self.chat_history.see(tk.END)  # Scroll to the bottom
        self.chat_history.config(state='disabled')
    
    def send_message_with_voice(self, user_message):
        if user_message != "":
            self.add_message("You: " + user_message)

            # Call the chatbot function to generate a response
            bot_response = self.chatbot_response(user_message)
            if bot_response is not None:
                self.add_message("Chatbot: " + bot_response)
                speak(bot_response)

    def open_admin(self):
        # Replace "admin.py" with the actual path to your admin.py file
        try:
            subprocess.Popen(["python", "AdminLoginWindow.py"])
        except Exception as e:
            print("Error opening admin.py:", e)

    def start_voice_input(self, event=None):
    # Disable the microphone button during speech recognition
        self.microphone_btn.config(state='disabled')

    # Use after() to schedule the voice input function
        self.root.after(0, self.get_voice_input)

    def get_voice_input(self):
        recognizer = sr.Recognizer()
        stt_engine = 'sphinx'

        if is_internet_connected():
            stt_engine = 'google'
        else:
            stt_engine = 'sphinx'

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(Fore.LIGHTBLUE_EX + "Listening... Speak now." + Style.RESET_ALL)
            audio = recognizer.listen(source)

        try:
            user_input = recognizer.recognize_google(audio)
            print(user_input)
            if user_input.lower() in ['quit', 'stop', 'exit', 'goodbye']:
                print(Fore.YELLOW + "Goodbye!" + Style.RESET_ALL)
                speak("Goodbye!")
                self.root.quit()
            else:
                self.root.after(0, self.send_message_with_voice, user_input)  # Schedule GUI update

        except sr.UnknownValueError:
            # If the speech recognition could not understand the input
            print(Fore.RED + "ChatBot: " + Style.RESET_ALL, "Sorry, I couldn't understand that. Please try again.")
            speak("Sorry, I couldn't understand that. Please try again.")
        except sr.RequestError:
            # If there was a problem connecting to the speech recognition service
            print(Fore.RED + "ChatBot: " + Style.RESET_ALL, "Sorry, there was an error connecting to the speech recognition service.")
            speak("Sorry, there was an error connecting to the speech recognition service.")
        except Exception as e:
            # Other unexpected errors
            print(Fore.RED + "ChatBot: " + Style.RESET_ALL, "Sorry, there was an unexpected error:", e)
            speak("Sorry, there was an unexpected error. Please try again.")

        self.root.after(0, self.enable_microphone_button)  # Schedule GUI update
    
    def enable_microphone_button(self):
        self.microphone_btn.config(state='normal')
        
    def chatbot_response(self, user_input):
        result = model.predict(np.array([bow(user_input, self.words)]))
        tag = classes[np.argmax(result)]
        for intent in self.intents['intents']:
            if intent['tag'] == tag:
                response = random.choice(intent['responses'])
                self.add_message("Chatbot: " + response)
                speak(response)
                # Add the chat interaction to the database
    
                user_id = None  # If you need to associate specific users, replace with the user's ID
                # Replace these lines with the actual function from the database module
# database(admin_id, user_id, user_input, response)

# Call a function from the 'database' module to insert the chat history
                database.insert_chat_message( user_id, user_input, response)

                break

    def enable_close(self):
        # This function is called when the window is closed
        database.close_connection()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x500")  # Set an initial size for the window
    chatbot_gui = ChatbotGUI(root)
    root.protocol("WM_DELETE_WINDOW", chatbot_gui.enable_close)  # Handle window close event
    root.mainloop()
    database.close_connection()