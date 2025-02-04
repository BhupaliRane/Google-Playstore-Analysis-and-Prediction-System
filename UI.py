import streamlit as st
import pickle
import numpy as np
import mysql.connector

st.set_page_config(page_title="Google Playstore Prediction", page_icon="📱", layout="centered")

with open("Category_kfold_encoded.pkl", "rb") as f:
    category_encoding = pickle.load(f)

with open("Content Rating_kfold_encoded.pkl", "rb") as f:
    content_rating_encoding = pickle.load(f)

# Function to encode user input using K-Fold Target Encoding mapping
def encode_category_kfold(value, encoding_map):
    return encoding_map.get(value, round(np.mean(list(encoding_map.values())), 1))


@st.cache_resource
def load_models():
    # Check if models can be loaded correctly
    with open("rating_model.pkl", "rb") as f:
        rating_model = pickle.load(f)
        print(f"Rating model type: {type(rating_model)}")

    with open("rating_model.pkl", "rb") as f:
        installs_model = pickle.load(f)
        print(f"Installs model type: {type(installs_model)}")
    
    print(hasattr(rating_model, 'predict'))  # Should return True
    print(hasattr(installs_model, 'predict')) 
    
    return rating_model, installs_model

rating_model, installs_model = load_models()

# Initialize session state
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
    category = st.text_input("Enter Category (String)")  
    size_in_mb = st.number_input("Enter Size in MB (Float)", min_value=0.0, step=0.1)  
    in_app_purchases = st.radio("In-App Purchase?", ["Yes", "No"], horizontal=True)  
    ad_supported = st.radio("Ad Support?", ["Yes", "No"], horizontal=True)  
    content_rating = st.selectbox("Select Content Rating", ["Everyone", "Everyone 10+", "Teen", "Mature 17+", "Adults only 18+"])

    in_app_purchases = 1 if in_app_purchases == "Yes" else 0
    ad_supported = 1 if ad_supported == "Yes" else 0

    # Apply K-Fold encoding & handle unseen values
    category_encoded = encode_category_kfold(category, category_encoding)
    content_rating_encoded = encode_category_kfold(content_rating, content_rating_encoding)

    col1, col2, col3 = st.columns([1, 2, 1])  
    with col1:
        if st.button("Predict Rating"):
            input_data = np.array([[category_encoded, size_in_mb, in_app_purchases, ad_supported, content_rating_encoded]])  # Fix: Use encoded values
            print(input_data)
            prediction = rating_model.predict(input_data)[0]
            st.success(f"Predicted Rating: {float(prediction):.2f}")

            category_encoded = float(category_encoded)  # Convert to float
            size_in_mb = float(size_in_mb)  # Convert to float
            in_app_purchases = int(in_app_purchases)  # Convert to int
            ad_supported = int(ad_supported)  # Convert to int
            content_rating_encoded = float(content_rating_encoded)  # Convert to float
            prediction = int(prediction) 

            try:
                # Connect to the MySQL database
                conn = mysql.connector.connect(host="localhost", user="root", password="Root", database="GooglePlayStore")
                if conn.is_connected():
                    print("Connection to the database is successful!")
                cursor = conn.cursor()

                # Insert data into the database
                query = """
                INSERT INTO user_ratings_data (category, size_in_mb, content_rating, ad_supported, in_app_purchases, transformed_rating)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (category_encoded, size_in_mb, content_rating_encoded, ad_supported, in_app_purchases, prediction)
                
                cursor.execute(query, values)
                conn.commit()  # Commit the changes to the database

                print("Data inserted successfully!")
            except mysql.connector.Error as e:
                print(f"Error inserting data: {e}")
            finally:
                if conn.is_connected():
                    conn.close()  # Close the connection to the database


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
                conn = mysql.connector.connect(host="localhost", user="root", password="Root", database="GooglePlayStore")
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
