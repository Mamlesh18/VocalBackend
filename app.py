from flask import Flask, render_template, request
import speech_recognition as sr
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
def clean_sql_query(query):
    return query.replace('```', '').strip()
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    sql_query = ""
    if request.method == "POST":
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio_clip = recognizer.listen(source)
            try:
                transcript = recognizer.recognize_google(audio_clip)
                # Call Gemini API to get the SQL query
                sql_query = get_sql_query(transcript)
            except sr.UnknownValueError:
                transcript = "Could not understand the audio."
            except sr.RequestError:
                transcript = "Failed to connect to Google API."
    
    return render_template("index.html", transcript=transcript, sql_query=sql_query)

def get_sql_query(transcript):
    if transcript:
        prompt = """
        give only query dont mention sql word
        You are an expert in converting English questions to Postgresql SQL queries!
        Also, the SQL code should not have ``` in the beginning or end, and no 'sql' word in the output.
        We need a single query even if there are multiple inputs from the user.
        Always the query will end with a semicolon.
        ex:
        sql -- no nede of this sql word
            CREATE TABLE human ();
        """
    response = get_gemini_response(transcript, prompt)
    cleaned_response = clean_sql_query(response)
    return cleaned_response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Ensure host and port are set

