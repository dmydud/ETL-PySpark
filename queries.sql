-- Query 1: Count the number of users per signup date (limit 10 results for output)
SELECT signup_date, COUNT(*) AS user_count
FROM users
GROUP BY signup_date 
ORDER BY signup_date DESC
LIMIT 10;  -- Limit to 10 results for output

-- Query 2: Get the distinct domains from the users table (limit 10 results for output)
SELECT DISTINCT "domain"
FROM users
LIMIT 10;  -- Limit to 10 results for output

-- Query 3: Get user details from the last 7 days (limit 10 results for output)
SELECT user_id, name, email, signup_date, "domain"
FROM users
WHERE signup_date >= CURRENT_DATE - interval '7 days'
LIMIT 10;  -- Limit to 10 results for output

-- Query 4: Get the user_id of users with the most common domain (limit 10 results for output)
SELECT user_id
FROM users
WHERE "domain" = (
	SELECT "domain" 
	FROM users
	GROUP BY "domain" 
	ORDER BY COUNT(user_id) desc 
	LIMIT 1
)
LIMIT 10;  -- Limit to 10 results for output

-- Query 5: Delete users whose domain is not in the specified list
DELETE FROM users 
WHERE "domain" NOT IN ('gmail.com', 'yahoo.com', 'example.com');
