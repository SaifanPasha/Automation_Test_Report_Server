from fastapi import FastAPI, Response, HTTPException, File, UploadFile, Form
import pandas as pd
from pydantic import BaseModel
import json
from datetime import datetime
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from fastapi.responses import FileResponse
import zipfile
import shutil

app = FastAPI()

app.add_middleware (
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Info(BaseModel):
    version: str
    description: str

@app.post("/upload/")
async def store_info(
    version: str = Form(...),
    description: str = Form(...),
    test_report_zip_file: UploadFile = File(...),
    test_case_file: UploadFile = File(...)
):
    # Generate a unique ID
    unique_id = str(uuid.uuid4())

    # Get the current date and time
    current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Create the folder structure
    upload_folder = "upload_data"
    unique_folder = os.path.join(upload_folder, unique_id)
    os.makedirs(unique_folder, exist_ok=True)

    # Save the uploaded test report CSV file
    test_case_file_name = "testCase.csv"
    test_case_file_location = os.path.join(unique_folder, test_case_file_name)
    with open(test_case_file_location, "wb") as f:
        f.write(await test_case_file.read())

    # Save the uploaded zip file temporarily
    zip_file_location = os.path.join(unique_folder, test_report_zip_file.filename)
    with open(zip_file_location, "wb") as f:
        f.write(await test_report_zip_file.read())

    # Create a temporary directory for extraction
    temp_extract_folder = os.path.join(unique_folder, "temp")
    os.makedirs(temp_extract_folder, exist_ok=True)

    # Extract the zip file into the temp directory
    with zipfile.ZipFile(zip_file_location, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_folder)
    
    # Remove the zip file after extraction
    os.remove(zip_file_location)

    # Get the list of items in the temp directory
    temp_items = os.listdir(temp_extract_folder)

    # If there's only one item and it's a directory (mainFolder), move its contents up
    if len(temp_items) == 1 and os.path.isdir(os.path.join(temp_extract_folder, temp_items[0])):
        main_folder = os.path.join(temp_extract_folder, temp_items[0])

        # Move all contents from main_folder to unique_folder
        for item in os.listdir(main_folder):
            src_path = os.path.join(main_folder, item)
            dest_path = os.path.join(unique_folder, item)

            if os.path.isfile(src_path) and src_path.endswith(".csv"):
                # Rename the CSV file to testCase.csv
                shutil.move(src_path, os.path.join(unique_folder, "testReport.csv"))
            else:
                shutil.move(src_path, dest_path)

        # Remove the now-empty main_folder
        os.rmdir(main_folder)
    else:
        # If no main folder, move everything from temp directly to unique_folder
        for item in temp_items:
            src_path = os.path.join(temp_extract_folder, item)
            dest_path = os.path.join(unique_folder, item)

            if os.path.isfile(src_path) and src_path.endswith(".csv"):
                # Rename the CSV file to testCase.csv
                shutil.move(src_path, os.path.join(unique_folder, "testReport.csv"))
            else:
                shutil.move(src_path, dest_path)

    # Remove the temp extraction folder
    shutil.rmtree(temp_extract_folder)

    # Create the data to be stored in JSON
    data = {
        "unique_id": unique_id,
        "version": version,
        "description": description,
        "date_time": current_datetime,
    }

    # Define the file path for storing the JSON data
    json_file_path = "data.json"

    # Check if the JSON file exists and read existing data
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # Append the new data to the existing data
    existing_data.append(data)

    # Write the updated data back to the JSON file
    with open(json_file_path, "w") as json_file:
        json.dump(existing_data, json_file, indent=4)

    return {"message": "Information stored successfully", "data": data}

@app.get("/getInfo/")
def get_info():
    json_file_path = "data.json"

    if not os.path.exists(json_file_path):
        raise HTTPException(status_code=404, detail="Data not found")

    with open(json_file_path, "r") as file:
        data = json.load(file)

    return data
        
@app.get("/get-testCase-data/{unique_id}/")
def get_testCase_csvFile(unique_id: str):
    upload_folder = "upload_data"
    file_type = "testCase"
    unique_folder = os.path.join(upload_folder, unique_id)
    
    # Check if the folder exists
    if not os.path.exists(unique_folder):
        raise HTTPException(status_code=404, detail="Unique ID not found.")
    
    # Find the CSV files in the folder
    csv_files = [f for f in os.listdir(unique_folder) if f.endswith('.csv')]
    
    # Filter based on file type ('testCase' or 'testReport')
    if file_type == "testCase":
        csv_file = next((f for f in csv_files if 'testCase' in f), None)
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'testCase'.")
    
    if not csv_file:
        raise HTTPException(status_code=404, detail=f"{file_type} CSV file not found.")
    
    # Path to the CSV file
    csv_file_path = os.path.join(unique_folder, csv_file)
    
    # Return the CSV file as a response
    return FileResponse(path=csv_file_path, media_type="text/csv", filename=csv_file)

@app.get("/get-testReport-data/{unique_id}")
def get_testReport_csvFile(unique_id: str):
    upload_folder = "upload_data"
    file_type = "testReport"
    unique_folder = os.path.join(upload_folder, unique_id)
    
    # Check if the folder exists
    if not os.path.exists(unique_folder):
        raise HTTPException(status_code=404, detail="Unique ID not found.")
    
    # Find the CSV files in the folder
    csv_files = [f for f in os.listdir(unique_folder) if f.endswith('.csv')]
    
    # Filter based on file type ('testCase' or 'testReport')
    if file_type == "testReport":
        csv_file = next((f for f in csv_files if 'testReport' in f), None)
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'testReport'.")
    
    if not csv_file:
        raise HTTPException(status_code=404, detail=f"{file_type} CSV file not found.")
    
    # Path to the CSV file
    csv_file_path = os.path.join(unique_folder, csv_file)
    
    # Return the CSV file as a response
    return FileResponse(path=csv_file_path, media_type="text/csv", filename=csv_file)


# @app.get("/download-image/{unique_id}/{folder}/{result_id}")
# async def download_image(unique_id: str, folder: str, result_id: str):
#     # Define the folder paths based on the folder (Actual_Result or Expected_Result)
#     folder_path = os.path.join('upload_data', unique_id, folder)

#     # Create file path for the image based on result_id
#     result_file = os.path.join(folder_path, f"{result_id}.bmp")

#     # Check if the image file exists
#     if not os.path.exists(result_file):
#         raise HTTPException(status_code=404, detail=f"Image '{result_id}.bmp' not found in {folder}")

#     # Return the image file
#     return FileResponse(result_file, media_type="image/bmp", filename=f"{result_id}.bmp")

@app.get("/download-actual-image/{unique_id}/Actual_Result/{result_id}")
async def download_actual_image(unique_id: str, result_id: str):
    folder = 'Actual_Result'
    folder_path = os.path.join('upload_data', unique_id, folder)

    # Create file path for the image based on result_id
    result_file = os.path.join(folder_path, f"{result_id}.bmp")

    # Check if the image file exists
    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail=f"Image '{result_id}.bmp' not found in {folder}")

    # Return the image file
    return FileResponse(result_file, media_type="image/bmp", filename=f"{result_id}.bmp")

@app.get("/download-expected-image/{unique_id}/Expected_Result/{result_id}")
async def download_expected_image(unique_id: str, result_id: str):
    folder = 'Expected_Result'
    folder_path = os.path.join('upload_data', unique_id, folder)

    # Create file path for the image based on result_id
    result_file = os.path.join(folder_path, f"{result_id}.bmp")

    # Check if the image file exists
    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail=f"Image '{result_id}.bmp' not found in {folder}")

    # Return the image file
    return FileResponse(result_file, media_type="image/bmp", filename=f"{result_id}.bmp")
    

# To run the FastAPI server, use the command: uvicorn <filename>:app --reload
