import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import requests
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import json

# Load environment variables
load_dotenv()

# Configure the GenAI API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def get_city_coordinates(city):
    geolocator = Nominatim(user_agent="hiking_trail_app")
    try:
        location = geolocator.geocode(city, timeout=5)
        if location:
            return location.latitude, location.longitude
        else:
            st.warning("City not found. Please check the spelling or try another city.")
            return None
    except Exception as e:
        st.error(f"Error fetching city coordinates: {e}")
        return None

def get_weather_data(latitude, longitude):
    base_url = "https://api.meteomatics.com"
    username = os.getenv("METEOMATICS_USERNAME")
    password = os.getenv("METEOMATICS_PASSWORD")
    
    now = datetime.utcnow()
    parameters = "t_2m:C,weather_symbol_1h:idx,t_min_2m_24h:C,t_max_2m_24h:C,precip_type_5min:idx"
    time_range = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')},{(now + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')},{(now + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')},{(now + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')}"
    url = f"{base_url}/{time_range}/{parameters}/{latitude},{longitude}/json"
    
    try:
        response = requests.get(url, auth=(username, password))
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Failed to retrieve weather data.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
        return None

weather_emojis = {
    1: "☀️",  # Clear sky
    2: "⛅",  # Partly cloudy
    3: "☁️",  # Cloudy
    4: "🌧️",  # Rain
    5: "🌨️",  # Rain and snow mixed
    6: "❄️",  # Snow
    7: "🌨️",  # Sleet
    8: "🌧️❄️",  # Freezing rain
    9: "🌨️"   # Hail
}

def display_weather_info(city):
    coordinates = get_city_coordinates(city)
    if coordinates:
        latitude, longitude = coordinates
        weather_data = get_weather_data(latitude, longitude)
        if weather_data:
            st.subheader(f"Weather Forecast for {city}")

            # Current temperature and precipitation type
            current_temp = weather_data['data'][0]['coordinates'][0]['dates'][0]['value'] if weather_data['data'] and weather_data['data'][0]['coordinates'] else "N/A"
            current_precip_type = weather_data['data'][4]['coordinates'][0]['dates'][0]['value'] if weather_data['data'] and weather_data['data'][4]['coordinates'] else 0
            current_emoji = weather_emojis.get(current_precip_type, "")
            st.write(f"Current Temperature: {current_temp}°C {current_emoji}")

            # Weather forecast for the next 3 days
            forecast_data = []
            for i in range(1, 4):
                if weather_data['data'] and weather_data['data'][0]['coordinates'] and len(weather_data['data'][0]['coordinates'][0]['dates']) > i:
                    date = weather_data['data'][0]['coordinates'][0]['dates'][i]['date']
                    min_temp = weather_data['data'][2]['coordinates'][0]['dates'][i]['value'] if weather_data['data'] and weather_data['data'][2]['coordinates'] else "N/A"
                    max_temp = weather_data['data'][3]['coordinates'][0]['dates'][i]['value'] if weather_data['data'] and weather_data['data'][3]['coordinates'] else "N/A"
                    precip_type = weather_data['data'][4]['coordinates'][0]['dates'][i]['value'] if weather_data['data'] and weather_data['data'][4]['coordinates'] else 0
                    emoji = weather_emojis.get(precip_type, "")
                    forecast_data.append({"date": date, "min_temp": min_temp, "max_temp": max_temp, "emoji": emoji})

            # Display weather forecast
            for day in forecast_data:
                date = datetime.strptime(day['date'], "%Y-%m-%dT%H:%M:%SZ").strftime("%a, %b %d")
                st.write(f"{day['emoji']} {date}: {day['min_temp']}°C - {day['max_temp']}°C")
        else:
            st.warning("Failed to retrieve weather data.")
    else:
        st.warning("Please enter a valid city.")

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
    Include a paragraph yet brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
    Format the response as follows:
    Trail 1:
    Name: [Trail Name]
    Description: [Trail Description]
    Difficulty: [Trail Difficulty]
    Length: [Trail Length]
    Elevation Gain: [Elevation Gain]
    Pet-Friendly: [pet_friendly]
    Notable Features: [Notable Features]
    AllTrails Link: [AllTrails Link]

    ...

    Trail 5:
    Name: [Trail Name]
    Description: [Trail Description]
    Difficulty: [Trail Difficulty]
    Length: [Trail Length]
    Elevation Gain: [Elevation Gain]
    Pet-Friendly: [pet_friendly]
    Notable Features: [Notable Features]
    AllTrails Link: [AllTrails Link]

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
    Include a paragraph yet brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
    Format the response as follows:
    Trail 1:
    Name: [Trail Name]
    Description: [Trail Description]
    Difficulty: [Trail Difficulty]
    Length: [Trail Length]
    Elevation Gain: [Elevation Gain]
    Notable Features: [Notable Features]
    AllTrails Link: [AllTrails Link]

    ...

    Trail 5:
    Name: [Trail Name]
    Description: [Trail Description]
    Difficulty: [Trail Difficulty]
    Length: [Trail Length]
    Elevation Gain: [Elevation Gain]
    Notable Features: [Notable Features]
    AllTrails Link: [AllTrails Link]
    """
    response = model.generate_content(prompt)
    return response.text

def home():
    st.title("Hiking Trail Recommendations")
    
    st.image("Garibaldi-Provincial-Park-Panorama-Ridge-Overnight-Backpacking-Trip-Sunset-BANNER-1.jpg", use_column_width=True)
    
    st.write("Enter a city to get personalized hiking trail recommendations.")
    city = st.text_input("Enter the city")
    if city:
        st.session_state.city = city
        st.rerun()

def display_popular_trails(city):
    st.header(f"Top 5 Popular Trails in {city}")
    popular_trails = generate_popular_trails(city)
    
    trails = popular_trails.split("\n\n")
    for trail in trails:
        if trail.strip():
            trail_info = trail.split("\n")
            for info in trail_info:
                if info.startswith("Name:"):
                    st.subheader(info.split(": ")[1])
                elif info.startswith("AllTrails Link:"):
                    st.write(f"[AllTrails Link]({info.split(': ')[1]})")
                else:
                    st.write(info)
            st.write("---")
    
    if st.button("Dismiss and Proceed to Search"):
        st.session_state.show_search_filters = True
        st.rerun()

def display_search_filters(city):
    st.header(f"Search Hiking Trails in {city}")
    
    display_weather_info(city)
    
    difficulty = st.selectbox("Difficulty Level", ["Easy", "Moderate", "Difficult"])
    length = st.slider("Trail Length (miles)", min_value=0.0, max_value=10.0, step=0.5)
    elevation = st.slider("Elevation Gain (feet)", min_value=0, max_value=1000, step=100)
    season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
    pet_friendly = st.checkbox("Pet-Friendly")
    
    user_preferences = st.text_area("Specific Needs (optional)", "")
    
    if st.button("Get Recommendations"):
        summary = generate_summary(city, difficulty, length, elevation, season, pet_friendly, user_preferences)
        st.subheader("Summary of Your Preferences")
        st.write(summary)
        
        recommendations = generate_recommendations(city, difficulty, length, elevation, season, pet_friendly, user_preferences)
        st.subheader("Recommended Hiking Trails")
        
        trails = recommendations.split("\n\n")
        for trail in trails:
            if trail.strip():
                trail_info = trail.split("\n")
                for info in trail_info:
                    if info.startswith("Name:"):
                        st.subheader(info.split(": ")[1])
                    elif info.startswith("AllTrails Link:"):
                        st.write(f"[AllTrails Link]({info.split(': ')[1]})")
                    else:
                        st.write(info)
                st.write("---")
    
    if st.button("Back to City Selection"):
        st.session_state.pop("city", None)
        st.session_state.pop("show_search_filters", None)
        st.rerun()

def search():
    city = st.session_state.city
    
    if "show_search_filters" not in st.session_state:
        display_popular_trails(city)
    else:
        display_search_filters(city)

def main():
    if "city" not in st.session_state:
        home()
    else:
        search()

if __name__ == "__main__":
    main()



# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# import streamlit as st
# import requests
# from datetime import datetime, timedelta
# from geopy.geocoders import Nominatim
# import json

# # Load environment variables
# load_dotenv()

# # Configure the GenAI API
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel('gemini-pro')

# def get_city_coordinates(city):
#     geolocator = Nominatim(user_agent="hiking_trail_app")
#     location = geolocator.geocode(city, timeout=5)
#     if location:
#         return location.latitude, location.longitude
#     else:
#         return None

# def get_weather_data(latitude, longitude):
#     base_url = "https://api.meteomatics.com"
#     username = os.getenv("METEOMATICS_USERNAME")
#     password = os.getenv("METEOMATICS_PASSWORD")
    
#     # Get the current date and time
#     now = datetime.utcnow()
    
#     # Define the parameters for the API request
#     parameters = "t_2m:C,weather_symbol_1h:idx,t_min_2m_24h:C,t_max_2m_24h:C,precip_type_5min:idx"
    
#     # Define the time range for the next 3 days
#     time_range = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')},{(now + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')},{(now + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')},{(now + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')}"
    
#     # Define the URL for the API request
#     url = f"{base_url}/{time_range}/{parameters}/{latitude},{longitude}/json"
    
#     try:
#         # Make the API request
#         response = requests.get(url, auth=(username, password))
        
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return None
#     except requests.exceptions.RequestException:
#         return None

# # def display_weather_info(city):
# #     coordinates = get_city_coordinates(city)
# #     if coordinates:
# #         latitude, longitude = coordinates
# #         weather_data = get_weather_data(latitude, longitude)
# #         if weather_data:
# #             st.subheader(f"Weather Forecast for {city}")
            
# #             # Current temperature
# #             current_temp = weather_data['data'][0]['coordinates'][0]['dates'][0]['value']
# #             st.write(f"Current Temperature: {current_temp}°C")
# #             weather_emojis = {1: "☀️", 2: "⛅", 3: "☁️", 4: "🌧️", 5: "❄️"}
# #             # Weather forecast for the next 3 days
# #             forecast_data = [
# #                 {"date": weather_data['data'][0]['coordinates'][0]['dates'][1]['date'], "min_temp": weather_data['data'][2]['coordinates'][0]['dates'][1]['value'], "max_temp": weather_data['data'][3]['coordinates'][0]['dates'][1]['value'], "emoji": weather_emojis.get(weather_data['data'][1]['coordinates'][0]['dates'][1]['value'], "")},
# #                 {"date": weather_data['data'][0]['coordinates'][0]['dates'][2]['date'], "min_temp": weather_data['data'][2]['coordinates'][0]['dates'][2]['value'], "max_temp": weather_data['data'][3]['coordinates'][0]['dates'][2]['value'], "emoji": weather_emojis.get(weather_data['data'][1]['coordinates'][0]['dates'][2]['value'], "")},
# #                 {"date": weather_data['data'][0]['coordinates'][0]['dates'][3]['date'], "min_temp": weather_data['data'][2]['coordinates'][0]['dates'][3]['value'], "max_temp": weather_data['data'][3]['coordinates'][0]['dates'][3]['value'], "emoji": weather_emojis.get(weather_data['data'][1]['coordinates'][0]['dates'][3]['value'], "")}
# #             ]
            
# #             # Display weather forecast
# #             for day in forecast_data:
# #                 date = datetime.strptime(day['date'], "%Y-%m-%dT%H:%M:%SZ").strftime("%a, %b %d")
# #                 st.write(f"{day['emoji']} {date}: {day['min_temp']}°C - {day['max_temp']}°C")
# #         else:
# #             st.warning("Failed to retrieve weather data.")
# #     else:
# #         st.warning("Failed to retrieve city coordinates.")

# # Define the weather emojis dictionary
# weather_emojis = {
#     1: "☀️",  # Clear sky
#     2: "⛅",  # Partly cloudy
#     3: "☁️",  # Cloudy
#     4: "🌧️",  # Rain
#     5: "🌨️",  # Rain and snow mixed
#     6: "❄️",  # Snow
#     7: "🌨️",  # Sleet
#     8: "🌧️❄️",  # Freezing rain
#     9: "🌨️"   # Hail
# }

# def display_weather_info(city):
#     coordinates = get_city_coordinates(city)
#     if coordinates:
#         latitude, longitude = coordinates
#         weather_data = get_weather_data(latitude, longitude)
#         if weather_data:
#             st.subheader(f"Weather Forecast for {city}")

#             # Current temperature and precipitation type
#             current_temp = weather_data['data'][0]['coordinates'][0]['dates'][0]['value'] if weather_data['data'] and weather_data['data'][0]['coordinates'] else "N/A"
#             current_precip_type = weather_data['data'][4]['coordinates'][0]['dates'][0]['value'] if weather_data['data'] and weather_data['data'][4]['coordinates'] else 0
#             current_emoji = weather_emojis.get(current_precip_type, "")
#             st.write(f"Current Temperature: {current_temp}°C {current_emoji}")

#             # Weather forecast for the next 3 days
#             forecast_data = []
#             for i in range(1, 4):
#                 if weather_data['data'] and weather_data['data'][0]['coordinates'] and len(weather_data['data'][0]['coordinates'][0]['dates']) > i:
#                     date = weather_data['data'][0]['coordinates'][0]['dates'][i]['date']
#                     min_temp = weather_data['data'][2]['coordinates'][0]['dates'][i]['value'] if weather_data['data'] and weather_data['data'][2]['coordinates'] else "N/A"
#                     max_temp = weather_data['data'][3]['coordinates'][0]['dates'][i]['value'] if weather_data['data'] and weather_data['data'][3]['coordinates'] else "N/A"
#                     precip_type = weather_data['data'][4]['coordinates'][0]['dates'][i]['value'] if weather_data['data'] and weather_data['data'][4]['coordinates'] else 0
#                     emoji = weather_emojis.get(precip_type, "")
#                     forecast_data.append({"date": date, "min_temp": min_temp, "max_temp": max_temp, "emoji": emoji})

#             # Display weather forecast
#             for day in forecast_data:
#                 date = datetime.strptime(day['date'], "%Y-%m-%dT%H:%M:%SZ").strftime("%a, %b %d")
#                 st.write(f"{day['emoji']} {date}: {day['min_temp']}°C - {day['max_temp']}°C")
#         else:
#             st.warning("Failed to retrieve weather data.")
#     else:
#         st.warning("Failed to retrieve city coordinates.")

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
#     Include a paragraph yet brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
#     Format the response as follows:
#     Trail 1:
#     Name: [Trail Name]
#     Description: [Trail Description]
#     Difficulty: [Trail Difficulty]
#     Length: [Trail Length]
#     Elevation Gain: [Elevation Gain]
#     Pet-Friendly: [pet_friendly]
#     Notable Features: [Notable Features]
#     AllTrails Link: [AllTrails Link]

#     Trail 2:
#     Name: [Trail Name]
#     Description: [Trail Description]
#     Difficulty: [Trail Difficulty]
#     Length: [Trail Length]
#     Elevation Gain: [Elevation Gain]
#     Pet-Friendly: [pet_friendly]
#     Notable Features: [Notable Features]
#     AllTrails Link: [AllTrails Link]

#     ...

#     Trail 5:
#     Name: [Trail Name]
#     Description: [Trail Description]
#     Difficulty: [Trail Difficulty]
#     Length: [Trail Length]
#     Elevation Gain: [Elevation Gain]
#     Pet-Friendly: [pet_friendly]
#     Notable Features: [Notable Features]
#     AllTrails Link: [AllTrails Link]

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

# # def generate_recommendations(city, difficulty, length, elevation, season, pet_friendly, user_preferences):
# #     prompt = f"""
# #     You are an expert in recommending hiking trails based on the city and user preferences.
# #     Provide the top 5 hiking trails for the given city that match the user's specific needs.
# #     Include a brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
# #     City: {city}
# #     Difficulty Level: {difficulty}
# #     Trail Length: {length} miles
# #     Elevation Gain: {elevation} feet
# #     Season: {season}
# #     Pet-Friendly: {pet_friendly}
# #     User Preferences: {user_preferences}
# #     Format the recommendations as a list of dictionaries, with each dictionary containing the following keys: "name", "description", "difficulty", "length", "elevation", "features", "alltrails_link".
# #     """
# #     response = model.generate_content(prompt)
# #     return eval(response.text)

# def generate_popular_trails(city):
#     prompt = f"""
#     Provide the top 5 most popular and beautiful hiking trails in {city}, regardless of any specific filters.
#     Include a paragraph yet brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, notable features, and the AllTrails link.
#     Format the response as follows:
#     Trail 1:
#     Name: [Trail Name]
#     Description: [Trail Description]
#     Difficulty: [Trail Difficulty]
#     Length: [Trail Length]
#     Elevation Gain: [Elevation Gain]
#     Notable Features: [Notable Features]
#     AllTrails Link: [AllTrails Link]

#     Trail 2:
#     Name: [Trail Name]
#     Description: [Trail Description]
#     Difficulty: [Trail Difficulty]
#     Length: [Trail Length]
#     Elevation Gain: [Elevation Gain]
#     Notable Features: [Notable Features]
#     AllTrails Link:
#     ...

#     Trail 5:
#     Name: [Trail Name]
#     Description: [Trail Description]
#     Difficulty: [Trail Difficulty]
#     Length: [Trail Length]
#     Elevation Gain: [Elevation Gain]
#     Notable Features: [Notable Features]
#     AllTrails Link: [AllTrails Link]
#     """
#     response = model.generate_content(prompt)
#     return response.text

# # def generate_popular_trails(city):
# #     prompt = f"""
# #     Provide the top 5 most popular and beautiful hiking trails in {city}, regardless of any specific filters.
# #     Include a brief description of each trail with relevant emojis, its difficulty level, length, elevation gain, and notable features.
# #     """
# #     response = model.generate_content(prompt)
# #     return response.text

# # Home Page
# def home():
#     st.title("Hiking Trail Recommendations")
    
#     # City signature picture
#     st.image("Garibaldi-Provincial-Park-Panorama-Ridge-Overnight-Backpacking-Trip-Sunset-BANNER-1.jpg", use_column_width=True)
    
#     st.write("Enter a city to get personalized hiking trail recommendations.")
#     city = st.text_input("Enter the city")
#     if city:
#         st.session_state.city = city
#         st.rerun()

# # # Display Popular Trails
# # def display_popular_trails(city):
# #     st.header(f"Top 5 Popular Trails in {city}")
# #     popular_trails = generate_popular_trails(city)
    
# #     for trail in popular_trails:
# #         with st.expander(trail['name']):
# #             st.write(trail['description'])
# #             st.write(f"Difficulty: {trail['difficulty']}")
# #             st.write(f"Length: {trail['length']} miles")
# #             st.write(f"Elevation Gain: {trail['elevation']} feet")
# #             st.write(f"Notable Features: {trail['features']}")
# #             st.write(f"AllTrails Link: {trail['alltrails_link']}")
    
# #     if st.button("Dismiss and Proceed to Search"):
# #         st.session_state.show_search_filters = True
# #         st.rerun()

# # # Display Popular Trails
# # def display_popular_trails(city):
# #     st.header(f"Top 5 Popular Trails in {city}")
# #     popular_trails = generate_popular_trails(city)
# #     st.write(popular_trails)
    
# #     if st.button("Dismiss and Proceed to Search"):
# #         st.session_state.show_search_filters = True
# #         st.rerun()

# def display_popular_trails(city):
#     st.header(f"Top 5 Popular Trails in {city}")
#     popular_trails = generate_popular_trails(city)
    
#     trails = popular_trails.split("\n\n")
#     for trail in trails:
#         if trail.strip():
#             trail_info = trail.split("\n")
#             for info in trail_info:
#                 if info.startswith("Name:"):
#                     st.subheader(info.split(": ")[1])
#                 elif info.startswith("AllTrails Link:"):
#                     st.write(f"[AllTrails Link]({info.split(': ')[1]})")
#                 else:
#                     st.write(info)
#             st.write("---")
    
#     if st.button("Dismiss and Proceed to Search"):
#         st.session_state.show_search_filters = True
#         st.rerun()

# def display_search_filters(city):
#     st.header(f"Search Hiking Trails in {city}")
    
#     # Weather Forecast
#     display_weather_info(city)
    
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
        
#         trails = recommendations.split("\n\n")
#         for trail in trails:
#             if trail.strip():
#                 trail_info = trail.split("\n")
#                 for info in trail_info:
#                     if info.startswith("Name:"):
#                         st.subheader(info.split(": ")[1])
#                     elif info.startswith("AllTrails Link:"):
#                         st.write(f"[AllTrails Link]({info.split(': ')[1]})")
#                     else:
#                         st.write(info)
#                 st.write("---")
    
#     # Back to city selection button
#     if st.button("Back to City Selection"):
#         st.session_state.pop("city", None)
#         st.session_state.pop("show_search_filters", None)
#         st.rerun()

# # # Display Search Filters and Recommendations
# # def display_search_filters(city):
# #     st.header(f"Search Hiking Trails in {city}")
    
# #     # Weather Forecast
# #     display_weather_info(city)
    
# #     # Filter options
# #     difficulty = st.selectbox("Difficulty Level", ["Easy", "Moderate", "Difficult"])
# #     length = st.slider("Trail Length (miles)", min_value=0.0, max_value=10.0, step=0.5)
# #     elevation = st.slider("Elevation Gain (feet)", min_value=0, max_value=1000, step=100)
# #     season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
# #     pet_friendly = st.checkbox("Pet-Friendly")
    
# #     # Optional user preferences
# #     user_preferences = st.text_area("Specific Needs (optional)", "")
    
# #     # Generate recommendations button
# #     if st.button("Get Recommendations"):
# #         summary = generate_summary(city, difficulty, length, elevation, season, pet_friendly, user_preferences)
# #         st.subheader("Summary of Your Preferences")
# #         st.write(summary)
        
# #         recommendations = generate_recommendations(city, difficulty, length, elevation, season, pet_friendly, user_preferences)
# #         st.subheader("Recommended Hiking Trails")
        
# #         for trail in recommendations:
# #             with st.expander(trail['name']):
# #                 st.write(trail['description'])
# #                 st.write(f"Difficulty: {trail['difficulty']}")
# #                 st.write(f"Length: {trail['length']} miles")
# #                 st.write(f"Elevation Gain: {trail['elevation']} feet")
# #                 st.write(f"Notable Features: {trail['features']}")
# #                 st.write(f"AllTrails Link: {trail['alltrails_link']}")
    
# #     # Back to city selection button
# #     if st.button("Back to City Selection"):
# #         st.session_state.pop("city", None)
# #         st.session_state.pop("show_search_filters", None)
# #         st.rerun()

# # Search Page
# def search():
#     city = st.session_state.city
    
#     if "show_search_filters" not in st.session_state:
#         display_popular_trails(city)
#     else:
#         display_search_filters(city)

# # Main App
# def main():
#     if "city" not in st.session_state:
#         home()
#     else:
#         search()

# if __name__ == "__main__":
#     main()



# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# import streamlit as st
# import requests
# from datetime import datetime, timedelta
# from geopy.geocoders import Nominatim

# # Load environment variables
# load_dotenv()

# # Configure the GenAI API
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel('gemini-pro')

# def get_city_coordinates(city):
#     geolocator = Nominatim(user_agent="hiking_trail_app")
#     location = geolocator.geocode(city, timeout=5)
#     if location:
#         return location.latitude, location.longitude
#     else:
#         return None

# def get_weather_data(latitude, longitude):
#     base_url = "https://api.meteomatics.com"
#     username = os.getenv("METEOMATICS_USERNAME")
#     password = os.getenv("METEOMATICS_PASSWORD")
    
#     # Get the current date and time
#     now = datetime.utcnow()
    
#     # Define the parameters for the API request
#     parameters = "t_2m:C"
    
#     # Define the URL for the API request
#     url = f"{base_url}/{now.strftime('%Y-%m-%dT%H:%M:%SZ')}/{parameters}/{latitude},{longitude}/json"
    
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
#     coordinates = get_city_coordinates(city)
#     if coordinates:
#         latitude, longitude = coordinates
#         weather_data = get_weather_data(latitude, longitude)
#         if weather_data:
#             st.subheader(f"Weather Forecast for {city}")
#             temperature = weather_data['data'][0]['coordinates'][0]['dates'][0]['value']
#             st.write(f"Temperature: {temperature}°C")
#         else:
#             st.warning("Failed to retrieve weather data.")
#     else:
#         st.warning("Failed to retrieve city coordinates.")

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
#     st.image("Garibaldi-Provincial-Park-Panorama-Ridge-Overnight-Backpacking-Trip-Sunset-BANNER-1.jpg", use_column_width=True)
    
#     st.write("Enter a city to get personalized hiking trail recommendations.")
#     city = st.text_input("Enter the city")
#     if city:
#         st.session_state.city = city
#         st.rerun()

# # Display Popular Trails
# def display_popular_trails(city):
#     st.header(f"Top 5 Popular Trails in {city}")
#     popular_trails = generate_popular_trails(city)
#     st.write(popular_trails)
    
#     if st.button("Dismiss and Proceed to Search"):
#         st.session_state.show_search_filters = True
#         st.rerun()

# # Display Search Filters and Recommendations
# def display_search_filters(city):
#     st.header(f"Search Hiking Trails in {city}")
    
#     # Weather Forecast
#     display_weather_info(city)
    
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
#         st.session_state.pop("show_search_filters", None)
#         st.rerun()

# # Search Page
# def search():
#     city = st.session_state.city
    
#     if "show_search_filters" not in st.session_state:
#         display_popular_trails(city)
#     else:
#         display_search_filters(city)

# # Main App
# def main():
#     if "city" not in st.session_state:
#         home()
#     else:
#         search()

# if __name__ == "__main__":
#     main()



