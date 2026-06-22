# Authentication Guide

Authentication requires an API key.

## Generating an API Key

1. Log in to the dashboard.
2. Navigate to Settings.
3. Click API Keys.
4. Generate a new API key.

## Expiration Policy

API keys expire after 90 days.

## Using the API Key

Include the key in the Authorization header.

Example:

Authorization: Bearer YOUR_API_KEY

## Error Codes

401 Unauthorized:
Occurs when the API key is invalid or expired.

403 Forbidden:
Occurs when the user does not have sufficient permissions.