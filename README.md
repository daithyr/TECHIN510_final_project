# TECHIN510_final_project: Hiking Trail Recommendation App
Group member: Daithy Ren

Discover personalized hiking trail recommendations and weather forecasts to enhance your outdoor adventures.

## Impress Me
Harness the power of AI and real-time weather data to find the best hiking trails tailored to your preferences and ensure you're prepared for any weather conditions.

## Technologies Used
- **Python**: The core programming language used for developing the app.
- **Streamlit**: Used to create the interactive web application interface.
- **Google Generative AI**: Provides AI-based recommendations for hiking trails.
- **Meteomatics API**: Supplies real-time weather data for the hiking locations.
- **Geopy**: Utilized for geocoding to convert city names to geographical coordinates.
- **dotenv**: Manages environment variables securely.

## Problems I am Trying to Solve
- **Personalized Trail Recommendations**: Finding the perfect hiking trail that matches individual preferences, such as difficulty level, length, elevation gain, and pet-friendliness, can be challenging.
- **Accurate Weather Information**: Hikers need accurate and up-to-date weather information to plan their trips safely and enjoyably.
- **User-Friendly Experience**: Creating an intuitive and interactive interface that guides users seamlessly through the process of finding and preparing for a hike.

## How to Run
1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-repo/hiking-trail-recommendation-app.git
    cd hiking-trail-recommendation-app
    ```

2. **Install Required Packages**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables**
    - Create a `.env` file in the root directory.
    - Add your API keys for Google Generative AI and Meteomatics API:
      ```
      GEMINI_API_KEY=your_google_generative_ai_key
      METEOMATICS_USERNAME=your_meteomatics_username
      METEOMATICS_PASSWORD=your_meteomatics_password
      ```

4. **Run the Streamlit App**
    ```bash
    streamlit run app.py
    ```

5. **Open the App in Your Web Browser**
    - Navigate to `http://localhost:8501` to start using the app.

## Reflections

### What I Learned
- **API Integration**: Successfully integrated multiple APIs to fetch and display data seamlessly.
- **Error Handling**: Implemented robust error handling to provide meaningful feedback to users, especially for invalid city names.
- **User Interface Design**: Designed an intuitive interface using Streamlit to enhance user experience.
- **Real-time Data Display**: Managed real-time data fetching and display for weather forecasts, ensuring users have up-to-date information.

### Questions/Problems Faced
- **City Recognition Issues**: Ensuring the app accurately recognizes and validates city names. This involved prompting users to re-enter city names if they were not found or misspelled.
- **Weather Data Mapping**: Mapping weather data indices to appropriate emojis to provide clear and intuitive weather forecasts for users.
- **AllTrails Link Accuracy**: Ensuring the accuracy of external AllTrails links can be challenging. Users are advised to verify the links manually to ensure they lead to the correct trail information.
- **User Experience Challenges**: Balancing the amount of information displayed to users while keeping the interface simple and user-friendly. Ensuring the app remains functional and valuable even when some data points are unavailable.

Feel free to contribute or raise issues if you encounter any problems!

