import streamlit as st
import fitz  # PyMuPDF for reading PDFs
import os
import pickle
import pandas as pd

# Directory setup
data_store = "results/"  
students_data_file = "students.pkl"  
os.makedirs(data_store, exist_ok=True)

# Load & Save Student Data
def load_students():
    if os.path.exists(students_data_file):
        with open(students_data_file, "rb") as f:
            students = pickle.load(f)
            # Ensure backward compatibility by adding missing fields
            for student in students:
                student.setdefault("father_name", "")
                student.setdefault("mobile_no", "")
                student.setdefault("address", "")
            return students
    return []

def save_students(students):
    with open(students_data_file, "wb") as f:
        pickle.dump(students, f)

# Add Student
def add_student(roll_no, name, father_name, student_class, mobile_no, address):
    students = load_students()
    if any(student["roll_no"] == roll_no for student in students):
        return False  # Roll No already exists
    students.append({
        "roll_no": roll_no,
        "name": name,
        "father_name": father_name,
        "class": student_class,
        "mobile_no": mobile_no,
        "address": address
    })
    save_students(students)
    return True

# Search Students
def search_students(search_term, search_type):
    students = load_students()
    if search_type == "Roll No":
        return [s for s in students if s["roll_no"] == search_term]
    elif search_type == "Name":
        return [s for s in students if search_term.lower() in s["name"].lower()]
    elif search_type == "Class":
        return [s for s in students if s["class"] == search_term]
    return students

# Load & Save Users
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
        return False  
    users[username] = password
    save_users(users)
    return True

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    if not st.session_state.logged_in:
        st.title("📚 Jamia Ishaatul Islam")
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
            parts = file.split("_")
            class_name = "_".join(parts[:-1])
            exam_name = parts[-1].replace(".pdf", "")
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

# Main App
if check_login():
    st.sidebar.button("Logout", on_click=logout)
    menu = ["📤 Upload Result", "📑 View Result", "🗑️ Delete Result", "👩‍🎓 Add Student Data", "📋 View Student Data", "🗑️ Delete Student Data"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "📤 Upload Result":
        st.subheader("Upload Exam Result (PDF)")
        class_name = st.text_input("Enter Class Name")
        exam_name = st.text_input("Enter Exam Name")
        uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])
        
        if uploaded_file and class_name and exam_name:
            save_uploaded_file(uploaded_file, class_name, exam_name)
            st.success("Result uploaded successfully!")

    elif choice == "📑 View Result":
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
                st.download_button("Download Full Class Result", get_original_pdf(selected_class, selected_exam), f"{selected_class}_{selected_exam}.pdf", "application/pdf")

    elif choice == "🗑️ Delete Result":
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

    elif choice == "👩‍🎓 Add Student Data":
        # Initialize session state for input fields
        if "student_data" not in st.session_state:
            st.session_state.student_data = {
                "roll_no": "",
                "name": "",
                "father_name": "",
                "class": "",
                "mobile_no": "",
                "address": ""
            }

        st.subheader("Add Student Data")

        # Input fields
        st.session_state.student_data["roll_no"] = st.text_input("Roll No", value=st.session_state.student_data["roll_no"])
        st.session_state.student_data["name"] = st.text_input("Name", value=st.session_state.student_data["name"])
        st.session_state.student_data["father_name"] = st.text_input("Father Name", value=st.session_state.student_data["father_name"])
        st.session_state.student_data["class"] = st.text_input("Class", value=st.session_state.student_data["class"])
        st.session_state.student_data["mobile_no"] = st.text_input("Mobile No", value=st.session_state.student_data["mobile_no"])
        st.session_state.student_data["address"] = st.text_area("Address", value=st.session_state.student_data["address"])

        # Function to add student and reset form
        def add_student_data():
            if all(st.session_state.student_data.values()):  # Ensure all fields are filled
                if add_student(
                    st.session_state.student_data["roll_no"],
                    st.session_state.student_data["name"],
                    st.session_state.student_data["father_name"],
                    st.session_state.student_data["class"],
                    st.session_state.student_data["mobile_no"],
                    st.session_state.student_data["address"],
                ):
                    st.success("Student added successfully!")
                    # Clear input fields for new entries
                    st.session_state.student_data = {
                        "roll_no": "",
                        "name": "",
                        "father_name": "",
                        "class": "",
                        "mobile_no": "",
                        "address": ""
                    }
                else:
                    st.error("Roll No already exists!")
            else:
                st.warning("Please fill in all fields.")

        st.button("Add Student", on_click=add_student_data)

    elif choice == "📋 View Student Data":
        st.subheader("View Student Data")
        search_type = st.radio("Search By", ["Roll No", "Name", "Class", "View All"])
        search_term = st.text_input(f"Enter {search_type}") if search_type != "View All" else None

        if st.button("Search"):
            results = search_students(search_term, search_type)
            if results:
                # Display student data in a table format
                df = pd.DataFrame(results)
                st.dataframe(df)

                # Provide an option to download the student data as a CSV file
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Student Data as CSV",
                    data=csv,
                    file_name="students_data.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No students found.")

    elif choice == "🗑️ Delete Student Data":
        st.subheader("Delete Student Data")
        students = load_students()

        if not students:
            st.warning("No student data available.")
        else:
            # Create dropdowns to select a student by roll number
            roll_numbers = [student["roll_no"] for student in students]
            selected_roll_no = st.selectbox("Select Roll No", roll_numbers)

            if st.button("Delete Student"):
                updated_students = [s for s in students if s["roll_no"] != selected_roll_no]
                save_students(updated_students)
                st.success(f"Student with Roll No {selected_roll_no} deleted successfully!")
                st.experimental_rerun()  # Refresh the page after deletion
