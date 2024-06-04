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
    Include a brief description of each trail, its difficulty level, and any notable features.
    City: {city}
    """
    response = model.generate_content(prompt)
    return response.text

def filter_trails(trails, difficulty, length, elevation):
    # Implement your trail filtering logic based on the selected filters
    filtered_trails = trails  # Replace with your actual filtering code
    return filtered_trails

# Home Page
def home():
    st.title("Hiking Trail Recommendations")
    st.write("Enter a city to get personalized hiking trail recommendations.")
    city = st.text_input("Enter the city")
    if st.button("Get Recommendations"):
        st.session_state.city = city
        st.experimental_set_query_params(page="recommendations")

# Recommendations Page
def recommendations():
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
        # Implement your trail filtering logic based on the selected filters
        filtered_trails = filter_trails(trails, difficulty, length, elevation)
        st.write(filtered_trails)
    
    if st.button("Back to Home"):
        st.experimental_set_query_params(page="home")

# Main App
def main():
    page = st.experimental_get_query_params().get("page", ["home"])[0]
    
    if page == "home":
        home()
    elif page == "recommendations":
        recommendations()

if __name__ == "__main__":
    main()
