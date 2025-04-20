import streamlit as st

st.set_page_config(page_title="🛡 Mindfit AI Companion", layout="centered")

# Title with improved icon
st.markdown("<h1 style='text-align: center;'>🛡 Welcome to Secure Portal</h1>", unsafe_allow_html=True)
st.markdown("### Please Sign In or Sign Up below:")

# Tabs for Sign In and Sign Up
tab1, tab2 = st.tabs(["🔐 Sign In", "🆕 Sign Up"]) 

# --- Sign In Tab ---
with tab1:
    st.subheader("Sign In to your account")
    with st.form("sign_in_form"):
        login_user = st.text_input("Username")
        login_pass = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Sign In")

    if login_submit:
        if login_user and login_pass:
            st.success(f"✅ Welcome back, {login_user}!")
        else:
            st.error("❌ Please enter both username and password.")

# --- Sign Up Tab ---
with tab2:
    st.subheader("Create a new account")
    with st.form("sign_up_form"):
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")
        new_age = st.number_input("Your Age", min_value=1, max_value=120, step=1)
        sign_up_submit = st.form_submit_button("Sign Up")

    if sign_up_submit:
        if new_user and new_pass and new_age > 0:
            st.success(f"🎉 Account created successfully for {new_user} (Age: {int(new_age)})!")
        else:
            st.warning("⚠ Please complete all fields to sign up.")