import streamlit as st
import pandas as pd
import numpy as np
import pickle
import pymongo
import hashlib
import os
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from PIL import Image

#This line is for page configuration
st.set_page_config(page_title="AI-Based Medicine System", layout="wide")

#This portion is to Setup our Database i.e MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["medicine_db"]
users_col = db["users"]
history_col = db["history"]

#This portion is for Password Functions and Authentication.
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if users_col.find_one({"username": username}):
        return False
    users_col.insert_one({
        "username": username,
        "password": hash_password(password)
    })
    return True

def login_user(username, password):
    user = users_col.find_one({"username": username})
    if user and user["password"] == hash_password(password):
        return True
    return False

#This all is for Load model and Data .
model = pickle.load(open("model.pkl", "rb"))
#All this .csv files are available in the Kaggle
symptoms_df = pd.read_csv("data/symtoms_df.csv")
precautions_df = pd.read_csv("data/precautions_df.csv")
workout_df = pd.read_csv("data/workout_df.csv")
description_df = pd.read_csv("data/description.csv")
medications_df = pd.read_csv("data/medications.csv")
diets_df = pd.read_csv("data/diets.csv")

df = pd.read_csv("data/Training.csv").drop_duplicates()
disease_list = sorted(df["prognosis"].unique())
symptoms_list = list(df.columns[:-1])

le = LabelEncoder()
le.fit(df["prognosis"])
disease_dict = dict(zip(le.transform(le.classes_), le.classes_))
symptoms_dict = {symptom: idx for idx, symptom in enumerate(symptoms_list)}
#Disease_dict helps convert back the number to actual disease name.
#Symptoms_dict maps each symptom to its index.


#This is the actual Prediction function of the code
def predict_disease(symptoms):
    input_data = np.zeros(len(symptoms_dict))
    for s in symptoms:
        if s in symptoms_dict:
            input_data[symptoms_dict[s]] = 1
    prediction = model.predict([input_data])[0]
    return disease_dict[prediction]

def get_info(disease):
    info = {}
    try:
        info["Description"] = description_df[description_df["Disease"] == disease]["Description"].values[0]
    except:
        info["Description"] = "No description available."

    try:
        info["Precautions"] = precautions_df[precautions_df["Disease"] == disease].values[0][2:]
    except:
        info["Precautions"] = []

    try:
        info["Symptoms"] = symptoms_df[symptoms_df["Disease"] == disease].values[0][2:]
    except:
        info["Symptoms"] = []

    try:
        info["Medications"] = medications_df[medications_df["Disease"] == disease]["Medication"].values[0]
    except:
        info["Medications"] = "[]"

    try:
        info["Diet"] = diets_df[diets_df["Disease"] == disease]["Diet"].values[0]
    except:
        info["Diet"] = "[]"

    try:
        info["Workout"] = workout_df[workout_df["disease"] == disease]["workout"].tolist()
    except:
        info["Workout"] = []

    return info

#This portion shows the UserInterface of the Application

st.sidebar.title("🔐 User Panel")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
#This portion is for login and registration selection buttom
menu = ["Login", "Register"]
if not st.session_state.logged_in:
    choice = st.sidebar.radio("Select Option", menu)

    if choice == "Register":
        st.sidebar.subheader("Create Account")
        new_user = st.sidebar.text_input("New Username")
        new_pass = st.sidebar.text_input("New Password", type='password')
        if st.sidebar.button("Register"):
            if register_user(new_user, new_pass):
                st.sidebar.success("✅ Registered! Go to login.")
            else:
                st.sidebar.warning("⚠️ Username already exists.")

    if choice == "Login":
        st.sidebar.subheader("Login")
        user = st.sidebar.text_input("Username")
        passwd = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            if login_user(user, passwd):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid credentials.")

else:
    st.sidebar.success(f"👤 Logged in as {st.session_state.username}")
    menu = ["Home", "History"]
    choice = st.sidebar.radio("Navigation", menu)
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
if choice == "Home": #This is for Home Page(after login if user want homepage then this shows)
    #Main Page For User
    if st.session_state.logged_in:

        if os.path.exists("banner.png"):
            banner = Image.open("banner.png")
            st.image(banner, width=700)
        else:
            st.warning("Banner image not found. Showing title instead.")
            st.title("🧠 AI-Based Medicine Recommendation System")


        st.title("🧠 AI-Based Medicine Recommendation System")
        st.markdown("Select symptoms and get disease prediction with advice.")

        selected_symptoms = st.multiselect("📝 Select Your Symptoms:", symptoms_list)

        if st.button("🔍 Predict Disease"):
            if selected_symptoms:
                predicted_disease = predict_disease(selected_symptoms)
                st.success(f"🩺 **Predicted Disease**: {predicted_disease}")

                info = get_info(predicted_disease)

                st.subheader("📖 Description")
                st.write(info["Description"])

                st.subheader("💊 Medications")
                st.write(", ".join(eval(info["Medications"])))

                st.subheader("🥗 Diet")
                st.write(", ".join(eval(info["Diet"])))

                st.subheader("🏃 Workouts")
                for w in info["Workout"]:
                    st.markdown(f"- {w}")

                st.subheader("🛡️ Precautions")
                for p in info["Precautions"]:
                    st.markdown(f"- {p}")

                # Hospital link shown only after login & prediction
                st.markdown("---")
                st.markdown("### 🏥 Nearby Hospital Suggestion")
                hospital_link = "https://www.google.com/maps/search/hospitals+near+me"
                st.markdown(f"[📍 Find Nearby Hospitals]({hospital_link})", unsafe_allow_html=True)
                # Save prediction in DB
                history_col.insert_one({
                    "username": st.session_state.username,
                    "symptoms": selected_symptoms,
                    "prediction": predicted_disease,
                    "timestamp": datetime.utcnow()
                })
                # Check count of repeated disease
            count = history_col.count_documents({
                "username": st.session_state.username,
                "prediction": predicted_disease
            })

            if count >= 3:
                st.warning("⚠️ You've had this prediction 3 or more times. Please consider visiting a doctor.")
                st.markdown("[🔍 Find nearby hospitals](https://www.google.com/maps/search/nearby+hospitals)") 
        else:
            st.warning("❗ Please select at least one symptom.")

elif choice == "History":
        st.title("🕓 Your Search History")
        history = history_col.find({"username": st.session_state.username}).sort("timestamp", -1)
#This format will be seen in the History json format
        for entry in history:
            st.markdown(f"""
            ---
            **🧍 Username:** `{entry.get('username', 'N/A')}`  
            **💊 Symptoms:** `{", ".join(entry.get('symptoms', []))}`  
            **🩺 Predicted Disease:** `{entry.get('prediction', 'N/A')}`  
            **🕒 Timestamp:** `{entry.get('timestamp', 'N/A')}`
            """)




