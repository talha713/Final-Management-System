import streamlit as st
import fitz  # PyMuPDF for reading PDFs
import pandas as pd
import os
import pickle
from io import BytesIO
from reportlab.pdfgen import canvas

# Directory and cache setup
data_store = "results/"  # Directory to store PDFs
cache_file = "cache.pkl"  # File to store persistent state
os.makedirs(data_store, exist_ok=True)

# User authentication
def load_users():
    if os.path.exists("users.pkl"):
        with open("users.pkl", "rb") as f:
            return pickle.load(f)
    return {}

def save_users(users):
    with open("users.pkl", "wb") as f:
        pickle.dump(users, f)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False  # User already exists
    users[username] = password
    save_users(users)
    return True

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    if not st.session_state.logged_in:
        # Centered Institute Logo
        st.markdown(
            """
            <style>
            .centered-img {
                display: flex;
                justify-content: center;
            }
            </style>
            <div class="centered-img">
            """,
            unsafe_allow_html=True
        )
        
        st.image("logo-removebg-preview.png", width=200)

        st.markdown("</div>", unsafe_allow_html=True)  # Closing the div

        st.title("📚 Institute Result Management System")

        choice = st.radio("Choose an option", ["Login", "Register"], horizontal=True)

        if choice == "Register":
            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password", type="password")
            if st.button("Register"):
                if register_user(new_username, new_password):
                    st.success("User registered successfully! Redirecting to login...")
                    st.session_state.logged_in = False
                    st.rerun()
                else:
                    st.error("Username already taken.")

        elif choice == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_clicked = st.button("Login")
            users = load_users()

            if login_clicked and username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            elif login_clicked:
                st.error("Invalid credentials. Try again.")
        return False
    return True

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

def get_user_folder():
    user_folder = os.path.join(data_store, st.session_state.username)
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def save_uploaded_file(uploaded_file, class_name, exam_name):
    file_path = os.path.join(get_user_folder(), f"{class_name}_{exam_name}.pdf")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def list_saved_results():
    files = os.listdir(get_user_folder())
    result_data = []
    for file in files:
        if file.endswith(".pdf"):
            class_name, exam_name = file.rsplit("_", 1)
            exam_name = exam_name.replace(".pdf", "")
            result_data.append((class_name, exam_name, file))
    return result_data

def get_original_pdf(class_name, exam_name):
    file_path = os.path.join(get_user_folder(), f"{class_name}_{exam_name}.pdf")
    with open(file_path, "rb") as pdf_file:
        return pdf_file.read()

def delete_result(class_name, exam_name):
    file_path = os.path.join(get_user_folder(), f"{class_name}_{exam_name}.pdf")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

# Main app interface
if check_login():
    st.title("📊 Result Management System")
    st.sidebar.button("Logout", on_click=logout)
    menu = ["Upload Result", "View Result", "Delete Result"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Upload Result":
        st.subheader("Upload Exam Result (PDF)")
        class_name = st.text_input("Enter Class Name")
        exam_name = st.text_input("Enter Exam Name")
        uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])
        
        if uploaded_file and class_name and exam_name:
            save_uploaded_file(uploaded_file, class_name, exam_name)
            st.success("Result uploaded successfully!")

    elif choice == "View Result":
        st.subheader("View Exam Result")
        result_data = list_saved_results()
        if not result_data:
            st.warning("No results uploaded yet.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                exams = list(set([r[1] for r in result_data]))
                selected_exam = st.selectbox("Select Exam", exams)
            with col2:
                classes = [r[0] for r in result_data if r[1] == selected_exam]
                selected_class = st.selectbox("Select Class", classes)
            
            if st.button("Show Result"):
                pdf_path = os.path.join(get_user_folder(), f"{selected_class}_{selected_exam}.pdf")
                st.download_button("Download Full Class Result", get_original_pdf(selected_class, selected_exam), f"{selected_class}_{selected_exam}.pdf", "application/pdf")

    elif choice == "Delete Result":
        st.subheader("Delete Exam Result")
        result_data = list_saved_results()
        if not result_data:
            st.warning("No results uploaded yet.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                exams = list(set([r[1] for r in result_data]))
                selected_exam = st.selectbox("Select Exam", exams)
            with col2:
                classes = [r[0] for r in result_data if r[1] == selected_exam]
                selected_class = st.selectbox("Select Class", classes)
            
            if st.button("Delete Result"):
                if delete_result(selected_class, selected_exam):
                    st.success("Result deleted successfully!")
                else:
                    st.error("Error deleting the result.")
