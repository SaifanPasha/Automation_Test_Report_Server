# Automation_Test_Report_Server

FastAPI server for managing automation test reports and metadata.

## Running the FastAPI Server

1. **Clone the Repository**
   - Run the following command to clone the repository:
     ```sh
     git clone https://github.com/SaifanPasha/Automation_Test_Report_Server.git
     ```

2. **Create a Virtual Environment**
   - Set up a virtual environment:
     ```sh
     python -m venv venv
     ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

4. **Install Dependencies**
   - Install the required packages:
     ```sh
     pip install -r requirements.txt
     ```

5. **Start the FastAPI Server**
   - Run the server with Uvicorn:
     ```sh
     uvicorn main:app --reload
     ```

## API Endpoints

1. **Upload Files**
   - **Endpoint:** `/upload/`
   - **Method:** POST
   - **Description:** Uploads a test report zip file and a test case CSV file. The zip file is extracted, and the contents are organized. Metadata is stored in a JSON file.
   - **Required Form Data:**
     - `version` (string)
     - `description` (string)
     - `test_report_zip_file` (file)
     - `test_case_file` (file)

2. **Get Metadata**
   - **Endpoint:** `/getInfo/`
   - **Method:** GET
   - **Description:** Retrieves all stored metadata from the JSON file.

3. **Get Test Case CSV File**
   - **Endpoint:** `/get-testCase-data/{unique_id}/`
   - **Method:** GET
   - **Description:** Returns the test case CSV file for a given unique ID.

4. **Get Test Report CSV File**
   - **Endpoint:** `/get-testReport-data/{unique_id}`
   - **Method:** GET
   - **Description:** Returns the test report CSV file for a given unique ID.

5. **Download Actual Result Image**
   - **Endpoint:** `/download-actual-image/{unique_id}/Actual_Result/{result_id}`
   - **Method:** GET
   - **Description:** Downloads the actual result image for a given unique ID and result ID.

6. **Download Expected Result Image**
   - **Endpoint:** `/download-expected-image/{unique_id}/Expected_Result/{result_id}`
   - **Method:** GET
   - **Description:** Downloads the expected result image for a given unique ID and result ID.

### References
1. [FastAPI Documentation](https://fastapi.tiangolo.com/)
2. [Uvicorn Documentation](https://www.uvicorn.org/)
