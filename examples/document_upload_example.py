"""Example client code for testing document upload and chat integration."""

import os
import asyncio
import json
import requests
import websockets


API_BASE = "http://localhost:8100/api/v1"
WS_URL = "ws://localhost:8100/api/v1/chat"


def upload_resume(file_path: str) -> str:
    """Upload a resume and get document ID."""
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_BASE}/upload/resume", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Resume uploaded: {data['filename']}")
        print(f"  Document ID: {data['document_id']}")
        print(f"  Text length: {data['text_length']} chars")
        return data["document_id"]
    else:
        print(f"✗ Upload failed: {response.text}")
        return None


def upload_jd(file_path: str) -> str:
    """Upload a job description and get document ID."""
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_BASE}/upload/job_description", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✓ JD uploaded: {data['filename']}")
        print(f"  Document ID: {data['document_id']}")
        return data["document_id"]
    else:
        print(f"✗ Upload failed: {response.text}")
        return None


def paste_jd(text: str) -> str:
    """Paste JD text and get document ID."""
    data = {"text": text, "doc_type": "job_description", "filename": "pasted_jd.txt"}
    response = requests.post(f"{API_BASE}/upload/text", json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Text uploaded: {result['filename']}")
        print(f"  Document ID: {result['document_id']}")
        return result["document_id"]
    else:
        print(f"✗ Upload failed: {response.text}")
        return None


async def chat_with_documents(resume_id: str = None, jd_id: str = None):
    """Connect to WebSocket and chat with document context."""
    async with websockets.connect(WS_URL) as websocket:
        print(f"\n✓ Connected to WebSocket")

        # Example 1: Chat with just resume
        if resume_id and not jd_id:
            message = {"message": "Can you review this resume?", "resume_id": resume_id}
            await websocket.send(json.dumps(message))
            print(f"\n→ Sent: Review resume request")

        # Example 2: Chat with resume and JD
        elif resume_id and jd_id:
            message = {
                "message": "Calculate the fit score for this candidate",
                "resume_id": resume_id,
                "jd_id": jd_id,
            }
            await websocket.send(json.dumps(message))
            print(f"\n→ Sent: Fit score request")

        # Example 3: Plain text message
        else:
            await websocket.send("Hello! What can you do?")
            print(f"\n→ Sent: Plain text message")

        # Receive response
        print(f"\n← Response:")
        try:
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                print(response, end="", flush=True)
        except asyncio.TimeoutError:
            print("\n\n✓ Response complete")


# Example usage
if __name__ == "__main__":
    print("=== Document Upload & Chat Integration Example ===\n")

    # Example 1: Upload files and chat
    print("Example 1: Upload resume and JD files")
    print("-" * 50)

    current_file_path = os.path.dirname(os.path.abspath(__file__))

    resume_id = upload_resume(os.path.join(current_file_path, "test_resume.pdf"))
    jd_id = upload_jd(os.path.join(current_file_path, "test_jd.txt"))

    if resume_id and jd_id:
        asyncio.run(chat_with_documents(resume_id, jd_id))

    print("\n" + "=" * 50 + "\n")

    # Example 2: Paste JD text
    print("Example 2: Paste JD text")
    print("-" * 50)
    jd_text = """
    We are looking for a Senior Python Developer with 5+ years of experience.
    Required skills: Python, FastAPI, PostgreSQL, Docker.
    """
    jd_id = paste_jd(jd_text)

    print("\n" + "=" * 50)
