import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyCj5c6PRO1cKvBmRJ2jq-vwaKw0yo9CA0g")
model = genai.GenerativeModel('gemini-1.5-flash')

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
