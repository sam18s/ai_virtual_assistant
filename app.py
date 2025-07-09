from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time
from datetime import datetime
import speech_recognition as sr
import webbrowser
import threading
import requests
import random
import os
import re
import wikipedia
import pyjokes
import subprocess
import platform
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from geopy.geocoders import Nominatim
from PyDictionary import PyDictionary
import webbrowser
from googletrans import Translator
import webbrowser
import urllib.parse
import pytz
from pdf_converter.routes import pdf_bp
from speech_recog.routes import speech_bp 

# Initialize Flask app
app = Flask(__name__)

# Load secrets from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Register Blueprints
app.register_blueprint(pdf_bp, url_prefix='/pdf') 
app.register_blueprint(speech_bp, url_prefix='/speech')

dictionary = PyDictionary()
translator = Translator()

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that. Could you repeat?"
        except sr.RequestError as e:
            return "Sorry, my speech service is down."
        

def get_weather(city):
    """Fetches weather information for a given city using OpenWeatherMap API."""
    api_key = "fc3380c0294c5688f37a2a395cad0e76"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            return f"The weather in {city.title()} is {weather_desc} with a temperature of {temp}°C and humidity of {humidity}%."
        elif response.status_code == 404:
            return f"City '{city}' not found. Please check the city name and try again."
        else:
            return "Unable to fetch weather details at the moment. Please try again later."
    except Exception as e:
        return f"An error occurred: {str(e)}. Unable to fetch weather details."

def get_news(query=None):
    api_key = "abe0b7347adb4be7a92e0e12c0bcc8ca"
    if query:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"
    else:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    try:
        response = requests.get(url)
        news_data = response.json()
        if news_data["status"] == "ok":
            articles = news_data["articles"][:5]  # Get top 5 articles
            news = "\n".join([f"{i+1}. {article['title']}" for i, article in enumerate(articles)])
            return news
        else:
            return "Unable to fetch news."
    except Exception:
        return "Unable to fetch news at the moment."

def get_random_advice():
    advice_list = [
        "Always be kind to others.",
        "Take breaks when working for long hours.",
        "Learn something new every day.",
        "Stay hydrated and drink plenty of water.",
        "Believe in yourself and your abilities.",
        "Focus on progress, not perfection.",
        "Surround yourself with positive people.",
        "Practice gratitude daily.",
        "Don't be afraid to ask for help.",
        "Take care of your mental health.",
    ]
    return random.choice(advice_list)

def calculate_math(expression):
    try:
        # Allow only valid characters: digits, operators, parentheses, and spaces
        if re.match(r'^[\d\s+\-*/().]+$', expression):
            # Evaluate the expression safely
            result = eval(expression)
            return f"The result is {result}."
        else:
            return "Invalid mathematical expression."
    except Exception as e:
        return "Sorry, I couldn't calculate that."

def search_youtube(query):
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Searching YouTube for {query}."

def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching Google for {query}."

def close_program(program_name):
    try:
        os.system(f"taskkill /f /im {program_name}")
        return f"Closed {program_name}."
    except Exception as e:
        return f"Sorry, I couldn't close {program_name}."

def play_music_on_youtube():
    command = take_command()
    if command:
        webbrowser.open(f"https://www.youtube.com/results?search_query={command.replace(' ', '+')}")
        return f"Searching YouTube for {command}."
    else:
        return "Sorry, I didn't catch the song name."

    
def check_internet_speed():
    webbrowser.open("https://www.speedtest.net/")
    return "Opening Speedtest to check your internet speed."

def set_alarm(alarm_time):
    def alarm():
        while True:
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == alarm_time:
                return "Time's up! Alarm ringing."
                break
            time.sleep(10)

    threading.Thread(target=alarm).start()
    return f"Alarm set for {alarm_time}."

def set_reminder(reminder_text, reminder_time):
    def reminder():
        while True:
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == reminder_time:
                return f"Reminder: {reminder_text}"
                break
            time.sleep(10)

    threading.Thread(target=reminder).start()
    return f"Reminder set for {reminder_time}."

def get_system_info():
    system_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Processor": platform.processor(),
        "Architecture": platform.machine(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
    }
    return system_info

def convert_currency(amount, from_currency, to_currency):
    api_key = "56e01d8ca77d7875cd8276ef"  # Replace with your API key
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    try:
        response = requests.get(url)
        data = response.json()
        rate = data['rates'][to_currency]
        converted_amount = amount * rate
        return f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}."
    except Exception as e:
        return "Sorry, I couldn't convert the currency."


def search_nearby_places(place_type, location):
    geolocator = Nominatim(user_agent="assistant")
    location = geolocator.geocode(location)
    if location:
        latitude, longitude = location.latitude, location.longitude
        return f"Searching for {place_type} near {location.address}."
    else:
        return "Sorry, I couldn't find the location."


def get_word_synonyms(word):
    synonyms = dictionary.synonym(word)
    if synonyms:
        return synonyms
    else:
        return "Sorry, I couldn't find synonyms for that word."

def get_word_antonyms(word):
    antonyms = dictionary.antonym(word)
    if antonyms:
        return antonyms
    else:
        return "Sorry, I couldn't find antonyms for that word."

ist = pytz.timezone('Asia/Kolkata')

# ------------------ Database Model ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(ist))

with app.app_context():
    db.create_all()


# Dictionary of supported sites
site_urls = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "manipal university": "https://student.onlinemanipal.com/s/",
    "github": "https://github.com",
    "chatgpt": "https://chat.openai.com",
    "linkedin": "https://www.linkedin.com/",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "twitter": "https://twitter.com",
    "reddit": "https://www.reddit.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "drive": "https://drive.google.com",
    "maps": "https://maps.google.com",
    "spotify": "https://open.spotify.com",
    "discord": "https://discord.com",
    "zoom": "https://zoom.us",
    "stackoverflow": "https://stackoverflow.com",
    "wikipedia": "https://www.wikipedia.org",
    "speedtest": "https://www.speedtest.net"
}

# ------------------ Routes ------------------

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


# ------------------ AI Assistant Logic ------------------

@app.route('/execute_command', methods=['POST'])
def execute_command():
    data = request.json
    text = data.get('text', '').lower()
    ai_response = ""

    if "how are you" in text or "kaise ho" in text:
        ai_response = "I am absolutely fine. What about you?"

    # Ask with AI (ChatGPT)
    elif "ask with ai" in text or "lucy" in text:
        query = text.replace("ask with ai", "").replace("lucy", "").strip()
        if query:
            encoded_query = urllib.parse.quote(query)
            url = f"https://chat.openai.com/?q={encoded_query}"
            ai_response = f"Asking AI about: {query}"
            return jsonify({'ai_response': ai_response, 'url': url})
        else:
            ai_response = "What would you like me to ask the AI?"
            
    # Open website command
    elif "open" in text:
        site_found = False
        for site_name, site_url in site_urls.items():
            if site_name in text:
                ai_response = f"Opening {site_name}..."
                return jsonify({'ai_response': ai_response, 'url': site_url})
        
        if not site_found:
            site_name = text.replace("open", "").strip()
            search_url = f"https://www.google.com/search?q={site_name}"
            ai_response = f"I couldn't find a direct link for {site_name}, so I searched it on Google."
            return jsonify({'ai_response': ai_response, 'url': search_url})



    elif 'time' in text:
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime("%I:%M %p")
        ai_response = f"The current time is {current_time}."

    elif 'date' in text or 'day' in text:
        current_date = datetime.now().strftime("%A, %d %B %Y")
        ai_response = f"Today is {current_date}."

    # Search on Google
    elif "search on google" in text or "google search" in text:
        query = text.replace("search on google", "").replace("google search", "").strip()
        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            ai_response = f"Searching Google for {query}"
            return jsonify({'ai_response': ai_response, 'url': url})
        else:
            ai_response = "What would you like me to search on Google?"
            return jsonify({'ai_response': ai_response})

    # Search on YouTube
    elif "search on youtube" in text or "youtube search" in text:
        query = text.replace("search on youtube", "").replace("youtube search", "").strip()
        if query:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            ai_response = f"Searching YouTube for {query}"
            return jsonify({'ai_response': ai_response, 'url': url})
        else:
            ai_response = "What would you like me to search on YouTube?"
            return jsonify({'ai_response': ai_response})

    elif 'weather' in text:
        city_match = re.search(r'weather(?: in)? (.+)', text)
        if city_match:
            city = city_match.group(1).strip()
            ai_response = get_weather(city)
        else:
            ai_response = "Please specify a city for the weather details."
    
    elif "who invented you" in text or "who made you" in text:
        ai_response = "I was created by Samiksha"

    elif "what is your name" in text:
        ai_response = "my name is lucy."

    elif "tell me about yourself" in text:
        ai_response = "Hello! I am Lucy AI, a highly intelligent virtual assistant designed to efficiently perform various tasks and provide seamless assistance. How may I help you?"

    elif "thank you" in text or "thanks" in text:
        ai_response = "You're welcome!"

    elif "bye" in text:
        ai_response = "Goodbye! Have a great day ahead."

    elif "good morning" in text:
        ai_response = "Good morning! I hope you have a productive day 😊"

    elif "nice to meet you" in text:
        ai_response = "Nice to meet you too! 😊 How can I help you today?"
    
    elif "i am fine" in text:
        ai_response = "Good 😊 How can I help you today?"

    elif "good night" in text:
        ai_response = "Good night! Sweet dreams 🌙"

    elif "hello" in text or "hii" in text:
        ai_response = "Hello! How can I assist you today?"

    elif "love you" in text:
        ai_response = "Aww, thank you! I'm always here for you ❤️"

    elif "who are you" in text:
        ai_response = "I’m your personal AI assistant created by Samiksha!"

    elif "i am sad" in text:
        ai_response = "I'm here for you. Everything will be alright 🌈"

    elif "i am happy" in text:
        ai_response = "Yay! That’s great to hear! 😊"

    elif "sing a song" in text:
        ai_response = "La la la 🎶 I would, but I might crash your speakers!"

    elif "tell me something" in text:
        ai_response = "Did you know? Honey never spoils. Archaeologists found 3,000-year-old honey in Egypt that’s still edible!"

    elif "what can you do" in text:
        ai_response = "I can help you search, speech, pdf convert, open sites, take notes, and more!"

    elif 'news' in text:
        topic = text.replace('news about', '').strip()
        ai_response = get_news(topic)

    elif 'advice' in text:
        ai_response = get_random_advice()

    elif 'calculate' in text:
        expression = text.replace('calculate', '').strip()
        ai_response = calculate_math(expression)

    elif 'wikipedia' in text:
        query = text.replace('search on wikipedia', '').strip()
        try:
            results = wikipedia.summary(query, sentences=10)
            ai_response = results
        except Exception:
            ai_response = "Sorry, I couldn't find anything on Wikipedia."

    elif 'joke' in text:
        ai_response = pyjokes.get_joke()


    # Check internet speed
    elif "check internet speed" in text or "speed test" in text:
        ai_response = "Opening Speedtest to check your internet speed."
        return jsonify({'ai_response': ai_response, 'url': site_urls['speedtest']})

    elif "set alarm" in text:
        ai_response = "What time should I set the alarm?"
        alarm_time = take_command()
        ai_response = set_alarm(alarm_time)

    elif "set reminder" in text:
        ai_response = "What should I remind you about?"
        reminder_text = take_command()
        ai_response = "When should I remind you?"
        reminder_time = take_command()
        ai_response = set_reminder(reminder_text, reminder_time)

    elif "system information" in text:
        system_info = get_system_info()
        ai_response = "Here is your system information:\n" + "\n".join([f"{key}: {value}" for key, value in system_info.items()])

    elif "convert currency" in text:
        ai_response = "How much do you want to convert?"
        amount = float(take_command())
        ai_response = "From which currency?"
        from_currency = take_command().upper()
        ai_response = "To which currency?"
        to_currency = take_command().upper()
        ai_response = convert_currency(amount, from_currency, to_currency)


    # Location/nearby places
    elif "nearby" in text or "find" in text or "location" in text:
        try:
            query = ""
            if "nearby" in text:
                query = text.split("nearby")[-1].strip()
            elif "find" in text:
                query = text.split("find")[-1].strip()
            elif "location" in text:
                query = text.split("location")[-1].strip()

            if query:
                search_query = urllib.parse.quote(f"{query} near me")
                maps_url = f"https://www.google.com/maps/search/{search_query}"
                ai_response = f"Searching for {query} near you..."
                return jsonify({'ai_response': ai_response, 'url': maps_url})
            else:
                ai_response = "Please specify what you're looking for nearby."
        except Exception as e:
            ai_response = f"Sorry, I couldn't search maps: {str(e)}"
            

    elif "synonyms of" in text:
        word = text.replace("synonyms of", "").strip()
        ai_response = get_word_synonyms(word)

    elif "antonyms of" in text:
        word = text.replace("antonyms of", "").strip()
        ai_response = get_word_antonyms(word)

    # elif "search" in text or "who is" in text or "what is" in text:
    #     query = text.replace("search on google", "").replace("google search", "").strip()
    #     if query:
    #         url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    #         ai_response = f"Searching Google for {query}"
    #         return jsonify({'ai_response': ai_response, 'url': url})
    #     else:
    #         ai_response = "What would you like me to search on Google?"
    #         return jsonify({'ai_response': ai_response})

    elif any(x in text.lower() for x in ["search", "who is", "what is", "google search", "search on google"]):
        # Convert to lowercase for consistent processing
        query = text.lower()

        # Remove trigger phrases from the beginning
        for phrase in ["search on google", "google search", "search", "who is", "what is"]:
            if query.startswith(phrase):
                query = query.replace(phrase, "", 1).strip()
                break  # Remove only one matching prefix

        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            ai_response = f"Searching Google for {query}"
            return jsonify({'ai_response': ai_response, 'url': url})
        else:
            ai_response = "What would you like me to search on Google?"
            return jsonify({'ai_response': ai_response})


    print(f"AI Response: {ai_response}")
    return jsonify({"user_input": text, "ai_response": ai_response}), 200

if __name__ == '__main__':
    app.run(debug=True)  



