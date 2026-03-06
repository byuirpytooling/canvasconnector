from .make_client import CanvasClient
import polars as pl
import requests 
from bs4 import BeautifulSoup

def get_assignment_details(client: CanvasClient, course_id: int, assignment_id: int, details_only: bool = False):
    url = f"{client.canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}"
    
    params = {"include[]": "rubric"}
    response = requests.get(url, headers=client.headers, params=params)
    data = response.json()

    if details_only:
        return {
            "submission_types": data.get("submission_types"),
            "allowed_attempts": data.get("allowed_attempts"),
            "workflow_state": data.get("workflow_state"),
            "points_possible": data.get("points_possible"),
            "due_at": data.get("due_at"),
            "allowed_extensions": data.get("allowed_extensions") or [],  # add this
        }

    raw_description = data.get("description") or ""
    soup = BeautifulSoup(raw_description, "html.parser")

    links = [{"text": a.get_text(strip=True), "url": a.get("href")} 
            for a in soup.find_all("a") if a.get("href")]

    clean_description = soup.get_text(separator="\n").strip()
    clean_description = clean_description.replace("\xa0", " ")
    clean_description = "\n".join(
        line for line in clean_description.splitlines()
        if line.strip() and line.strip() != "Links to an external site."
    )
    
    return {
        "name": data.get("name"),
        "description": clean_description,
        "links": links,
        "rubric": data.get("rubric") or [],
        "due_at": data.get("due_at"),
        "points_possible": data.get("points_possible"),
        "submission_types": data.get("submission_types"),
        "allowed_attempts": data.get("allowed_attempts"),
        "workflow_state": data.get("workflow_state"),
    }

def _upload_file(client: CanvasClient, course_id: int, assignment_id: int, 
                 file_path: str, allowed_extensions: list[str] = None):
    import os
    
    # Validate file exists
    if not os.path.exists(file_path):
        raise Exception(f"File not found: {file_path}")
    
    # Validate extension if restricted
    if allowed_extensions:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in allowed_extensions:
            raise Exception(f"File type {ext} not allowed. Must be one of: {allowed_extensions}")
    
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    # Step 1 - Request upload URL
    upload_url = f"{client.canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/self/files"
    upload_request = requests.post(upload_url, headers=client.headers, json={
        "name": file_name,
        "size": file_size,
    })
    
    if upload_request.status_code != 200:
        raise Exception(f"Failed to request upload URL: {upload_request.status_code}: {upload_request.text}")
    
    upload_data = upload_request.json()
    
    # Step 2 - Upload file bytes
    with open(file_path, "rb") as f:
        upload_response = requests.post(
            upload_data["upload_url"],
            data=upload_data["upload_params"],
            files={"file": f}
        )
    
    if upload_response.status_code not in (200, 201, 301, 302):
        raise Exception(f"Failed to upload file: {upload_response.status_code}: {upload_response.text}")
    
    # Step 3 - Return file_id
    file_id = upload_response.json().get("id")
    if not file_id:
        raise Exception("Upload succeeded but no file_id returned.")
    
    print(f"✓ File uploaded successfully: {file_name}")
    return file_id


def submit_assignment(client: CanvasClient, course_id: int, assignment_id: int, 
                      body: str = None, submission_url: str = None, file_path: str = None):
    details = get_assignment_details(client, course_id, assignment_id, details_only=True)
    submission_type = details["submission_types"][0]
    allowed_extensions = details.get("allowed_extensions") or []
    endpoint = f"{client.canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions"
    
    if submission_type == "online_quiz":
        raise Exception("Quiz submissions must be completed through the Canvas UI.")
    
    elif submission_type == "online_text_entry":
        if not body:
            raise Exception("body is required for text entry assignments.")
        payload = {
            "submission": {
                "submission_type": "online_text_entry",
                "body": body
            }
        }
    
    elif submission_type == "online_url":
        if not submission_url:
            raise Exception("submission_url is required for URL assignments.")
        payload = {
            "submission": {
                "submission_type": "online_url",
                "url": submission_url
            }
        }
    
    elif submission_type == "online_upload":
        if not file_path:
            raise Exception("file_path is required for file upload assignments.")
        extensions = [f".{ext}" for ext in allowed_extensions] if allowed_extensions else None
        file_id = _upload_file(client, course_id, assignment_id, file_path, allowed_extensions=extensions)
        payload = {
            "submission": {
                "submission_type": "online_upload",
                "file_ids": [file_id]
            }
        }
    
    elif submission_type in ("none", "not_graded"):
        raise Exception("This assignment does not require a submission.")

    elif submission_type in ("media_recording", "student_annotation", "external_tool"):
        raise Exception("This submission type is not supported. Please submit through the Canvas UI.")
    
    else:
        raise Exception(f"Unsupported submission type: {submission_type}")
    
    response = requests.post(endpoint, headers=client.headers, json=payload)
    
    if response.status_code == 201:
        print("✓ Assignment submitted successfully")
        return True
    else:
        raise Exception(f"Failed to submit: {response.status_code}: {response.text}")