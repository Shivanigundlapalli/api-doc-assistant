# API Error Codes

When interacting with the API, you may encounter error codes. All error responses are returned in JSON format and include a `code` and `message` to help you troubleshoot.

## 400 Bad Request
The request was invalid or cannot be otherwise served. An exact error message will be provided in the response body. 
**Fix:** Validate your request parameters against the documentation before retrying.

## 401 Unauthorized
You have failed to provide a valid API key in the `Authorization` header.
**Fix:** Ensure you are passing the header `Authorization: Bearer YOUR_API_KEY` and that your API key is active in your dashboard.

## 403 Forbidden
Your API key is valid, but you do not have the required permissions to access the requested resource.
**Fix:** Check your account roles and permissions. If you need elevated access, contact your administrator.

## 404 Not Found
The requested resource does not exist.
**Fix:** Double-check the URL path, endpoint spelling, and ensure the resource ID you are requesting is correct.

## 429 Too Many Requests
You have exceeded your API rate limit.
**Fix:** Read the `Retry-After` header in the response and wait the specified number of seconds before making another request.

## 500 Internal Server Error
An unexpected error occurred on our end.
**Fix:** Try the request again later. If the issue persists, check our status page or contact support.
