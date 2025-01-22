# Admin Portal for Educational Institutions
The Admin Portal is a Streamlit-based web application designed specifically for educational institutions to manage and organize PDF files and their metadata. It provides a seamless interface for administrators to upload, edit, and delete educational resources, ensuring efficient document management and easy access for students and faculty.

### Key Features
##### File Upload:

Upload multiple PDF files (e.g., textbooks, lecture notes, research papers) to a centralized AWS S3 bucket.

Rename files and assign metadata (e.g., departments, semesters, tags) during upload.

Automatically generate and upload metadata CSV files for each PDF.

##### Edit Existing Files:

View and edit metadata for existing PDFs (e.g., update departments, semesters, or tags).

Rename files and update metadata directly from the portal.

Delete outdated or irrelevant files and their associated metadata.

##### Metadata Management:

Predefined options for departments, semesters, and tags to ensure consistency.

Supports bulk metadata updates for multiple files.

##### S3 Integration:

Seamless integration with AWS S3 for secure and scalable file storage.

Uses boto3 for efficient S3 operations, ensuring reliability and performance.

##### User-Friendly Interface:

Simple navigation with a sidebar for switching between Home, Upload Files, and Edit Existing Files.

Real-time feedback and error handling for all operations.

### Use Cases for Educational Institutions
Course Material Management:

Upload and organize textbooks, lecture notes, and assignments for each semester.

Assign metadata (e.g., department, semester) for easy filtering and retrieval.

Research Paper Repository:

Store and manage research papers and publications with relevant tags (e.g., topics, authors).

Update metadata as new research is published.

Policy and Announcement Distribution:

Upload policy documents, announcements, and rulebooks.

Assign tags (e.g., "Policy", "Announcement") for quick access.

Faculty Resource Sharing:

Share teaching resources, presentations, and study materials across departments.

Edit or delete outdated resources as needed.

Benefits for Educational Institutions
Centralized Document Management: All files and metadata are stored in a single, secure location (AWS S3).

Efficient Organization: Metadata (departments, semesters, tags) ensures easy categorization and retrieval.

Time-Saving: Streamlined workflows for uploading, editing, and deleting files.

Scalable: Designed to handle large volumes of documents as the institution grows.

User-Friendly: Intuitive interface for administrators with no technical expertise required.

How It Works
Upload Files:

Administrators upload PDFs (e.g., lecture notes, textbooks) and assign metadata (departments, semesters, tags).

Files and metadata are automatically stored in the S3 bucket.

Edit Files:

Administrators can update file names, departments, semesters, or tags for existing files.

Changes are reflected in the S3 bucket in real time.

Delete Files:

Outdated or irrelevant files can be deleted along with their metadata.
