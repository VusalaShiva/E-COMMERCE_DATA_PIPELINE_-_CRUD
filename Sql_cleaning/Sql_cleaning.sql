-- Step 1.1: Create the Database (if it doesn't exist)
CREATE DATABASE IF NOT EXISTS ecommerce_project;
USE ecommerce_project;

-- Step 1.2: Create the staging table for raw data
CREATE TABLE raw_orders (
    Order_ID VARCHAR(50),
    Order_Date VARCHAR(50),
    Customer_ID VARCHAR(50),
    Region VARCHAR(50),
    Payment_Method VARCHAR(50),
    Revenue VARCHAR(50),
    Quantity VARCHAR(50),
    Email VARCHAR(100)
);

-- Phase 2: Data Profiling (MySQL)
-- Run the following SQL queries to profile your raw_orders table and identify the scope of the cleaning needed.

-- 1. Identify NULL / Missing Values
-- This query uses SUM with CASE to count how many rows have missing data in key columns. Remember, some of your "missing" 
-- values may be the string 'NULL' or 'NA' from the Python generation script, which a simple IS NULL will not catch (you'll check for those in Step 5).
SELECT
    COUNT(*) AS Total_Records,
    SUM(CASE WHEN Customer_ID IS NULL OR Customer_ID = '' THEN 1 ELSE 0 END) AS Missing_Customer_IDs,
    SUM(CASE WHEN Region IS NULL OR Region = '' THEN 1 ELSE 0 END) AS Missing_Regions,
    SUM(CASE WHEN Revenue IS NULL OR Revenue = '' THEN 1 ELSE 0 END) AS Missing_Revenues
FROM
    raw_orders;
    
-- 2. Identify Duplicate Order IDs
-- This query is crucial for finding the duplicate transactions you intentionally injected.
SELECT
    Order_ID,
    COUNT(*) AS Duplicate_Count
FROM
    raw_orders
GROUP BY
    Order_ID
HAVING
    COUNT(*) > 1
ORDER BY
    Duplicate_Count DESC;

-- 3. Identify Textual Inconsistencies (Standardization)
-- Check the categorical column Payment_Method for variations in case, spacing, and abbreviations (e.g., 'UPI', 'upi', 'U.P.I.').

SELECT DISTINCT
    Payment_Method
FROM
    raw_orders
ORDER BY
    Payment_Method;
    
-- 4. Identify Invalid Date Formats
-- We check for records where the Order_Date is clearly not in the standard YYYY-MM-DD format (which is required for proper date conversion).

-- This query uses REGEXP to find dates that don't look like YYYY-MM-DD
-- Note: MySQL's STR_TO_DATE() or TRY_CONVERT() is often a better cleaning tool, 
-- but this profiling query helps identify the bad records.
SELECT
    Order_ID,
    Order_Date
FROM
    raw_orders
WHERE
    Order_Date NOT REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
LIMIT 10;

-- 5. Identify Incorrect Data Types (Non-Numeric and String NULLs/NAs)
-- This query attempts to find text that was incorrectly inserted into the Revenue and Quantity columns.
SELECT
    COUNT(*) AS Non_Numeric_Revenue_Count
FROM
    raw_orders
WHERE
    Revenue REGEXP '[^0-9.]'  -- Finds records with characters other than digits or a decimal point
    OR UPPER(Revenue) IN ('NULL', 'NA', 'ZERO', 'FORTY', 'THIRTY-FIVE'); -- Finds the explicit text errors
SELECT
    COUNT(*) AS Non_Numeric_Quantity_Count
FROM
    raw_orders
WHERE
    Quantity REGEXP '[^0-9]' -- Finds records with characters other than digits
    OR UPPER(Quantity) IN ('ONE', 'TWO', 'FIVE', '100+'); -- Finds the explicit text errors
    
-- 6. Identify Invalid Email Addresses
-- This query uses a basic regular expression to flag emails that are missing the common structure (@ and a .).

SELECT
    COUNT(*) AS Invalid_Email_Count
FROM
    raw_orders
WHERE
    Email NOT REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';

-- Yes, absolutely. Cleaning step-by-step is the best way to ensure data quality and track your progress.

-- We'll use your current script as a foundation, executing the cleaning logic one major issue at a time on the data inserted into the final table.

-- Here is the step-by-step plan for Phase 3: Data Cleaning and Transformation (MySQL).

-- Phase 3: Data Cleaning Step-by-Step
-- Setup: Create the Final Clean Table
-- First, define the clean structure where the processed data will reside. We'll use this table to insert the data after each cleaning pass.

-- SQL

USE ecommerce_project;

-- 1. Drop and Create the final table with correct data types and constraints
DROP TABLE IF EXISTS clean_orders;

CREATE TABLE clean_orders (
    Order_ID INT PRIMARY KEY NOT NULL, 
    Order_Date DATE NOT NULL,          
    Customer_ID VARCHAR(50) NOT NULL,
    Region VARCHAR(50) NOT NULL,
    Payment_Method VARCHAR(50) NOT NULL, 
    Revenue DECIMAL(10, 2) NOT NULL,     
    Quantity INT NOT NULL,               
    Email VARCHAR(100)
);

-- IMPORTANT: Create a temporary table to hold the data as we clean it.
-- This is cleaner than multiple inserts/updates. We start by inserting ALL raw data.
DROP TABLE IF EXISTS temp_cleaned_data;

CREATE TABLE temp_cleaned_data AS
SELECT 
    Order_ID, Order_Date, Customer_ID, Region, Payment_Method, Revenue, Quantity, Email
FROM raw_orders;

ALTER TABLE temp_cleaned_data ADD COLUMN rn INT;
-- Step 1: Handle Duplicates (De-duplication)
-- We must ensure that each Order_ID is unique before inserting into the final table, which requires Order_ID to be a primary key. We'll keep the first record found for each duplicate set.

-- SQL
SET SQL_SAFE_UPDATES = 0;
-- 2. Identify and remove duplicate records (keeping the first one found)
WITH RankedOrders AS (
    SELECT
        Order_ID,
        ROW_NUMBER() OVER (PARTITION BY Order_ID ORDER BY Order_Date) as row_num -- Rank based on Order_ID
    FROM temp_cleaned_data
)
DELETE T1
FROM temp_cleaned_data T1
INNER JOIN RankedOrders RO
    ON T1.Order_ID = RO.Order_ID
WHERE 
    RO.row_num > 1;

SELECT COUNT(*) AS Records_After_Deduplication FROM temp_cleaned_data;
-- Step 2: Clean and Format Dates
-- Convert all different date string formats (MM/DD/YYYY, DD-MM-YY) into the standard MySQL DATE type (YYYY-MM-DD).

-- SQL

-- 3. Standardize Order_Date
UPDATE temp_cleaned_data
SET Order_Date = 
    CASE
        -- Case 1: Handle MM/DD/YYYY format
        WHEN Order_Date REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$' THEN STR_TO_DATE(Order_Date, '%m/%d/%Y')
        -- Case 2: Handle DD-MM-YY format
        WHEN Order_Date REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{2}$' THEN STR_TO_DATE(Order_Date, '%d-%m-%y')
        -- Case 3: Assume YYYY-MM-DD (standard) for all others, using STR_TO_DATE for safety
        ELSE STR_TO_DATE(Order_Date, '%Y-%m-%d')
    END
WHERE 
    Order_Date IS NOT NULL AND TRIM(Order_Date) != '';

-- Check the dates (Optional validation step)
SELECT DISTINCT Order_Date FROM temp_cleaned_data LIMIT 5;
-- -----------------------------------------------------------------------------
-- Step 3 (Corrected): Standardize Categorical Text (Payment Method, Region)
-- We must use standard functions as INITCAP() does not exist in MySQL.
-- -----------------------------------------------------------------------------

-- 4. Standardize Payment_Method (Capitalize first letter, replace non-standard characters)
-- Replaces INITCAP with CONCAT(UPPER(LEFT(..., 1)), LOWER(SUBSTRING(..., 2)))
UPDATE temp_cleaned_data
SET Payment_Method = 
    REPLACE(
        CONCAT(
            UPPER(LEFT(TRIM(Payment_Method), 1)), -- Capitalize the very first letter
            LOWER(SUBSTRING(TRIM(Payment_Method), 2)) -- Lowercase the rest of the string
        ), 
    '.', ' '
    )
WHERE 
    Payment_Method IS NOT NULL AND TRIM(Payment_Method) != '';

-- If you need to capitalize every word (e.g., 'cash on delivery' -> 'Cash On Delivery'), 
-- you may need to define a Stored Function or use Python/Pandas for this step.
-- For simple standardization, the above script is highly effective.

-- 5. Clean up Region (Handling both true NULLs and string 'NULL'/'NA' values)
UPDATE temp_cleaned_data
SET Region = 
    CASE
        -- Condition 1: Handle true SQL NULL
        WHEN Region IS NULL THEN 'UNKNOWN' 
        -- Condition 2: Handle string representations of NULL/missing data
        WHEN UPPER(TRIM(Region)) IN ('NULL', 'NA', '') THEN 'UNKNOWN'
        ELSE TRIM(Region)
    END;

-- Verification: Check to see if any true NULLs remain (should be 0)
SELECT COUNT(*) FROM temp_cleaned_data WHERE Region IS NULL;

-- 6. Fill Missing Customer_ID
UPDATE temp_cleaned_data
SET Customer_ID = 'CUST-UNKNOWN'
WHERE Customer_ID IS NULL OR TRIM(Customer_ID) = '';

-- Check the standardization (Optional validation step)
SELECT DISTINCT Payment_Method FROM temp_cleaned_data ORDER BY 1 LIMIT 5;


-- Step 4: Clean Non-Numeric Data Types (Revenue and Quantity)
-- Convert textual representations of numbers into actual numeric values (DECIMAL or INT).

-- SQL

-- 7. Clean Revenue (Handle text and set to 0.00 if non-convertible)
UPDATE temp_cleaned_data
SET Revenue = 
    CASE
        WHEN UPPER(Revenue) IN ('NA', 'ZERO', 'NULL') THEN '0.00'
        WHEN UPPER(Revenue) = 'FORTY' THEN '40.00'
        WHEN UPPER(Revenue) = 'THIRTY-FIVE' THEN '35.00'
        -- If it contains non-numeric characters (and wasn't caught above), set to 0
        WHEN Revenue REGEXP '[^0-9.]' THEN '0.00' 
        ELSE Revenue
    END
WHERE 
    Revenue IS NOT NULL;


-- 8. Clean Quantity (Handle text and set to 0 if non-convertible)
UPDATE temp_cleaned_data
SET Quantity = 
    CASE
        WHEN UPPER(Quantity) IN ('NA', 'NULL') THEN '0'
        WHEN UPPER(Quantity) = 'ONE' THEN '1'
        WHEN UPPER(Quantity) = 'TWO' THEN '2'
        WHEN UPPER(Quantity) = 'FIVE' THEN '5'
        WHEN Quantity = '100+' THEN '100' 
        WHEN Quantity REGEXP '[^0-9]' THEN '0'
        ELSE Quantity
    END
WHERE 
    Quantity IS NOT NULL;

-- Check the numeric data (Optional validation step)
SELECT Order_ID, Revenue, Quantity FROM temp_cleaned_data WHERE CAST(Revenue AS DECIMAL(10,2)) <= 0 LIMIT 5;
-- Step 5: Final Load into Clean Table
-- Finally, insert the completely cleaned data from the temporary table into the final clean_orders table, using CAST to ensure the final data types match the schema.

-- SQL

-- 9. Final Insertion (Casting to enforce data types and constraints)
INSERT INTO clean_orders (
    Order_ID, 
    Order_Date, 
    Customer_ID, 
    Region, 
    Payment_Method, 
    Revenue, 
    Quantity, 
    Email
)
SELECT
    CAST(Order_ID AS SIGNED) AS Order_ID,
    CAST(Order_Date AS DATE) AS Order_Date,
    Customer_ID,
    Region,
    Payment_Method,
    CAST(Revenue AS DECIMAL(10, 2)) AS Revenue,
    CAST(Quantity AS SIGNED) AS Quantity,
    CASE
        WHEN Email NOT REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' THEN NULL
        ELSE Email
    END AS Email
FROM
    temp_cleaned_data;

-- 10. Verification
SELECT 
    COUNT(*) AS Total_Final_Clean_Records,
    MIN(Order_Date) AS First_Order,
    MAX(Revenue) AS Max_Revenue
FROM 
    clean_orders;

-- 11. Cleanup (Remove the temporary table)
DROP TABLE temp_cleaned_data;
-- Now you have a fully cleaned and structured clean_orders table, ready for analytics and reporting!


-- Modified portion of Step 9: Final Load
USE ecommerce_project;

-- 1. Correct the syntax for checking true NULLs: use 'IS NULL', not 'LIKE NULL'
-- 2. Update the clean_orders table, setting the Email column based on the CASE logic.

UPDATE clean_orders
SET Email = 
    CASE
        -- Condition 1: Check for true SQL NULL
        -- NOTE: Corrected from 'LIKE NULL' to 'IS NULL'
        WHEN Email IS NULL THEN 'UNKNOWN@example.com' 
        
        -- Condition 2: Check for invalid format (must handle the current value)
        -- We must ensure we ONLY update emails that DON'T meet the standard regex.
        -- If the email is NOT NULL, but fails the regex, it's invalid.
        WHEN Email NOT REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' THEN 'UNKNOWN@example.com'
        
        -- If the email is valid and not NULL, keep its existing value.
        ELSE Email 
    END
-- Optional: Adding a WHERE clause to limit the update to records that actually need changing
-- This can make the update faster and confirm the count of changes.
WHERE Email IS NULL 
   OR Email NOT REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';

-- 3. Verification
SELECT 
    COUNT(*) AS Total_Records,
    SUM(CASE WHEN Email = 'UNKNOWN@example.com' THEN 1 ELSE 0 END) AS Count_of_Unknown_Emails,
    SUM(CASE WHEN Email IS NULL THEN 1 ELSE 0 END) AS Remaining_Null_Emails -- Should be 0
FROM 
    clean_orders;
