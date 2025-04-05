import streamlit as st
import pickle
import numpy as np
import mysql.connector
import pandas as pd
import base64
import time
import os


# Set theme and layout
st.set_page_config(
    page_title="Google Playstore Prediction",
    page_icon="📱",
    layout="wide"
)

# Function to encode local image to Base64
def get_base64_image(image_path):
    print("Looking for image at:", image_path)
    print("Current working directory:", os.getcwd())
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded
image_path = os.path.join("Images", "bg.jpg")
background_image = get_base64_image(image_path)

# Adjust container width dynamically
page = st.session_state.get("page", "Home")
if page == "View Dashboard":
    st.markdown("""
    <style>
        .block-container {
            max-width: 1600px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Load CSS for modern styling and animations
st.markdown(
    f"""
    <style>
        .stApp {{
            background-image: url('{background_image}');
            background-size: cover;
            color: #fff;
            font-family: 'Poppins', sans-serif;
        }}
        .stTitle {{
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            color: #fff !important;
            margin-bottom: 20px;
        }}
        .block-container {{
            max-width: 900px;
            margin: auto;
            padding: 2rem 2rem 4rem 2rem;
            background-color: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.3);
            text-align: center;
            color: #fff !important;
            backdrop-filter: blur(50px);
        }}
        .stButton > button {{
            width: 80%;
            background-color: #578FCA;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }}
        .stButton > button:hover {{
            background-color: #2980b9;
            transform: scale(1.1);
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
            color: white !important;
            border-color: white !important;
        }}
        .popup {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.8);
            background: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.4);
            text-align: center;
            color: #333;
            animation: popup-appear 0.5s ease-in-out forwards;
        }}
        @keyframes popup-appear {{
            from {{ transform: translate(-50%, -50%) scale(0.8); opacity: 0; }}
            to {{ transform: translate(-50%, -50%) scale(1); opacity: 1; }}
        }}
        .star {{
            display: inline-block;
            font-size: 40px;
            color: #FFD700;
            opacity: 0;
            transform: scale(0.5);
            animation: star-pop 0.5s forwards;
        }}
        @keyframes star-pop {{
            0% {{ opacity: 0; transform: scale(0.5) rotateY(0deg); }}
            50% {{ opacity: 0.7; transform: scale(1.2) rotateY(180deg); }}
            100% {{ opacity: 1; transform: scale(1) rotateY(360deg); }}
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Load encoding mappings
with open("Category_label_encoded.pkl", "rb") as f:
    category_encoding = pickle.load(f)

with open("Content Rating_label_encoded.pkl", "rb") as f:
    content_rating_encoding = pickle.load(f)

# Load mean values for missing columns
with open("mean_values.pkl", "rb") as f:
    mean_values = pickle.load(f)  # Dictionary containing mean values of Installs, Free, Rating_Count, Editors_Choice

# Function to encode user input using Label Encoding mapping
def encode_category(value, encoding_map):
    return encoding_map.get(value, round(np.mean(list(encoding_map.values())), 1))

# Function to load and display the Tableau Dashboard with increased width
def show_tableau_dashboard():
    tableau_html = """
    <div class='tableauContainer' style='width: 100%; margin: auto, padding:20px;'>
        <div class='tableauPlaceholder' id='viz1739257421829' style='position: relative; width: 80%; height: 40vh;'>
            <noscript>
                <a href='#'><img alt=' ' src='https://public.tableau.com/static/images/DB/DBDAProject_17392469401620/Dashboard1/1_rss.png' style='border: none; width: 100%;' /></a>
            </noscript>
            <object class='tableauViz' style='display:none; width: 100%; height: 90vh;'>
                <param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' />
                <param name='embed_code_version' value='3' />
                <param name='site_root' value='' />
                <param name='name' value='DBDAProject_17392469401620/Dashboard1' />
                <param name='tabs' value='yes' />
                <param name='toolbar' value='yes' />
                <param name='static_image' value='https://public.tableau.com/static/images/DB/DBDAProject_17392469401620/Dashboard1/1.png' />
                <param name='animate_transition' value='yes' />
                <param name='display_static_image' value='yes' />
                <param name='display_spinner' value='yes' />
                <param name='display_overlay' value='yes' />
                <param name='display_count' value='yes' />
                <param name='language' value='en-GB' />
            </object>
        </div>
    </div>
    <script type='text/javascript'>
        var divElement = document.getElementById('viz1739257421829');
        var vizElement = divElement.getElementsByTagName('object')[0];
        if (divElement.offsetWidth > 800) {
            vizElement.style.width = '100%';
            vizElement.style.height = (divElement.offsetWidth * 0.75) + 'px';
        } else if (divElement.offsetWidth > 500) {
            vizElement.style.width = '100%';
            vizElement.style.height = (divElement.offsetWidth * 0.75) + 'px';
        } else {
            vizElement.style.width = '100%';
            vizElement.style.minHeight = '1750px';
            vizElement.style.maxHeight = (divElement.offsetWidth * 1.77) + 'px';
        }
        var scriptElement = document.createElement('script');
        scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
        vizElement.parentNode.insertBefore(scriptElement, vizElement);
    </script>
    """
    st.components.v1.html(tableau_html, height=900)
    
@st.cache_resource
def load_models():
    with open("finetuning.pkl", "rb") as f:
        rating_model = pickle.load(f)
    return rating_model

rating_model = load_models()


if "page" not in st.session_state:
    st.session_state["page"] = "Home"

if st.session_state["page"] == "Home":
    st.markdown("""
        <div style=" display: flex; justify-content: center; align-items: center; height: 40vh; text-align: center;">
            <div>
                <h1>Welcome to Google Playstore Prediction Application</h1>
                <p>Choose an option below to proceed</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("Predict Rating ⭐"):
            st.session_state["page"] = "Rating Prediction"
    with col3:
        if st.button("View Dashboard 📊"):
            st.session_state["page"] = "View Dashboard"

elif st.session_state["page"] == "Rating Prediction":

    st.title("Rating Prediction Model")
    
    # User inputs
    category = st.selectbox("Select Your App Category", list(category_encoding.keys()))
    size_in_mb = st.number_input("Enter Size in MB", min_value=0.0, step=0.1)  
    in_app_purchases = st.radio("Is In-app purchase available in your app?", ["Yes", "No"], horizontal=True)  
    ad_supported = st.radio("Does your app includes ad?", ["Yes", "No"], horizontal=True)  
    content_rating = st.selectbox("Select Content Rating", list(content_rating_encoding.keys()))

    in_app_purchases = 1 if in_app_purchases == "Yes" else 0
    ad_supported = 1 if ad_supported == "Yes" else 0

    # Apply encoding to categorical features
    category_encoded = encode_category(category, category_encoding)
    content_rating_encoded = encode_category(content_rating, content_rating_encoding)
 
    if category in mean_values:
        category_stats = mean_values[category]
    else:
        category_stats = {
            "Installs": np.mean([d["Installs"] for d in mean_values.values()]),
            "Free": np.mean([d["Free"] for d in mean_values.values()]),
            "Rating Count": np.mean([d["Rating Count"] for d in mean_values.values()]),
            "Editors Choice": np.mean([d["Editors Choice"] for d in mean_values.values()]),
        }
    
    # Extract values safely
    installs_mean = category_stats["Installs"]
    free_median = category_stats["Free"]
    rating_count_median = category_stats["Rating Count"]
    editors_choice_median = category_stats["Editors Choice"]

    col1, col2, col3 = st.columns([1, 2, 1])  
    with col1:
        if st.button("Predict Rating"):
            try:
                with st.spinner("Predicting..."):
                    time.sleep(2)

                category_encoded = int(category_encoded)  
                size_in_mb = float(size_in_mb) 
                in_app_purchases = int(in_app_purchases)  
                ad_supported = int(ad_supported)  
                content_rating_encoded = int(content_rating_encoded)  
                input_features = np.array([[category_encoded, size_in_mb, in_app_purchases, ad_supported, content_rating_encoded, 
                                installs_mean, free_median, rating_count_median, editors_choice_median]])

                predicted_rating = round(float(rating_model.predict(input_features)[0]), 1)                

                # Animated Star Display
                star_count = min(5, max(1, round(predicted_rating)))
                stars_html = "".join([f"<span class='star' style='animation-delay:{i * 0.2}s;'>⭐</span>" for i in range(star_count)])

                st.markdown(f"""
                    <div class='popup'>
                        <div>{stars_html}</div>
                    </div>
                """, unsafe_allow_html=True)

                # Store in database
                conn = mysql.connector.connect(host="localhost", user="root", password="Root", database="GooglePlayStore")
                cursor = conn.cursor()
                
                query = """
                INSERT INTO user_ratings_data (category, size_in_mb, content_rating, ad_supported, in_app_purchases, transformed_rating, Installs, Free, Rating_count, Editors_Choice, Category_Encoded, Content_Rating_Encoded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (category, size_in_mb, content_rating, ad_supported, in_app_purchases, int(predicted_rating), installs_mean, free_median, rating_count_median, editors_choice_median, category_encoded, content_rating_encoded)
                
                cursor.execute(query, values)
                conn.commit()
                conn.close()

            except Exception as e:
                st.error(f"Error during prediction: {e}")

    with col3:
        if st.button("Back to Home"):
            st.session_state["page"] = "Home"

elif st.session_state["page"] == "View Dashboard":
    st.markdown("<style>#dashboard-container { max-width: 100%; }</style>", unsafe_allow_html=True)
    st.subheader("Interactive Tableau Dashboard")
    with st.spinner("Loading Dashboard..."):
        time.sleep(2)
    show_tableau_dashboard()
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  
    with col4:
        if st.button("Back to Home"):
            st.session_state["page"] = "Home"
