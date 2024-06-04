
# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# import streamlit as st
# import requests
# from datetime import datetime, timedelta

# # Load environment variables
# load_dotenv()

# # Configure the GenAI API
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel('gemini-pro')

# def get_weather_data(city):
#     base_url = "https://api.meteomatics.com"
#     username = os.getenv("METEOMATICS_USERNAME")
#     password = os.getenv("METEOMATICS_PASSWORD")
    
#     # Get the current date and time
#     now = datetime.utcnow()
    
#     # Define the parameters for the API request
#     parameters = "t_2m:C,relative_humidity_2m:p"
    
#     # Define the URL for the API request
#     url = f"{base_url}/{now.strftime('%Y-%m-%dT%H:%M:%SZ')}/{parameters}/{city}/json"
    
#     try:
#         # Make the API request
#         response = requests.get(url, auth=(username, password))
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return None
#     except requests.exceptions.RequestException:
#         return None

# def display_weather_info(city):
#     weather_data = get_weather_data(city)
#     if weather_data:
#         st.subheader(f"Weather Forecast for {city}")
#         st.write(f"Temperature: {weather_data['data'][0]['coordinates'][0]['dates'][0]['value']}°C")
#         st.write(f"Relative Humidity: {weather_data['data'][1]['coordinates'][0]['dates'][0]['value']}%")
#     else:
#         st.warning("Failed to retrieve weather data.")

# def generate_summary(city, difficulty, length, elevation, season, pet_friendly, user_preferences):
#     prompt = f"""
#     Generate a summary of the user's hiking trail preferences based on the following information:
#     City: {city}
#     Difficulty Level: {difficulty}
#     Trail Length: {length} miles
#     Elevation Gain: {elevation} feet
#     Season: {season}
#     Pet-Friendly: {pet_friendly}
#     User Preferences: {user_preferences}
#     Start the summary with "Here are some recommendations based on your preferences:"
#     """
#     response = model.generate_content(prompt)
#     return response.text

# def generate_recommendations(city, difficulty, length, elevation, season, pet_friendly, user_preferences):
#     prompt = f"""
#     You are an expert in recommending hiking trails based on the city and user preferences.
#     Provide the top 5 hiking trails for the given city that match the user's specific needs.
#     Include a brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
#     City: {city}
#     Difficulty Level: {difficulty}
#     Trail Length: {length} miles
#     Elevation Gain: {elevation} feet
#     Season: {season}
#     Pet-Friendly: {pet_friendly}
#     User Preferences: {user_preferences}
#     """
#     response = model.generate_content(prompt)
#     return response.text

# def generate_popular_trails(city):
#     prompt = f"""
#     Provide the top 5 most popular and beautiful hiking trails in {city}, regardless of any specific filters.
#     Include a brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, and notable features.
#     """
#     response = model.generate_content(prompt)
#     return response.text

# # Home Page
# def home():
#     st.title("Hiking Trail Recommendations")
    
#     # City signature picture
#     st.image("https://example.com/city_image.jpg", use_column_width=True)
    
#     st.write("Enter a city to get personalized hiking trail recommendations.")
#     city = st.text_input("Enter the city")
#     if city:
#         st.session_state.city = city
#         st.experimental_rerun()

# # Search Page
# def search():
#     city = st.session_state.city
#     st.header(f"Search Hiking Trails in {city}")
    
#     # Weather Forecast
#     display_weather_info(city)
    
#     # Popular Trails
#     popular_trails = generate_popular_trails(city)
#     st.subheader(f"Top 5 Popular Trails in {city}")
#     st.write(popular_trails)
    
#     if st.button("Dismiss and Proceed to Search"):
#         st.experimental_rerun()
    
#     # Filter options
#     difficulty = st.selectbox("Difficulty Level", ["Easy", "Moderate", "Difficult"])
#     length = st.slider("Trail Length (miles)", min_value=0.0, max_value=10.0, step=0.5)
#     elevation = st.slider("Elevation Gain (feet)", min_value=0, max_value=1000, step=100)
#     season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
#     pet_friendly = st.checkbox("Pet-Friendly")
    
#     # Optional user preferences
#     user_preferences = st.text_area("Specific Needs (optional)", "")
    
#     # Generate recommendations button
#     if st.button("Get Recommendations"):
#         summary = generate_summary(city, difficulty, length, elevation, season, pet_friendly, user_preferences)
#         st.subheader("Summary of Your Preferences")
#         st.write(summary)
        
#         recommendations = generate_recommendations(city, difficulty, length, elevation, season, pet_friendly, user_preferences)
#         st.subheader("Recommended Hiking Trails")
#         st.write(recommendations)
    
#     # Back to city selection button
#     if st.button("Back to City Selection"):
#         st.session_state.pop("city", None)
#         st.experimental_rerun()

# # Main App
# def main():
#     if "city" not in st.session_state:
#         home()
#     else:
#         search()

# if __name__ == "__main__":
#     main()


import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import requests
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# Load environment variables
load_dotenv()

# Configure the GenAI API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def get_city_coordinates(city):
    geolocator = Nominatim(user_agent="hiking_trail_app")
    location = geolocator.geocode(city, timeout=5)  # Increase the timeout value (e.g., 5 seconds)
    if location:
        return location.latitude, location.longitude
    else:
        return None

def get_weather_data(latitude, longitude):
    base_url = "https://api.meteomatics.com"
    username = os.getenv("METEOMATICS_USERNAME")
    password = os.getenv("METEOMATICS_PASSWORD")
    
    # Get the current date and time
    now = datetime.utcnow()
    
    # Define the parameters for the API request
    parameters = "t_2m:C"
    
    # Define the URL for the API request
    url = f"{base_url}/{now.strftime('%Y-%m-%dT%H:%M:%SZ')}/{parameters}/{latitude},{longitude}/json"
    
    try:
        # Make the API request
        response = requests.get(url, auth=(username, password))
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None

def display_weather_info(city):
    coordinates = get_city_coordinates(city)
    if coordinates:
        latitude, longitude = coordinates
        weather_data = get_weather_data(latitude, longitude)
        if weather_data:
            st.subheader(f"Weather Forecast for {city}")
            temperature = weather_data['data'][0]['coordinates'][0]['dates'][0]['value']
            st.write(f"Temperature: {temperature}°C")
        else:
            st.warning("Failed to retrieve weather data.")
    else:
        st.warning("Failed to retrieve city coordinates.")

def generate_summary(city, difficulty, length, elevation, season, pet_friendly, user_preferences):
    prompt = f"""
    Generate a summary of the user's hiking trail preferences based on the following information:
    City: {city}
    Difficulty Level: {difficulty}
    Trail Length: {length} miles
    Elevation Gain: {elevation} feet
    Season: {season}
    Pet-Friendly: {pet_friendly}
    User Preferences: {user_preferences}
    Start the summary with "Here are some recommendations based on your preferences:"
    """
    response = model.generate_content(prompt)
    return response.text

def generate_recommendations(city, difficulty, length, elevation, season, pet_friendly, user_preferences):
    prompt = f"""
    You are an expert in recommending hiking trails based on the city and user preferences.
    Provide the top 5 hiking trails for the given city that match the user's specific needs.
    Include a brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
    City: {city}
    Difficulty Level: {difficulty}
    Trail Length: {length} miles
    Elevation Gain: {elevation} feet
    Season: {season}
    Pet-Friendly: {pet_friendly}
    User Preferences: {user_preferences}
    """
    response = model.generate_content(prompt)
    return response.text

def generate_popular_trails(city):
    prompt = f"""
    Provide the top 5 most popular and beautiful hiking trails in {city}, regardless of any specific filters.
    Include a brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, and notable features.
    """
    response = model.generate_content(prompt)
    return response.text

# Home Page
def home():
    st.title("Hiking Trail Recommendations")
    
    # City signature picture
    st.image("Garibaldi-Provincial-Park-Panorama-Ridge-Overnight-Backpacking-Trip-Sunset-BANNER-1.jpg", use_column_width=True)
    
    st.write("Enter a city to get personalized hiking trail recommendations.")
    city = st.text_input("Enter the city")
    if city:
        st.session_state.city = city
        st.experimental_rerun()

# Search Page
def search():
    city = st.session_state.city
    st.header(f"Search Hiking Trails in {city}")
    
    # Weather Forecast
    display_weather_info(city)
    
    # Popular Trails
    popular_trails = generate_popular_trails(city)
    st.subheader(f"Top 5 Popular Trails in {city}")
    st.write(popular_trails)
    
    if st.button("Dismiss and Proceed to Search"):
        st.experimental_rerun()
    
    # Filter options
    difficulty = st.selectbox("Difficulty Level", ["Easy", "Moderate", "Difficult"])
    length = st.slider("Trail Length (miles)", min_value=0.0, max_value=10.0, step=0.5)
    elevation = st.slider("Elevation Gain (feet)", min_value=0, max_value=1000, step=100)
    season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
    pet_friendly = st.checkbox("Pet-Friendly")
    
    # Optional user preferences
    user_preferences = st.text_area("Specific Needs (optional)", "")
    
    # Generate recommendations button
    if st.button("Get Recommendations"):
        summary = generate_summary(city, difficulty, length, elevation, season, pet_friendly, user_preferences)
        st.subheader("Summary of Your Preferences")
        st.write(summary)
        
        recommendations = generate_recommendations(city, difficulty, length, elevation, season, pet_friendly, user_preferences)
        st.subheader("Recommended Hiking Trails")
        st.write(recommendations)
    
    # Back to city selection button
    if st.button("Back to City Selection"):
        st.session_state.pop("city", None)
        st.experimental_rerun()

# Main App
def main():
    if "city" not in st.session_state:
        home()
    else:
        search()

if __name__ == "__main__":
    main()

