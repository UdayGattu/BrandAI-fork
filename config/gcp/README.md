# GCP Credentials Setup

This directory should contain your Google Cloud Platform service account credentials.

## Setup Instructions

### 1. Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Click **Create Service Account**
5. Give it a name (e.g., `brandai-service`)
6. Grant the following roles:
   - **Vertex AI User** (for Imagen 2 and Veo)
   - **Storage Object Viewer** (if using Cloud Storage)
   - **AI Platform Developer** (for Vertex AI APIs)

### 2. Download Credentials

1. Click on the created service account
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Download the JSON file

### 3. Place Credentials File

Place the downloaded JSON file in this directory with the name:
```
service-account.json
```

**Important:** 
- Never commit this file to Git (it's in `.gitignore`)
- Keep it secure and never share it publicly

### 4. Set Environment Variables

Create a `.env` file in the project root with:

```env
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_APPLICATION_CREDENTIALS=./config/gcp/service-account.json
```

### 5. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key and add it to your `.env` file

### 6. Test Setup

Run the test script:
```bash
python scripts/test_gcp_credentials.py
```

## File Structure

```
config/gcp/
├── README.md (this file)
├── .gitkeep (keeps directory in Git)
└── service-account.json (your credentials - NOT in Git)
```

## Troubleshooting

- **"Credentials file not found"**: Make sure `service-account.json` is in this directory
- **"Invalid credentials"**: Check that the JSON file is valid and not corrupted
- **"Vertex AI initialization failed"**: Verify your project ID and that Vertex AI API is enabled
- **"Gemini API failed"**: Check that your API key is correct and has quota available

