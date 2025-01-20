import os
import streamlit as st
import boto3

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
                # Generate S3 object name
                object_name = f"documents/{uploaded_file.name}"
                
                # Prepare metadata
                metadata = {
                    "file_name": st.session_state[f"name_{i}"],
                    "departments": ",".join(st.session_state[f"dept_{i}"]),
                    "semesters": ",".join(st.session_state[f"sem_{i}"]),
                    "tags": ",".join(st.session_state[f"tags_{i}"])
                }
                
                # Upload file to S3 with metadata
                try:
                    s3.upload_fileobj(
                        uploaded_file,
                        "ragnroll",
                        object_name,
                        ExtraArgs={"Metadata": metadata}
                    )
                    st.success(f"File {uploaded_file.name} uploaded to S3 with metadata.")
                except Exception as e:
                    st.error(f"Error uploading {uploaded_file.name}: {e}")
        else:
            st.warning("No files uploaded.")




def edit_page():
    st.write("### Edit Existing Files")

    # List all files in the S3 bucket
    try:
        response = s3.list_objects_v2(Bucket="ragnroll", Prefix="documents/")
        if "Contents" in response:
            files = [obj["Key"] for obj in response["Contents"]]
        else:
            st.warning("No files found in the S3 bucket.")
            return
    except Exception as e:
        st.error(f"Error listing files from S3: {e}")
        return

    # Dropdown to select a file
    selected_file = st.selectbox("Select a file to edit", files, index=None)

    if selected_file:
        # Fetch metadata for the selected file
        try:
            metadata = s3.head_object(Bucket="ragnroll", Key=selected_file)["Metadata"]
        except Exception as e:
            st.error(f"Error fetching metadata for {selected_file}: {e}")
            metadata = {}

        # Display file name from metadata (not the original PDF name)
        file_name = metadata.get("file_name", selected_file.split("/")[-1].replace(".pdf", ""))
        new_name = st.text_input("File Name", value=file_name, key="edit_name")

        # Department selection (multi-select dropdown with "All" option)
        departments = st.multiselect(
            "Department(s)",
            options=["All"] + DEPARTMENTS,
            default=metadata.get("departments", "").split(",") if metadata.get("departments") else [],
            key="edit_dept"
        )
        if "All" in departments:
            departments = DEPARTMENTS

        # Semester selection (multi-select dropdown with "All" option)
        semesters = st.multiselect(
            "Semester(s)",
            options=["All"] + SEMESTERS,
            default=metadata.get("semesters", "").split(",") if metadata.get("semesters") else [],
            key="edit_sem"
        )
        if "All" in semesters:
            semesters = SEMESTERS

        # Tags selection (multi-select dropdown)
        tags = st.multiselect(
            "Tags",
            options=PREDEFINED_TAGS,
            default=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
            key="edit_tags"
        )

        # Save changes button
        if st.button("Save Changes"):
            try:
                # Update metadata in S3
                s3.copy_object(
                    Bucket="ragnroll",
                    Key=selected_file,
                    CopySource={"Bucket": "ragnroll", "Key": selected_file},
                    Metadata={
                        "file_name": new_name,
                        "departments": ",".join(departments),
                        "semesters": ",".join(semesters),
                        "tags": ",".join(tags)
                    },
                    MetadataDirective="REPLACE"
                )
                st.success("Metadata updated successfully!")
            except Exception as e:
                st.error(f"Error updating metadata: {e}")

        # Delete file button
        if st.button("Delete File"):
            try:
                s3.delete_object(Bucket="ragnroll", Key=selected_file)
                st.success(f"File {selected_file} deleted successfully!")
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
