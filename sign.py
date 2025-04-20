import streamlit as st
from auth import create_users_table, add_user, authenticate_user
import os
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import json
import google.generativeai as genai
from transformers import pipeline
import re 

# ⛳ Set page config IMMEDIATELY after imports
st.set_page_config(page_title=" 🧠 Mindfit AI Companion", layout="wide")

# Initialize users table
create_users_table()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ------------------- LOGIN/SIGNUP PAGE -------------------
if not st.session_state.authenticated:
    st.title("🧠 Mindfit AI Companion")
    tab1, tab2 = st.tabs(["🔐 Sign In", "🆕 Sign Up"])

    with tab1:
        st.subheader("Sign In to your account")
        with st.form("sign_in"):
            login_user = st.text_input("Username")
            login_pass = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Sign In")

        if login_submit:
            if authenticate_user(login_user, login_pass):
                st.success("✅ Login successful!")
                st.session_state.authenticated = True
                st.session_state.current_user = login_user
                st.rerun()
            else:
                st.error("❌ Invalid credentials!")

    with tab2:
        st.subheader("Create a new account")
        with st.form("sign_up"):
            new_user = st.text_input("Create Username")
            new_pass = st.text_input("Create Password", type="password")
            new_age = st.number_input("Your Age", min_value=1, max_value=120, step=1)
            sign_up_submit = st.form_submit_button("Sign Up")

        if sign_up_submit:
            if new_user and new_pass and new_age:
                try:
                    add_user(new_user, new_pass, new_age)
                    st.session_state.authenticated = True
                    st.session_state.current_user = new_user
                    st.success("🎉 Account created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error("❌ Username already exists or error occurred.")
            else:
                st.warning("⚠ Please fill all fields.")
        
        st.stop()

# ------------------- MAIN APP -------------------

# Load environment variables

# Set up Gemini client
# Set up Gemini client with hardcoded public API key

genai.configure(api_key="AIzaSyAl4rEdDYGSo0DL6Htl2sHmwP3tazBghmc")


# Set up emotion detection pipeline
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=1)

# Main page title
st.title("🧠 Mindfit AI Companion")

# Sidebar
if st.session_state.current_user:
    st.sidebar.success(f"👤 Logged in as: {st.session_state.current_user}")
else:
    st.sidebar.info("🔐 Please sign in to access your data.")

# Sidebar usage guide
st.sidebar.title("📖 How to Use")
st.sidebar.markdown("""
1. **Chat Companion Tab**: 
   - Share how you're feeling in the text box.
   - The app detects your emotion and responds supportively.

2. **Google Fit Dashboard Tab**:
   - Upload your `.json` files from Google Fit.
   - View visualizations of your fitness and health metrics.

---
📧 Email: [contact@betterhelp.com](mailto:contact@betterhelp.com)  
🌐 Visit: [https://www.betterhelp.com/](https://www.betterhelp.com/)
""")

# Main usage guide
with st.expander("📘 How to Use This Website"):
    st.markdown("""
    Welcome to your **🧠 Mindfit AI Companion**! Here's how to use it:

    ### 🗣️ Chat Companion
    1. Head over to the **Chat Companion** tab.
    2. Type in how you’re feeling or anything you want to talk about.
    3. The assistant will detect your emotion and respond with support.
    4. You’ll also see your chat history below the conversation.

    ### 📊 Google Fit Dashboard
    1. Go to the **Google Fit Dashboard** tab.
    2. Upload your `.json` files from your **Google Fit Takeout**.
    3. View visualizations of your:
        - Steps
        - Sleep
        - Calories Burned
        - Weight & Body Fat % 
        - Heart Rate
        - Hydration and more!
    """)

# ------------------- TABS -------------------
tab1, tab2 = st.tabs(["🗣️ Chat Companion", "📊 Google Fit Dashboard"])

# ---------------- TAB 1: Chat Companion ----------------
with tab1:
    st.markdown("<p style='text-align: center;'>How are you feeling today? Share with me 💬</p>", unsafe_allow_html=True)

    # Custom CSS
    st.markdown("""<style>
    .chat-history { padding-bottom: 120px; }
    .input-container {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 800px;
    }
    .chat-bubble {
        padding: 10px 15px;
        margin: 10px;
        border-radius: 15px;
        max-width: 80%;
        line-height: 1.5;
        color: black !important;
    }
    .user { background-color: #DCF8C6; margin-left: auto; text-align: right; }
    .ai { background-color: #F1F0F0; margin-right: auto; text-align: left; }
    </style>""", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Input container
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input("", placeholder="eg: I am feeling tired...", label_visibility="collapsed")
        with col2:
            send_clicked = st.form_submit_button("Send")
    st.markdown("</div>", unsafe_allow_html=True)

    # Handle chat
    if send_clicked and user_input.strip():
        emotion_result = emotion_classifier(user_input)[0]
        detected_emotion = emotion_result[0]['label']
        st.markdown(f"**❄️ Detected Emotion:** {detected_emotion}")

        if detected_emotion.lower() in ["sadness", "depressed", "anger", "fear"]:
            st.warning("You're not alone. Reach out to 📧 Email: contact@betterhelp.com or visit https://www.betterhelp.com/")

        st.session_state.chat_history.append({"role": "user", "parts": [{"text": user_input}]})

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=st.session_state.chat_history
            )
            ai_text = response.text.strip()
            st.session_state.chat_history.append({"role": "assistant", "parts": [{"text": ai_text}]})
        except Exception as e:
            st.error(f"Error: {e}")

    # Display chat history
    st.markdown("<div class='chat-history'>", unsafe_allow_html=True)
    st.subheader("📜 Chat History")
    for msg in reversed(st.session_state.chat_history):
        role_class = "user" if msg["role"] == "user" else "ai"
        text = msg["parts"][0]["text"]
        st.markdown(f"<div class='chat-bubble {role_class}'>{text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TAB 2: Google Fit Dashboard ----------------
with tab2:
    st.markdown("<h2 style='text-align: center;'>📊 Google Fit Health Dashboard</h2>", unsafe_allow_html=True)

    def parse_date(nano_time):
        try:
            return dt.datetime.fromtimestamp(int(nano_time) / 1e9).date()
        except:
            return None

    uploaded_files = st.file_uploader("📂 Upload your Google Fit JSON files", type=["json"], accept_multiple_files=True)

    # Initialize lists
    steps_data, weight_data, fat_data, height_data = [], [], [], []
    heart_data, resp_data, hydration_data, calories_data, sleep_data, active_minutes_data = [], [], [], [], [], []


    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                data = json.load(uploaded_file)
                data_points = data.get("Data Points", [])
                for dp in data_points:
                    start_nano = dp.get("startTimeNanos", 0)
                    end_nano = dp.get("endTimeNanos", 0)
                    date_only = parse_date(start_nano)
                    data_type = dp.get("dataTypeName", "").lower()
                    value = dp.get("fitValue", [{}])[0].get("value", {})
                    int_val = value.get("intVal")
                    fp_val = value.get("fpVal")

                    if "step_count" in data_type:
                        steps_data.append({"Date": date_only, "Steps": int_val or 0})
                    elif "heart_rate" in data_type:
                        heart_data.append({"Date": date_only, "Heart Rate (BPM)": fp_val or 0})
                    elif "weight" in data_type:
                        weight_data.append({"Date": date_only, "Weight (kg)": fp_val or 0})
                    elif "body_fat" in data_type:
                        fat_data.append({"Date": date_only, "Body Fat (%)": fp_val or 0})
                    elif "height" in data_type:
                        height_data.append({"Date": date_only, "Height (m)": fp_val or 0})
                    elif "respiratory_rate" in data_type:
                        resp_data.append({"Date": date_only, "Respiratory Rate": fp_val or 0})
                    elif "hydration" in data_type:
                        hydration_data.append({"Date": date_only, "Hydration (ml)": fp_val or 0})
                    elif "calories" in data_type:
                        calories_data.append({"Date": date_only, "Calories (kcal)": fp_val or 0})
                    elif "sleep" in data_type and end_nano:
                        duration_hours = (int(end_nano) - int(start_nano)) / 1e9 / 3600
                        sleep_data.append({"Date": date_only, "Sleep (hrs)": round(duration_hours, 2)})
                    elif "active_minutes" in data_type:
                        active_minutes_data.append({"Date": date_only, "Active Minutes": int_val or 0})
            except Exception as e:
                st.error(f"❌ Error reading {uploaded_file.name}: {e}")

        def plot_metric(df, x_col, y_col, chart_type="bar", color=None, title=""):
            if df.empty:
                return
            fig = px.bar(df, x=x_col, y=y_col, color=color or y_col, title=title) if chart_type == "bar" else px.line(df, x=x_col, y=y_col, markers=True, title=title)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

        # Plotting each metric
        if steps_data:
            st.subheader("🚶 Daily Steps")
            df = pd.DataFrame(steps_data).groupby("Date")["Steps"].sum().reset_index()
            plot_metric(df, "Date", "Steps", "bar", title="Steps Over Time")

        if heart_data:
            st.subheader("❤️ Heart Rate")
            df = pd.DataFrame(heart_data).groupby("Date")["Heart Rate (BPM)"].mean().reset_index()
            plot_metric(df, "Date", "Heart Rate (BPM)", "line", title="Heart Rate Over Time")

        if weight_data:
            st.subheader("⚖️ Weight")
            df = pd.DataFrame(weight_data).groupby("Date")["Weight (kg)"].mean().reset_index()
            plot_metric(df, "Date", "Weight (kg)", "line", title="Weight Trend")

        if fat_data:
            st.subheader("💧 Body Fat %")
            df = pd.DataFrame(fat_data).groupby("Date")["Body Fat (%)"].mean().reset_index()
            plot_metric(df, "Date", "Body Fat (%)", "line", title="Body Fat Trend")

        if hydration_data:
            st.subheader("💧 Hydration Intake")
            df = pd.DataFrame(hydration_data).groupby("Date")["Hydration (ml)"].sum().reset_index()
            plot_metric(df, "Date", "Hydration (ml)", "bar", title="Hydration Over Time")

        if calories_data:
            st.subheader("🔥 Calories Burned")
            df = pd.DataFrame(calories_data).groupby("Date")["Calories (kcal)"].sum().reset_index()
            plot_metric(df, "Date", "Calories (kcal)", "bar", title="Calories Burned Over Time")

        if sleep_data:
            st.subheader("🛌 Sleep Duration")
            df = pd.DataFrame(sleep_data).groupby("Date")["Sleep (hrs)"].sum().reset_index()
            plot_metric(df, "Date", "Sleep (hrs)", "bar", title="Sleep Duration")

        if active_minutes_data:
            st.subheader("💪 Active Minutes")
            df = pd.DataFrame(active_minutes_data).groupby("Date")["Active Minutes"].sum().reset_index()
            plot_metric(df, "Date", "Active Minutes", "bar", title="Active Minutes")

        if not any([steps_data, heart_data, weight_data, fat_data, hydration_data, calories_data, sleep_data]):
            st.warning("✅ Files loaded but no matching data types were found.")
    else:
        st.info("👆 Upload your Google Fit Takeout `.json` files to view visualizations.")
