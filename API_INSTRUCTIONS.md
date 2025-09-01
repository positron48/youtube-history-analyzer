# YouTube Data API v3 Setup Instructions

> 🌍 **Language versions**: [🇷🇺 Русский](API_INSTRUCTIONS_ru.md) | [🇺🇸 English](API_INSTRUCTIONS.md)

## Step 1: Create Project in Google Cloud Console

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Sign in to your Google account
3. Create a new project or select existing one
4. Give the project a clear name (e.g., "YouTube History Analyzer")

## Step 2: Enable YouTube Data API v3

1. In the left menu, select "APIs & Services" → "Library"
2. Find "YouTube Data API v3" in search
3. Click on the API and click "Enable"

## Step 3: Create API Key

1. In the left menu, select "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API key"
3. Copy the created API key

## Step 4: Configure Restrictions (Optional)

1. Click on the created API key
2. In "Application restrictions" section, select "HTTP referrers"
3. Add domains from which the API will be used
4. In "API restrictions" section, select "Restrict key"
5. Select only "YouTube Data API v3"

## Step 5: Create API Key File

1. Create `youtube_api_key.txt` file in the project folder
2. Paste your API key into it (without quotes and extra characters)
3. Save the file

## Example youtube_api_key.txt content:
```
AIzaSyB1234567890abcdefghijklmnopqrstuvwxyz
```

## Important Notes:

- **Security**: Never publish API key in public access
- **Limits**: YouTube Data API v3 allows up to 10,000 requests per day for free
- **Quota**: This is sufficient for most users
- **Monitoring**: In Google Cloud Console you can track API usage

## Verification:

After setting up the API key, launch the analyzer and select the option to get video duration. If everything is configured correctly, you will see the message "✓ Using YouTube Data API v3".

## Troubleshooting:

- **403 Forbidden**: Check API key correctness and API enabling
- **400 Bad Request**: Check request format
- **Quota exceeded**: Daily request limit reached (wait until next day)

## Alternatives:

If you have problems with the API, you can:
1. Use another Google account
2. Create a new project
3. Contact Google Cloud Support
