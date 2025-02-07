import streamlit as st
import pickle
import numpy as np
import mysql.connector
import pandas as pd
import base64


# Set theme and layout
st.set_page_config(
    page_title="Google Playstore Prediction",
    page_icon="📱",
    layout="wide"
)

# Function to encode local image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_str = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{base64_str}"

# Load background image
background_image = get_base64_image(r"C:\Users\shree\Downloads\Playstore\background.png")

# Apply background image using CSS
st.markdown(
    f"""
    <style>
        .stApp {{
            background-image: url('{background_image}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #333;
            font-family: Arial, sans-serif;
        }}
        .block-container {{
            max-width: 800px;
            margin: auto;
            padding: 2rem;
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }}
        .stTitle {{
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            color: #2C3E50;
            margin-bottom: 20px;
        }}
        .stButton > button {{
            width: 100%;
            background-color: #3498db;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }}
        .stButton > button:hover {{
            background-color: #2980b9;
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
        <div style="display: flex; justify-content: center; align-items: center; height: 40vh; text-align: center;">
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
    category = st.selectbox("Select App Category", list(category_encoding.keys()))
    size_in_mb = st.number_input("Enter Size in MB", min_value=0.0, step=0.1)  
    in_app_purchases = st.radio("In-App Purchase?", ["Yes", "No"], horizontal=True)  
    ad_supported = st.radio("Ad Support?", ["Yes", "No"], horizontal=True)  
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
                input_features = np.array([[category_encoded, size_in_mb, in_app_purchases, ad_supported, content_rating_encoded, 
                                installs_mean, free_median, rating_count_median, editors_choice_median]])
                prediction = rating_model.predict(input_features)[0]
                st.success(f"Predicted Rating: {int(prediction):.2f}")
                # st.success(f"Predicted Rating: {'⭐' * round(prediction)} ({prediction:.2f})")
                
                # Store in database
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="GooglePlayStore")
                cursor = conn.cursor()
                
                query = """
                INSERT INTO user_ratings_data (category, size_in_mb, content_rating, ad_supported, in_app_purchases, transformed_rating)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (category_encoded, size_in_mb, content_rating_encoded, ad_supported, in_app_purchases, int(prediction))
                
                cursor.execute(query, values)
                conn.commit()
                conn.close()
                st.success("Data inserted successfully!")

            except Exception as e:
                st.error(f"Error during prediction: {e}")

    with col3:
        if st.button("Back to Home"):
            st.session_state["page"] = "Home"

elif st.session_state["page"] == "Tableau Dashboard":
    st.subheader("Interactive Tableau Dashboard")
    tableau_url = "https://public.tableau.com/views/Dashboard_17389506378000/Dashboard1?:language=en-GB&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link"
    st.markdown(f"""
        <iframe src="{tableau_url}" width="100%" height="600px" frameborder="0"></iframe>
    """, unsafe_allow_html=True)
