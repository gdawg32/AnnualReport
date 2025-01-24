import google.generativeai as genai
from django.utils.timezone import localtime
from .models import Achievement
from datetime import date

# Configure Gemini API
genai.configure(api_key="AIzaSyCj5c6PRO1cKvBmRJ2jq-vwaKw0yo9CA0g")
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to fetch all achievements
def fetch_achievements():
    achievements = Achievement.objects.all()
    return achievements

# Function to process achievement data and format it for Gemini API
def process_achievements(achievements):
    achievements_data = []

    for achievement in achievements:
        achievement_info = {
            "title": achievement.title,
            "description": achievement.description,
            "awardee": achievement.awarded_to,
            "date": localtime(achievement.date_awarded).strftime('%B %d, %Y'),
            "image": achievement.image
        }
        achievements_data.append(achievement_info)

    return achievements_data

# Function to generate a report using Gemini API
def generate_report(achievements_data):
    # Format the input text to pass to the Gemini API
    achievements_text = "Here is the list of achievements:\n\n"
    
    for data in achievements_data:
        achievements_text += f"Title: {data['title']}\n"
        achievements_text += f"Description: {data['description']}\n"
        achievements_text += f"Awarded to: {data['awardee']}\n"
        achievements_text += f"Awarded on: {data['date']}\n"
    
    # Use Gemini API to generate a report based on the achievements
    response = model.generate_content(achievements_text)
    return response.text