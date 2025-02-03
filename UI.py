import streamlit as st
import pickle
import numpy as np
import mysql.connector

st.set_page_config(page_title="Google Playstore Prediction", page_icon="📱", layout="centered")

# Load your models (Ensure you have 'rating_model.pkl' and 'installs_model.pkl' in the same directory)

@st.cache_resource
def load_models():
    with open("rating_model.pkl", "rb") as f:
        rating_model = pickle.load(f)
    with open("rating_model.pkl", "rb") as f:
        installs_model = pickle.load(f)
    return rating_model, installs_model

rating_model, installs_model = load_models()

# Initialize session state for navigation
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
    
    # Dummy input fields (Replace with actual feature inputs for rating prediction)
    category = st.text_input("Enter Category (String)")  # String input
    size_in_mb = st.number_input("Enter Size in MB (Float)", min_value=0.0, step=0.1)  # Float input
    in_app_purchase = st.radio("In-App Purchase?", ["Yes", "No"],horizontal=True)  # Yes/No as boolean
    ad_support = st.radio("Ad Support?", ["Yes", "No"], horizontal=True)  # Yes/No as boolean
    
    in_app_purchase = 1 if in_app_purchase == "Yes" else 0
    ad_support = 1 if ad_support == "Yes" else 0

    col1, col2, col3 = st.columns([1, 2, 1])  # Adjust width as needed
    with col1:
        if st.button("Predict Rating"):
            input_data = np.array([[category, size_in_mb, in_app_purchase, ad_support]])
            prediction = rating_model.predict(input_data)[0]
            st.success(f"Predicted Rating: {prediction:.2f}")

            conn = mysql.connector.connect(host="localhost", user="root", password="Root", database="GooglePlayStore")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_ratings_data (category, size_in_mb, in_app_purchase, ad_support) VALUES (%s, %f, %d, %d)",
                (category, size_in_mb, in_app_purchase, ad_support)
            )
            conn.commit()
            conn.close()
            st.success("Data inserted successfully!")

    with col3:
        if st.button("Back to Home"):
            st.session_state["page"] = "Home"
    
    
elif st.session_state["page"] == "Installs Prediction":
    st.title("Installs Prediction Model")
    
    # Dummy input fields (Replace with actual feature inputs for installs prediction)
    feature_1 = st.number_input("Feature A", min_value=0.0, max_value=10.0, value=5.0)
    feature_2 = st.number_input("Feature B", min_value=0.0, max_value=10.0, value=5.0)
    
    if st.button("Back to Home"):
        st.session_state["page"] = "Home"
        
    if st.button("Predict Installs"):
        input_data = np.array([[feature_1, feature_2]])
        prediction = installs_model.predict(input_data)[0]
        st.success(f"Predicted Installs: {int(prediction)}")

        conn = mysql.connector.connect(host="localhost", user="root", password="Root", database="GooglePlayStore")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_installs_data (feature1, feature2) VALUES (%s, %s)",
            (feature1, feature2)
        )
        conn.commit()
        conn.close()
        st.success("Data inserted successfully!")
