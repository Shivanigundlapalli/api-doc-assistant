# API Rate Limits

To ensure fair usage and platform stability, our API enforces rate limits based on your subscription tier. Limits are applied per API key and IP address.

## Standard Limits

| Plan       | Requests / Minute | Requests / Day |
|------------|-------------------|----------------|
| Free       | 100               | 10,000         |
| Pro        | 1,000             | 500,000        |
| Enterprise | Custom            | Custom         |

## Response Headers

Every successful API response includes the following HTTP headers to help you track your usage in real-time:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the current time window.
- `X-RateLimit-Remaining`: The number of requests remaining in the current time window.
- `X-RateLimit-Reset`: The exact time (in UTC epoch seconds) when your rate limit window resets.

## When Limits Are Exceeded

If you exceed your rate limit, the API will reject your request and return a `429 Too Many Requests` HTTP status code. 

### Error Response Example

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded your rate limit.",
    "retry_after": 45
  }
}
```

### The Retry-After Header

In addition to the standard rate limit headers, a `429` response will include a `Retry-After` header. This indicates the number of seconds you must wait before making another request.

Example:
`Retry-After: 45`

You must wait the specified number of seconds to avoid being temporarily blocked.
