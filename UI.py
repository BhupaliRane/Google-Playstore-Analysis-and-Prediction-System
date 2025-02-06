import streamlit as st
import pickle
import numpy as np
import mysql.connector
import pandas as pd

st.set_page_config(page_title="Google Playstore Prediction", page_icon="📱", layout="centered")

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
    with open("rating_model.pkl", "rb") as f:
        rating_model = pickle.load(f)

    with open("rating_model.pkl", "rb") as f:
        installs_model = pickle.load(f)
    
    return rating_model, installs_model

rating_model, installs_model = load_models()

if "page" not in st.session_state:
    st.session_state["page"] = "Home"

if st.session_state["page"] == "Home":
    st.title("Welcome to Google Playstore Prediction Application")
    st.write("Choose an option below to proceed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Predict Rating ⭐"):
            st.session_state["page"] = "Rating Prediction"
    with col2:
        if st.button("Predict Installs 📥"):
            st.session_state["page"] = "Installs Prediction"

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

    # **Replace missing columns with mean values**
    installs_mean = mean_values.get("Installs", 0)
    free_mean = mean_values.get("Free", 0)
    rating_count_mean = mean_values.get("Rating_Count", 0)
    editors_choice_mean = mean_values.get("Editors_Choice", 0)


    col1, col2, col3 = st.columns([1, 2, 1])  
    with col1:
        if st.button("Predict Rating"):
            
            try:
                input_features = np.array([[category_encoded, size_in_mb, in_app_purchases, ad_supported, content_rating_encoded, 
                                installs_mean, free_mean, rating_count_mean, editors_choice_mean]])
                prediction = rating_model.predict(input_features)[0]
                st.success(f"Predicted Rating: {int(prediction):.2f}")

                category_encoded = int(category_encoded)  
                size_in_mb = float(size_in_mb) 
                in_app_purchases = int(in_app_purchases)  
                ad_supported = int(ad_supported)  
                content_rating_encoded = int(content_rating_encoded)  
                prediction = int(prediction)



                # Store in database
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="GooglePlayStore")
                cursor = conn.cursor()
                
                query = """
                INSERT INTO user_ratings_data (category, size_in_mb, content_rating, ad_supported, in_app_purchases, transformed_rating)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (category_encoded, size_in_mb, content_rating_encoded, ad_supported, in_app_purchases, prediction)
                
                cursor.execute(query, values)
                conn.commit()
                conn.close()
                st.success("Data inserted successfully!")

            except Exception as e:
                st.error(f"Error during prediction: {e}")

    with col3:
        if st.button("Back to Home"):
            st.session_state["page"] = "Home"

elif st.session_state["page"] == "Installs Prediction":
    st.title("Installs Prediction Model")

    # User Inputs
    feature_1 = st.number_input("Feature A", min_value=0.0, max_value=10.0, value=5.0)
    feature_2 = st.number_input("Feature B", min_value=0.0, max_value=10.0, value=5.0)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("Predict Installs"):
            input_data = np.array([[feature_1, feature_2]])
            prediction = installs_model.predict(input_data)[0]
            st.success(f"Predicted Installs: {int(prediction)}")

            # Store in SQL
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="root", database="GooglePlayStore")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO user_installs_data (feature1, feature2) VALUES (%s, %s)",
                    (feature_1, feature_2)  # Fix: Use correct variable names
                )
                conn.commit()
                conn.close()
                st.success("Data inserted successfully!")
            except Exception as e:
                st.error(f"Error inserting data: {e}")

    with col3:
        if st.button("Back to Home"):
            st.session_state["page"] = "Home"
