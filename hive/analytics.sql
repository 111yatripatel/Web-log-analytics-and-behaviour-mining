-- ============================================================================
-- Distributed Analytical Queries over HDFS Web Logs
-- ============================================================================

USE web_log_analytics;

-- 1. Total Requests
SELECT COUNT(*) AS total_requests FROM web_logs;

-- 2. HTTP Status Code Distribution
SELECT status, COUNT(*) AS count, ROUND(COUNT(*) * 100.0 / 3461612, 2) AS percentage
FROM web_logs
GROUP BY status
ORDER BY count DESC;

-- 3. Top 20 Requested URLs
SELECT url, COUNT(*) AS request_count
FROM web_logs
GROUP BY url
ORDER BY request_count DESC
LIMIT 20;

-- 4. HTTP Methods Distribution
SELECT method, COUNT(*) AS method_count
FROM web_logs
GROUP BY method
ORDER BY method_count DESC;

-- 5. Total Response Bytes Transferred
SELECT SUM(response_bytes) AS total_bytes FROM web_logs;

-- 6. Average Response Bytes per Request
SELECT ROUND(AVG(response_bytes), 2) AS avg_bytes FROM web_logs;

-- 7. Overall Error Rate (Status >= 400)
SELECT 
    COUNT(*) AS total_requests,
    SUM(CASE WHEN status >= 400 THEN 1 ELSE 0 END) AS error_requests,
    ROUND(SUM(CASE WHEN status >= 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 4) AS error_rate_percent
FROM web_logs;

-- 8. Status Class Distribution (2xx, 3xx, 4xx, 5xx)
SELECT 
    CASE 
        WHEN status >= 200 AND status < 300 THEN '2xx Success'
        WHEN status >= 300 AND status < 400 THEN '3xx Redirection'
        WHEN status >= 400 AND status < 500 THEN '4xx Client Error'
        WHEN status >= 500 AND status < 600 THEN '5xx Server Error'
        ELSE 'Other'
    END AS status_class,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / 3461612, 2) AS percentage
FROM web_logs
GROUP BY 
    CASE 
        WHEN status >= 200 AND status < 300 THEN '2xx Success'
        WHEN status >= 300 AND status < 400 THEN '3xx Redirection'
        WHEN status >= 400 AND status < 500 THEN '4xx Client Error'
        WHEN status >= 500 AND status < 600 THEN '5xx Server Error'
        ELSE 'Other'
    END
ORDER BY count DESC;

-- 9. Requests Per Hour (Sample aggregated traffic pattern)
SELECT 
    SUBSTR(log_time, 13, 2) AS hour_of_day,
    COUNT(*) AS requests
FROM web_logs
GROUP BY SUBSTR(log_time, 13, 2)
ORDER BY hour_of_day;

-- 10. Errors Per Hour
SELECT 
    SUBSTR(log_time, 13, 2) AS hour_of_day,
    COUNT(*) AS error_count
FROM web_logs
WHERE status >= 400
GROUP BY SUBSTR(log_time, 13, 2)
ORDER BY hour_of_day;

-- 11. Top Error URLs (4xx / 5xx)
SELECT url, status, COUNT(*) AS error_count
FROM web_logs
WHERE status >= 400
GROUP BY url, status
ORDER BY error_count DESC
LIMIT 20;

-- 12. Largest Responses
SELECT url, status, response_bytes
FROM web_logs
ORDER BY response_bytes DESC
LIMIT 10;

-- 13. Request Volume by Method and Status
SELECT method, status, COUNT(*) AS count
FROM web_logs
GROUP BY method, status
ORDER BY count DESC;
