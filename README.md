# Result Management System

## 📌 Overview
This is a **Result Management System** built using **Python** and **Streamlit**. The application allows users to:

✅ **Upload exam results** in PDF format.  
✅ **View results** by selecting class and exam name.  
✅ **Extract and display text** from uploaded PDFs.  
✅ **Download full class results** in PDF format.  
✅ **Delete results** when no longer needed.  

## 🚀 Features
- **Upload Result**: Upload a PDF containing exam results for a specific class and exam.
- **View Result**: Select a class and exam to view extracted text from the PDF.
- **Download Result**: Download the full class result in PDF format.
- **Delete Result**: Remove uploaded results if needed.

## 📦 Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/result-management.git
   cd result-management
   ```
2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # For macOS/Linux
   venv\Scripts\activate  # For Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## ▶️ Running the Application
Run the following command to start the Streamlit app:
```sh
streamlit run app.py
```

## 📝 Requirements
Ensure you have Python 3.8+ installed. The required libraries are:
- `streamlit`
- `pymupdf`
- `pandas`
- `reportlab`

---
Developed with ❤️ using Python & Streamlit
