import streamlit as st
# import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import time
import warnings

# Suppress warnings for clean output
warnings.filterwarnings("ignore")

# Configure Streamlit page settings
st.set_page_config(page_title="Personal Fitness Tracker", page_icon="💪", layout="wide")

# Apply custom styling
st.markdown("""
    <style>
        .main {background-color: #e3f2fd;}
        .sidebar .sidebar-content {background-color: #90caf9;}
        h1, h2, h3 {color: #0d47a1;}
        .stButton>button {background-color: #1976d2; color: white;}
    </style>
""", unsafe_allow_html=True)

# Display main title
st.write("# 💪 Personal Fitness Tracker")
st.write("In this WebApp you will be able to observe your predicted calories burned in your body. Pass your parameters such as `Age`, `Gender`, `BMI`, etc., into this WebApp and then you will see the predicted value of kilocalories burned.")

# Sidebar for user input parameters
st.sidebar.header("User Input Parameters")

def user_input_features():
    """Collects user inputs via sliders and radio buttons"""
    age = st.sidebar.slider("Age", 15, 90, 25, step=1)
    bmi = st.sidebar.slider("BMI", 18, 45, 22, step=1)
    duration = st.sidebar.slider("Duration (min)", 5, 60, 20, step=1)
    heart_rate = st.sidebar.slider("Heart Rate", 50, 180, 90, step=1)
    body_temp = st.sidebar.slider("Body Temperature (°C)", 35, 42, 37, step=1)
    gender = 1 if st.sidebar.radio("Gender", ("Male", "Female")) == "Male" else 0
    return pd.DataFrame({"Age": [age], "BMI": [bmi], "Duration": [duration], "Heart_Rate": [heart_rate], "Body_Temp": [body_temp], "Gender_male": [gender]})

df = user_input_features()

# Display loading animation
bar = st.progress(0)
for i in range(100):
    bar.progress(i + 1)
    time.sleep(0.01)

# Load dataset
calories = pd.read_csv("calories.csv")
exercise = pd.read_csv("exercise.csv")

# Merge datasets and preprocess data
df_combined = exercise.merge(calories, on="User_ID").drop(columns="User_ID")
df_combined["BMI"] = round(df_combined["Weight"] / ((df_combined["Height"] / 100) ** 2), 2)
df_combined = df_combined[["Gender", "Age", "BMI", "Duration", "Heart_Rate", "Body_Temp", "Calories"]]
df_combined = pd.get_dummies(df_combined, drop_first=True)

# Train-test split
train_data, test_data = train_test_split(df_combined, test_size=0.2, random_state=1)
X_train, y_train = train_data.drop("Calories", axis=1), train_data["Calories"]

# Train the Random Forest model
random_reg = RandomForestRegressor(n_estimators=1000, max_features=3, max_depth=6)
random_reg.fit(X_train, y_train)

# Ensure input data aligns with training data
df = df.reindex(columns=X_train.columns, fill_value=0)

# Predict calorie burn
prediction = random_reg.predict(df)

# Create structured tabs for output
tabs = st.tabs(["Overview", "Prediction", "Similar Results", "Insights"])

with tabs[0]:
    # Display user inputs
    st.header("📊 Overview")
    st.write("Here are your input parameters:")
    st.write(df)

with tabs[1]:
    # Display predicted calorie burn
    st.header("🔥 Predicted Calories Burned")
    st.metric(label="Estimated Calories Burned", value=f"{round(prediction[0], 2)} kcal")

with tabs[2]:
    # Show similar results from dataset
    st.header("🔍 Similar Results")
    similar_data = df_combined[(df_combined["Calories"] >= prediction[0] - 10) & (df_combined["Calories"] <= prediction[0] + 10)]
    st.write(similar_data.sample(5) if not similar_data.empty else "No similar data found.")

with tabs[3]:
    # Display general insights and comparison to dataset
    st.header("📈 General Insights")
    st.write(f"You are older than <span style='color:blue; font-weight:bold;'>{round((df_combined['Age'] < df['Age'].values[0]).mean() * 100, 2)}%</span> of users.", unsafe_allow_html=True)
    st.write(f"Your exercise duration is higher than <span style='color:blue; font-weight:bold;'>{round((df_combined['Duration'] < df['Duration'].values[0]).mean() * 100, 2)}%</span> of users.", unsafe_allow_html=True)
    st.write(f"Your heart rate is higher than <span style='color:blue; font-weight:bold;'>{round((df_combined['Heart_Rate'] < df['Heart_Rate'].values[0]).mean() * 100, 2)}%</span> of users.", unsafe_allow_html=True)
    st.write(f"Your body temperature is higher than <span style='color:blue; font-weight:bold;'>{round((df_combined['Body_Temp'] < df['Body_Temp'].values[0]).mean() * 100, 2)}%</span> of users.", unsafe_allow_html=True)