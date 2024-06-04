import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import requests
from datetime import datetime, timedelta
from requests.exceptions import RequestException, JSONDecodeError

# Load environment variables
load_dotenv()

# Configure the GenAI API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def generate_recommendations(city):
    prompt = f"""
    You are an expert in recommending hiking trails based on the city.
    Provide the top 5 hiking trails for the given city.
    Include a brief description of each trail, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
    City: {city}
    """
    response = model.generate_content(prompt)
    return response.text

def generate_filtered_recommendations(city, difficulty, length, elevation, season, pet_friendly):
    prompt = f"""
    You are an expert in recommending hiking trails based on the city and specified filters.
    Provide the top 5 hiking trails for the given city that match the following criteria:
    - Difficulty Level: {difficulty}
    - Maximum Trail Length: {length} miles
    - Maximum Elevation Gain: {elevation} feet
    - Season: {season}
    - Pet-Friendly: {pet_friendly}
    Include a brief description of each trail, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
    City: {city}
    """
    response = model.generate_content(prompt)
    return response.text

def get_weather_data(city):
    base_url = "https://api.meteomatics.com"
    username = os.getenv("METEOMATICS_USERNAME")
    password = os.getenv("METEOMATICS_PASSWORD")
    
    # Get the current date and time
    now = datetime.utcnow()
    
    # Define the parameters for the API request
    params = {
        "connector": "python_v1.0.0",
        "time_series_start": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "time_series_end": (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parameter": "t_2m:C,relative_humidity_2m:p",
        "location": f"{city}",
        "format": "json"
    }
    
    try:
        # Make the API request
        response = requests.get(base_url, auth=(username, password), params=params)
        
        print(f"API Request URL: {response.url}")
        print(f"API Response Status Code: {response.status_code}")
        print(f"API Response Content: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except (RequestException, JSONDecodeError) as e:
        print(f"Error: {str(e)}")
        return None

def display_weather_info(city):
    weather_data = get_weather_data(city)
    if weather_data:
        st.subheader(f"Weather Forecast for {city}")
        st.write(f"Temperature: {weather_data['data'][0]['coordinates'][0]['dates'][0]['value']}°C")
        st.write(f"Relative Humidity: {weather_data['data'][1]['coordinates'][0]['dates'][0]['value']}%")
    else:
        st.warning("Failed to retrieve weather data.")
        
# Home Page
def home():
    st.title("Hiking Trail Recommendations")
    st.write("Enter a city to get personalized hiking trail recommendations.")
    city = st.text_input("Enter the city")
    if city:
        st.session_state.city = city
        option = st.selectbox("Select an option", ["Search on Your Own", "Get Personalized Recommendation"])
        if option == "Search on Your Own":
            st.session_state.page = "search"
        else:
            st.session_state.page = "recommendation"
        st.experimental_rerun()

# Search Page
def search():
    city = st.session_state.city
    st.header(f"Search Hiking Trails in {city}")
    
    # Weather Forecast
    display_weather_info(city)
    
    # Filter options
    difficulty = st.selectbox("Difficulty Level", ["Easy", "Moderate", "Difficult"])
    length = st.slider("Trail Length (miles)", min_value=0.0, max_value=10.0, step=0.5)
    elevation = st.slider("Elevation Gain (feet)", min_value=0, max_value=1000, step=100)
    season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
    pet_friendly = st.checkbox("Pet-Friendly")
    
    if st.button("Apply Filters"):
        filtered_recommendations = generate_filtered_recommendations(city, difficulty, length, elevation, season, pet_friendly)
        st.write(filtered_recommendations)
    
    if st.button("Back to Home"):
        st.session_state.pop("page", None)
        st.experimental_rerun()

# Recommendation Page
def recommendation():
    city = st.session_state.city
    st.header(f"Personalized Hiking Trail Recommendations for {city}")
    
    if st.button("Get Recommendations"):
        recommendations = generate_recommendations(city)
        st.write(recommendations)
    
    if st.button("Back to Home"):
        st.session_state.pop("page", None)
        st.experimental_rerun()

# Main App
def main():
    if "page" not in st.session_state:
        home()
    elif st.session_state.page == "search":
        search()
    elif st.session_state.page == "recommendation":
        recommendation()

if __name__ == "__main__":
    main()
# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# import streamlit as st

# # Load environment variables
# load_dotenv()

# # Configure the GenAI API
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel('gemini-pro')

# def generate_recommendations(city):
#     prompt = f"""
#     You are an expert in recommending hiking trails based on the city.
#     Provide the top 5 hiking trails for the given city.
#     Include a brief description of each trail, its difficulty level, length, elevation gain, and any notable features.
#     City: {city}
#     """
#     response = model.generate_content(prompt)
#     return response.text

# def generate_filtered_recommendations(city, difficulty, length, elevation):
#     prompt = f"""
#     You are an expert in recommending hiking trails based on the city and specified filters.
#     Provide the top 5 hiking trails for the given city that match the following criteria:
#     - Difficulty Level: {difficulty}
#     - Maximum Trail Length: {length} miles
#     - Maximum Elevation Gain: {elevation} feet
#     Include a brief description of each trail, its difficulty level, length, elevation gain, and any notable features.
#     City: {city}
#     """
#     response = model.generate_content(prompt)
#     return response.text

# # Home Page
# def home():
#     st.title("Hiking Trail Recommendations")
#     st.write("Enter a city to get personalized hiking trail recommendations.")
#     city = st.text_input("Enter the city")
#     if st.button("Get Recommendations"):
#         st.session_state.city = city
#         st.rerun()

# # Recommendations Page
# def recommendations():
#     if "city" not in st.session_state:
#         st.warning("Please enter a city on the Home Page first.")
#         return
    
#     city = st.session_state.city
#     st.header(f"Hiking Trails in {city}")
    
#     # LLM-powered Recommendations
#     if st.button("Get Personalized Recommendations"):
#         recommendations = generate_recommendations(city)
#         st.write(recommendations)
    
#     # Self-Searching with Filters
#     st.subheader("Filter Trails")
#     difficulty = st.selectbox("Difficulty Level", ["Easy", "Moderate", "Difficult"])
#     length = st.slider("Trail Length (miles)", min_value=0.0, max_value=10.0, step=0.5)
#     elevation = st.slider("Elevation Gain (feet)", min_value=0, max_value=1000, step=100)
    
#     if st.button("Apply Filters"):
#         filtered_recommendations = generate_filtered_recommendations(city, difficulty, length, elevation)
#         st.write(filtered_recommendations)
    
#     if st.button("Back to Home"):
#         st.rerun()

# # Main App
# def main():
#     page = st.sidebar.selectbox("Select a page", ["Home", "Recommendations"])
    
#     if page == "Home":
#         home()
#     elif page == "Recommendations":
#         recommendations()

# if __name__ == "__main__":
#     main()
