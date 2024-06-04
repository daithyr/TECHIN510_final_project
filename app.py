import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Configure the GenAI API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def generate_recommendations(city):
    prompt = f"""
    You are an expert in recommending hiking trails based on the city.
    Provide the top 5 hiking trails for the given city.
    Include a brief description of each trail, its difficulty level, length, elevation gain, and any notable features.
    City: {city}
    """
    response = model.generate_content(prompt)
    return response.text

def generate_filtered_recommendations(city, difficulty, length, elevation):
    prompt = f"""
    You are an expert in recommending hiking trails based on the city and specified filters.
    Provide the top 5 hiking trails for the given city that match the following criteria:
    - Difficulty Level: {difficulty}
    - Maximum Trail Length: {length} miles
    - Maximum Elevation Gain: {elevation} feet
    Include a brief description of each trail, its difficulty level, length, elevation gain, and any notable features.
    City: {city}
    """
    response = model.generate_content(prompt)
    return response.text

# Home Page
def home():
    st.title("Hiking Trail Recommendations")
    st.write("Enter a city to get personalized hiking trail recommendations.")
    city = st.text_input("Enter the city")
    if st.button("Get Recommendations"):
        st.session_state.city = city
        st.rerun()

# Recommendations Page
def recommendations():
    if "city" not in st.session_state:
        st.warning("Please enter a city on the Home Page first.")
        return
    
    city = st.session_state.city
    st.header(f"Hiking Trails in {city}")
    
    # LLM-powered Recommendations
    if st.button("Get Personalized Recommendations"):
        recommendations = generate_recommendations(city)
        st.write(recommendations)
    
    # Self-Searching with Filters
    st.subheader("Filter Trails")
    difficulty = st.selectbox("Difficulty Level", ["Easy", "Moderate", "Difficult"])
    length = st.slider("Trail Length (miles)", min_value=0.0, max_value=10.0, step=0.5)
    elevation = st.slider("Elevation Gain (feet)", min_value=0, max_value=1000, step=100)
    
    if st.button("Apply Filters"):
        filtered_recommendations = generate_filtered_recommendations(city, difficulty, length, elevation)
        st.write(filtered_recommendations)
    
    if st.button("Back to Home"):
        st.rerun()

# Main App
def main():
    page = st.sidebar.selectbox("Select a page", ["Home", "Recommendations"])
    
    if page == "Home":
        home()
    elif page == "Recommendations":
        recommendations()

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
#         st.experimental_set_query_params(page="recommendations")

# # Recommendations Page
# def recommendations():
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
#         st.experimental_set_query_params(page="home")

# # Main App
# def main():
#     page = st.experimental_get_query_params().get("page", ["home"])[0]
    
#     if page == "home":
#         home()
#     elif page == "recommendations":
#         recommendations()

# if __name__ == "__main__":
#     main()
