import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import folium

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
    
    # Filter options
    difficulty = st.selectbox("Difficulty Level", ["Easy", "Moderate", "Difficult"])
    length = st.slider("Trail Length (miles)", min_value=0.0, max_value=10.0, step=0.5)
    elevation = st.slider("Elevation Gain (feet)", min_value=0, max_value=1000, step=100)
    season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
    pet_friendly = st.checkbox("Pet-Friendly")
    
    if st.button("Apply Filters"):
        filtered_recommendations = generate_filtered_recommendations(city, difficulty, length, elevation, season, pet_friendly)
        st.write(filtered_recommendations)
        
        # Display overall traffic map of recommended trails
        map_center = ... # Retrieve the center coordinates of the recommended trails area
        m = folium.Map(location=map_center, zoom_start=10)
        folium.Marker(location=map_center, popup="Recommended Trails Area").add_to(m)
        st.components.v1.html(m._repr_html_(), height=500)
    
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
        
        # Display overall traffic map of recommended trails
        map_center = ... # Retrieve the center coordinates of the recommended trails area
        m = folium.Map(location=map_center, zoom_start=10)
        folium.Marker(location=map_center, popup="Recommended Trails Area").add_to(m)
        st.components.v1.html(m._repr_html_(), height=500)
    
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
