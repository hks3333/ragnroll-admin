import os
import csv
import streamlit as st
import boto3
from io import StringIO

# Initialize S3 client
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

# Initialize session state for page navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Sidebar for navigation
st.sidebar.title("Admin")
if st.sidebar.button("Home"):
    st.session_state.page = "Home"
if st.sidebar.button("Upload Files"):
    st.session_state.page = "Upload Files"
if st.sidebar.button("Edit Existing Files"):
    st.session_state.page = "Edit Existing Files"

# Function to upload file to S3
def upload_to_s3(file, bucket_name, object_name):
    try:
        s3.upload_fileobj(file, bucket_name, object_name)
        return True
    except Exception as e:
        st.error(f"Error uploading file to S3: {e}")
        return False

def generate_metadata_csv(file_name, departments, semesters, tags):
    # Replace "All" with the full list of values
    if "All" in departments:
        departments = DEPARTMENTS
    if "All" in semesters:
        semesters = SEMESTERS
    
    # Create a CSV string with headers and data
    csv_output = StringIO()
    writer = csv.writer(csv_output)
    
    # Write headers
    writer.writerow(["file_name", "departments", "semesters", "tags"])
    
    # Write data
    writer.writerow([
        file_name,                     # file_name
        ",".join(departments),         # departments
        ",".join(semesters),           # semesters
        ",".join(tags)                 # tags
    ])
    
    # Return the CSV string
    return csv_output.getvalue()

# Homepage
def homepage():
    st.write("Welcome to the PDF Upload and Management System!")
    st.write("Use the navigation sidebar to switch between pages.")

# Upload page
def upload_page():
    st.write("### Upload PDFs")
    
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
                # Rename the file
                new_name = st.session_state[f"name_{i}"]
                new_file_name = f"{new_name}.pdf"
                
                # Generate metadata CSV
                metadata = generate_metadata_csv(
                    new_name,  # File name without extension
                    st.session_state[f"dept_{i}"],
                    st.session_state[f"sem_{i}"],
                    st.session_state[f"tags_{i}"]
                )
                
                # Upload the renamed PDF file to S3
                pdf_object_name = f"documents/{new_file_name}"
                if upload_to_s3(uploaded_file, "ragnroll", pdf_object_name):
                    st.success(f"File {new_file_name} uploaded to S3.")
                    
                    # Upload the metadata CSV file to S3
                    # Upload the metadata CSV file to S3
                    metadata_object_name = f"documents/{new_name}.csv"
                    try:
                        # Generate the CSV metadata
                        csv_metadata = generate_metadata_csv(
                            new_name,  # File name without extension
                            st.session_state[f"dept_{i}"],
                            st.session_state[f"sem_{i}"],
                            st.session_state[f"tags_{i}"]
                        )
                        
                        # Upload the CSV file to S3
                        s3.put_object(
                            Bucket="ragnroll",
                            Key=metadata_object_name,
                            Body=csv_metadata
                        )
                        st.success(f"Metadata for {new_file_name} uploaded to S3.")
                    except Exception as e:
                        st.error(f"Error uploading metadata for {new_file_name}: {e}")
        else:
            st.warning("No files uploaded.")

# Edit page
def edit_page():
    st.write("### Edit Existing Files")

    # List all files in the S3 bucket
    try:
        response = s3.list_objects_v2(Bucket="ragnroll", Prefix="documents/")
        if "Contents" in response:
            files = [obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".pdf")]
        else:
            st.warning("No files found in the S3 bucket.")
            return
    except Exception as e:
        st.error(f"Error listing files from S3: {e}")
        return

    # Dropdown to select a file
    selected_file = st.selectbox("Select a file to edit", files, index=None)

    if selected_file:
        # Fetch metadata CSV file
        metadata_file = selected_file.replace(".pdf", ".csv")
        try:
            metadata_response = s3.get_object(Bucket="ragnroll", Key=metadata_file)
            metadata_content = metadata_response["Body"].read().decode("utf-8")
            
            # Parse the CSV content
            reader = csv.reader(StringIO(metadata_content))
            headers = next(reader)  # Skip headers
            file_name, departments, semesters, tags = next(reader)
            
            # Split comma-separated values into lists
            departments = departments.split(",")
            semesters = semesters.split(",")
            tags = tags.split(",")
        except Exception as e:
            st.error(f"Error fetching metadata for {selected_file}: {e}")
            metadata = {}

        # Display file name (editable)
        file_name = file_name or selected_file.split("/")[-1].replace(".pdf", "")
        new_name = st.text_input("File Name", value=file_name, key="edit_name")

        # Department selection (multi-select dropdown with "All" option)
        departments = st.multiselect(
            "Department(s)",
            options=["All"] + DEPARTMENTS,
            default=departments,
            key="edit_dept"
        )
        if "All" in departments:
            departments = DEPARTMENTS

        # Semester selection (multi-select dropdown with "All" option)
        semesters = st.multiselect(
            "Semester(s)",
            options=["All"] + SEMESTERS,
            default=semesters,
            key="edit_sem"
        )
        if "All" in semesters:
            semesters = SEMESTERS

        # Tags selection (multi-select dropdown)
        tags = st.multiselect(
            "Tags",
            options=PREDEFINED_TAGS,
            default=tags,
            key="edit_tags"
        )

        # Save changes button
        if st.button("Save Changes"):
            try:
                # Generate updated metadata CSV
                updated_metadata_csv = generate_metadata_csv(
                    new_name,
                    departments,
                    semesters,
                    tags
                )

                # Upload updated metadata CSV file to S3
                s3.put_object(
                    Bucket="ragnroll",
                    Key=metadata_file,
                    Body=updated_metadata_csv
                )
                st.success("Metadata updated successfully!")
            except Exception as e:
                st.error(f"Error updating metadata: {e}")

        # Delete file button
        if st.button("Delete File"):
            try:
                # Delete PDF file from S3
                s3.delete_object(Bucket="ragnroll", Key=selected_file)
                
                # Delete metadata CSV file from S3
                s3.delete_object(Bucket="ragnroll", Key=metadata_file)
                
                st.success(f"File {selected_file} and its metadata deleted successfully!")
                # Rerun the script to refresh the file list
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting file: {e}")
    else:
        st.warning("No file selected.")

# Page routing
if st.session_state.page == "Home":
    homepage()
elif st.session_state.page == "Upload Files":
    upload_page()
elif st.session_state.page == "Edit Existing Files":
    edit_page()