# GitHub Webhook Activity Tracker

## 📌 Project Overview
This project is a full-stack application designed to capture GitHub repository activity via Webhooks, store essential event data in MongoDB, and display recent activity on a UI that updates automatically every 15 seconds. It handles **PUSH**, **PULL_REQUEST**, and **MERGE** events.

## 🧩 Architecture
- **Backend**: Flask (Python)
    - Receives Webhook events at `/webhook/receiver`.
    - Parses payloads to extract only required fields (`request_id`, `author`, `action`, `from_branch`, `to_branch`, `timestamp`).
    - Connects to MongoDB (Atlas or Local) to store events.
    - Exposes `GET /events` for the UI.
- **Database**: MongoDB
    - Stores events with a strict schema.
- **Frontend**: HTML/CSS/JavaScript
    - Polls `/events` every 15 seconds.
    - Displays formatted activity messages.

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB (Local or Atlas connection string)
- `ngrok` (for local webhook testing)

### Installation
1. **Clone the repository** (if not already done).
2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Configure Environment**:
    Create a `.env` file in the root directory:
    ```bash
    # For Local MongoDB
    MONGO_URI=mongodb://localhost:27017/webhook_db
    
    # OR for MongoDB Atlas
    # MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/webhook_db?retryWrites=true&w=majority
    ```

### Running the Application
1. Start the server:
    ```bash
    python app.py
    ```
2. The application runs on `http://localhost:5000`.

## 🔐 GitHub Webhook Configuration
To connect a GitHub repository (`action-repo`) to this backend:

1. **Expose Local Server**:
    If running locally, use ngrok to create a public URL:
    ```bash
    ngrok http 5000
    ```
2. **Add Webhook in GitHub**:
    - Go to **Settings** > **Webhooks** > **Add webhook** in your `action-repo`.
    - **Payload URL**: `https://<your-ngrok-url>/webhook/receiver`
    - **Content type**: `application/json`
    - **Events**: Select "Just the push event" and "Pull requests".
    - Save the webhook.

## 🧪 Testing End-to-End

### 1. Manual Testing (cURL)
You can verify the system without an actual GitHub repo using these commands:

**Push Event:**
```bash
curl -X POST http://localhost:5000/webhook/receiver \
-H "Content-Type: application/json" \
-H "X-GitHub-Event: push" \
-d '{
  "ref": "refs/heads/feature-branch",
  "after": "a1b2c3d4",
  "pusher": { "name": "DevUser" }
}'
```

**Pull Request Opened:**
```bash
curl -X POST http://localhost:5000/webhook/receiver \
-H "Content-Type: application/json" \
-H "X-GitHub-Event: pull_request" \
-d '{
  "action": "opened",
  "pull_request": {
    "id": 42,
    "user": { "login": "PR_Author" },
    "head": { "ref": "feature-branch" },
    "base": { "ref": "main" }
  }
}'
```

**Merge Event (Simulated):**
```bash
curl -X POST http://localhost:5000/webhook/receiver \
-H "Content-Type: application/json" \
-H "X-GitHub-Event: pull_request" \
-d '{
  "action": "closed",
  "sender": { "login": "MergeMaster" },
  "pull_request": {
    "id": 42,
    "user": { "login": "PR_Author" },
    "head": { "ref": "feature-branch" },
    "base": { "ref": "main" },
    "merged": true
  }
}'
```

### 2. Verify UI
- Open `http://localhost:5000`.
- Verify that the events appear in the list within 15 seconds.
- Format should match: `DevUser pushed to feature-branch on 29th January 2026 - 10:00 PM UTC`.

## 📦 Submission Links
- **Action Repo**: [Link to your action-repo]
- **Webhook Repo**: [Link to this repo]
