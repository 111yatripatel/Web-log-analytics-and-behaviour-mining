# NASA HTTP Server Log Dataset

## Source & Overview
This dataset contains two months of real HTTP server access logs from the NASA Kennedy Space Center WWW server in Florida.
It originates from the Internet Traffic Archive (ITA) and represents real-world distributed web traffic:
- `data/raw/NASA_access_log_Jul95`: All requests logged from 00:00:00 July 1, 1995 through 23:59:59 July 31, 1995.
- `data/raw/NASA_access_log_Aug95`: All requests logged from 00:00:00 August 1, 1995 through 23:59:59 August 31, 1995.

## Raw Format (Common Log Format variant)
Each line represents an HTTP access request:
```text
<host> - - [<timestamp>] "<request_method> <url> <protocol>" <status_code> <response_bytes>
```

### Example Record:
```text
unicomp6.unicomp.net - - [01/Jul/1995:00:00:06 -0400] "GET /shuttle/countdown/ HTTP/1.0" 200 3985
```

### Fields:
1. **Host**: Remote hostname or IPv4 address of the client making the request.
2. **Identd / User ID**: Two hyphens (`- -`), unused/unauthenticated.
3. **Timestamp**: Format `[DD/Mon/YYYY:HH:MM:SS -0400]` (US Eastern Daylight Time).
4. **HTTP Request**: Quoted string containing:
   - Method (`GET`, `POST`, `HEAD`, etc.)
   - URL path (`/shuttle/countdown/`)
   - Protocol (`HTTP/1.0`)
5. **HTTP Status Code**: Standard 3-digit status code (`200`, `304`, `404`, `500`, etc.).
6. **Response Bytes**: Number of bytes transferred in the response body. If no bytes were sent (e.g. 304 Not Modified, redirects, or errors), this may be represented as `-` or `0`.

## Real-World Edge Cases Handled in Preprocessing:
- Missing response bytes (`-` mapped to `0`).
- Malformed HTTP request strings (e.g. quotes missing, truncated requests, requests without methods or protocols).
- Non-standard characters and mixed encodings (handled via `latin-1` / `utf-8` fallback with `errors='replace'`).
- Incomplete log lines.
