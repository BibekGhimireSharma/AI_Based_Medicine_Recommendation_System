# 💊 AI-Based Medicine Recommendation System

An intelligent web application built using **Streamlit** and **MongoDB** that predicts possible diseases based on symptoms entered by the user. The system allows **user authentication**, **prediction history tracking**, and a **user-friendly interface** for personalized health insights.

-----

## 🚀 Features

- 🔐 User Registration & Login system  
- 🩺 Disease prediction using symptom input  
- 💾 History tracking for each logged-in user  
- 🧠 AI-based prediction logic (can be extended to ML models)  
- ☁️ MongoDB integration for storing user data & predictions  
- 📱 Responsive UI built with Streamlit  

---

## ⚙️ Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)  
- **Backend**: Python  
- **Database**: [MongoDB](https://www.mongodb.com/)  
- **Libraries**: `pymongo`, `pandas`, `sklearn`, `pickle`  

---

## 🛠️ Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/medicine-recommendation-system.git
cd medicine-recommendation-system

# 2. Install required packages
pip install -r requirements.txt

# 3. Start MongoDB server locally (Ensure it's running on localhost:27017)

# 4. Run the app
streamlit run app.py
