import os
import streamlit as st
import boto3

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Predefined tags
PREDEFINED_TAGS = ["Textbook", "Lecture Notes", "Research Paper", "Policy", "Announcement", "Notice", "Rulebook", "Other"]

# Predefined departments
DEPARTMENTS = [
    "Department of Computer Science",
    "Department of Mechanical Engineering",
    "Department of Electrical Engineering",
    "Department of Civil Engineering",
    "Department of Mathematics",
    "Department of Physics",
    "Department of Chemistry",
    "Department of Humanities",
]

# Predefined semesters
SEMESTERS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "Supply"]

# Streamlit app
st.title("PDF Upload and Management")

bucket_name = "ragnroll"
def upload_to_s3(file, bucket_name, object_name):
    try:
        s3.upload_fileobj(file, bucket_name, object_name)
        return True
    except Exception as e:
        st.error(f"Error uploading file to S3: {e}")
        return False

# File uploader for multiple PDFs
uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

# Display uploaded files in a grid
if uploaded_files:
    st.subheader("Uploaded PDFs")
    cols = st.columns(2)  # 2-column grid
    for i, uploaded_file in enumerate(uploaded_files):
        with cols[i % 2]:  # Distribute files across columns
            st.write(f"**File {i + 1}**")
            
            # Display file name (editable, without .pdf extension)
            file_name = uploaded_file.name.replace(".pdf", "")
            new_name = st.text_input(f"Name for File {i + 1}", value=file_name, key=f"name_{i}")
            
            # Department selection (multi-select dropdown with "All" option)
            departments = st.multiselect(
                f"Department(s) for File {i + 1}",
                options=["All"] + DEPARTMENTS,  # Add "All" option
                default=[],  # Default to empty
                key=f"dept_{i}"
            )
            # If "All" is selected, choose all departments
            if "All" in departments:
                departments = DEPARTMENTS
            
            # Semester selection (multi-select dropdown with "All" option)
            semesters = st.multiselect(
                f"Semester(s) for File {i + 1}",
                options=["All"] + SEMESTERS,  # Add "All" option
                default=[],  # Default to empty
                key=f"sem_{i}"
            )
            # If "All" is selected, choose all semesters
            if "All" in semesters:
                semesters = SEMESTERS
            
            # Tags selection (multi-select dropdown)
            tags = st.multiselect(
                f"Tags for File {i + 1}",
                options=PREDEFINED_TAGS,
                default=[],  # Default to empty
                key=f"tags_{i}"
            )
            
            st.write("---")  # Separator between files

# Upload button
if st.button("Upload All Files"):
    if uploaded_files:
        for i, uploaded_file in enumerate(uploaded_files):
            # Generate S3 object name
            object_name = f"documents/{uploaded_file.name}"
            
            # Upload file to S3
            if upload_to_s3(uploaded_file, bucket_name, object_name):
                st.success(f"File {uploaded_file.name} uploaded to S3.")
            else:
                st.error(f"Failed to upload {uploaded_file.name}.")
    else:
        st.warning("No files uploaded.")