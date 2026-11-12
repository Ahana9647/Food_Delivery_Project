-- =============================================================================
-- Group C: Food Delivery Order Performance Analysis
-- Member 4: SQL Queries & Analysis
-- Database: MySQL 8.0+
-- File: analysis_queries.sql
-- =============================================================================

-- IMPORTANT:
-- 1. Import food_delivery_orders.csv into food_delivery_db.orders first.
-- 2. Check that the imported column names and data types match the table below.
-- 3. Run this script section by section in MySQL Workbench.
-- 4. The queries below use the project brief's suggested column names.

-- =============================================================================
-- 0. DATABASE AND TABLE SETUP
-- =============================================================================

CREATE DATABASE IF NOT EXISTS food_delivery_db;
USE food_delivery_db;

CREATE TABLE IF NOT EXISTS orders (
    Order_ID VARCHAR(30),
    Order_Date DATE,
    Order_Time TIME,
    Restaurant VARCHAR(100),
    Customer_ID VARCHAR(30),
    City VARCHAR(50),
    Distance_KM DECIMAL(10,2),
    Preparation_Time_Min INT,
    Delivery_Time_Min INT,
    Expected_Delivery_Min INT,
    On_Time TINYINT,
    Rating DECIMAL(3,2),
    Order_Value DECIMAL(10,2),
    Delivery_Fee DECIMAL(10,2),
    Vehicle_Type VARCHAR(30),
    Customer_Type VARCHAR(30),
    Order_Status VARCHAR(30)
);

-- =============================================================================
-- 1. CHECK DATABASE, TABLE AND IMPORTED DATA
-- =============================================================================

SELECT DATABASE() AS selected_database;
SHOW TABLES;
DESCRIBE orders;

-- First 10 records
SELECT * FROM orders
LIMIT 10;

-- Total number of imported records
SELECT COUNT(*) AS total_imported_rows
FROM orders;

-- Check order status values
SELECT Order_Status, COUNT(*) AS order_count
FROM orders
GROUP BY Order_Status
ORDER BY order_count DESC;

-- =============================================================================
-- 2. DATA QUALITY CHECKS
-- =============================================================================

-- Missing values in important fields
SELECT
    SUM(Order_ID IS NULL OR TRIM(Order_ID) = '') AS missing_order_id,
    SUM(Restaurant IS NULL OR TRIM(Restaurant) = '') AS missing_restaurant,
    SUM(Distance_KM IS NULL) AS missing_distance,
    SUM(Delivery_Time_Min IS NULL) AS missing_delivery_time,
    SUM(Expected_Delivery_Min IS NULL) AS missing_expected_time,
    SUM(Rating IS NULL) AS missing_rating
FROM orders;

-- Duplicate Order_ID values
SELECT Order_ID, COUNT(*) AS occurrences
FROM orders
WHERE Order_ID IS NOT NULL
GROUP BY Order_ID
HAVING COUNT(*) > 1;

-- Invalid or suspicious numeric values
SELECT *
FROM orders
WHERE Distance_KM < 0
   OR Preparation_Time_Min < 0
   OR Delivery_Time_Min < 0
   OR Expected_Delivery_Min < 0
   OR Rating < 1
   OR Rating > 5
   OR Order_Value < 0
   OR Delivery_Fee < 0;

-- =============================================================================
-- 3. COMPLETED ORDERS
-- =============================================================================

-- All core performance calculations use delivered orders.
-- The CTE derives on-time status from actual and expected delivery duration.
-- This avoids depending on a possibly inconsistent imported On_Time column.

WITH completed AS (
    SELECT *,
           CASE
               WHEN Delivery_Time_Min <= Expected_Delivery_Min THEN 1
               ELSE 0
           END AS calculated_on_time
    FROM orders
    WHERE LOWER(TRIM(Order_Status)) = 'delivered'
      AND Delivery_Time_Min IS NOT NULL
      AND Expected_Delivery_Min IS NOT NULL
      AND Delivery_Time_Min >= 0
      AND Expected_Delivery_Min >= 0
)
SELECT COUNT(*) AS completed_orders
FROM completed;

-- =============================================================================
-- 4. OVERALL BUSINESS KPIs
-- =============================================================================

WITH completed AS (
    SELECT *,
           CASE
               WHEN Delivery_Time_Min <= Expected_Delivery_Min THEN 1
               ELSE 0
           END AS calculated_on_time
    FROM orders
    WHERE LOWER(TRIM(Order_Status)) = 'delivered'
      AND Delivery_Time_Min IS NOT NULL
      AND Expected_Delivery_Min IS NOT NULL
      AND Delivery_Time_Min >= 0
      AND Expected_Delivery_Min >= 0
)
SELECT
    COUNT(*) AS completed_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min,
    ROUND(AVG(calculated_on_time) * 100, 2) AS on_time_delivery_percentage,
    ROUND(AVG(Rating), 2) AS average_customer_rating,
    ROUND(AVG(Distance_KM), 2) AS average_distance_km,
    SUM(calculated_on_time = 0) AS late_orders,
    ROUND(AVG(Preparation_Time_Min), 2) AS average_preparation_time_min
FROM completed;

-- =============================================================================
-- 5. DELIVERY DELAY ANALYSIS
-- =============================================================================

SELECT
    Order_ID,
    Restaurant,
    Delivery_Time_Min,
    Expected_Delivery_Min,
    Delivery_Time_Min - Expected_Delivery_Min AS delay_min,
    CASE
        WHEN Delivery_Time_Min <= Expected_Delivery_Min THEN 'On Time'
        ELSE 'Late'
    END AS delivery_status
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
ORDER BY delay_min DESC
LIMIT 20;

-- =============================================================================
-- 6. RESTAURANT PERFORMANCE SCORECARD
-- =============================================================================

SELECT
    Restaurant,
    COUNT(*) AS total_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min,
    ROUND(AVG(
        CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
             THEN 1 ELSE 0 END
    ) * 100, 2) AS on_time_percentage,
    ROUND(AVG(Rating), 2) AS avg_rating,
    ROUND(AVG(Distance_KM), 2) AS avg_distance_km,
    ROUND(AVG(Delivery_Time_Min - Expected_Delivery_Min), 2) AS avg_delay_min
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
GROUP BY Restaurant
ORDER BY total_orders DESC;

-- =============================================================================
-- 7. TOP 10 PERFORMING RESTAURANTS
-- Rule: minimum 30 completed orders; highest on-time percentage,
-- then highest average rating. The 30-order threshold follows the brief.
-- =============================================================================

SELECT
    Restaurant,
    COUNT(*) AS total_orders,
    ROUND(AVG(
        CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
             THEN 1 ELSE 0 END
    ) * 100, 2) AS on_time_percentage,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min,
    ROUND(AVG(Rating), 2) AS avg_rating
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
GROUP BY Restaurant
HAVING COUNT(*) >= 30
ORDER BY on_time_percentage DESC, avg_rating DESC
LIMIT 10;

-- =============================================================================
-- 8. BOTTOM 10 PERFORMING RESTAURANTS
-- Rule: minimum 30 completed orders; lowest on-time percentage first,
-- then highest average delivery time.
-- =============================================================================

SELECT
    Restaurant,
    COUNT(*) AS total_orders,
    ROUND(AVG(
        CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
             THEN 1 ELSE 0 END
    ) * 100, 2) AS on_time_percentage,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min,
    ROUND(AVG(Rating), 2) AS avg_rating
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
GROUP BY Restaurant
HAVING COUNT(*) >= 30
ORDER BY on_time_percentage ASC, avg_delivery_time_min DESC
LIMIT 10;

-- =============================================================================
-- 9. DISTANCE BAND ANALYSIS
-- =============================================================================

SELECT
    CASE
        WHEN Distance_KM <= 2 THEN '0-2 KM'
        WHEN Distance_KM <= 5 THEN '2-5 KM'
        WHEN Distance_KM <= 10 THEN '5-10 KM'
        WHEN Distance_KM <= 20 THEN '10-20 KM'
        ELSE '20+ KM'
    END AS distance_band,
    COUNT(*) AS total_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min,
    ROUND(AVG(
        CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
             THEN 1 ELSE 0 END
    ) * 100, 2) AS on_time_percentage
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Distance_KM >= 0
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
GROUP BY distance_band
ORDER BY MIN(Distance_KM);

-- =============================================================================
-- 10. CUSTOMER RATING ANALYSIS
-- =============================================================================

SELECT
    Restaurant,
    COUNT(*) AS total_orders,
    ROUND(AVG(Rating), 2) AS average_rating,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Rating BETWEEN 1 AND 5
GROUP BY Restaurant
HAVING COUNT(*) >= 30
ORDER BY average_rating DESC
LIMIT 10;

-- =============================================================================
-- 11. MONTHLY DELIVERY PERFORMANCE
-- =============================================================================

SELECT
    DATE_FORMAT(Order_Date, '%Y-%m') AS order_month,
    COUNT(*) AS total_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min,
    ROUND(AVG(
        CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
             THEN 1 ELSE 0 END
    ) * 100, 2) AS on_time_percentage,
    ROUND(AVG(Rating), 2) AS avg_rating
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Order_Date IS NOT NULL
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
GROUP BY DATE_FORMAT(Order_Date, '%Y-%m')
ORDER BY order_month;

-- =============================================================================
-- 12. VEHICLE TYPE PERFORMANCE (ADVANCED EXTENSION)
-- =============================================================================

SELECT
    Vehicle_Type,
    COUNT(*) AS total_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min,
    ROUND(AVG(
        CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
             THEN 1 ELSE 0 END
    ) * 100, 2) AS on_time_percentage,
    ROUND(AVG(Rating), 2) AS avg_rating
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
GROUP BY Vehicle_Type
ORDER BY on_time_percentage DESC;

-- =============================================================================
-- 13. CITY-WISE PERFORMANCE (ADVANCED EXTENSION)
-- =============================================================================

SELECT
    City,
    COUNT(*) AS total_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min,
    ROUND(AVG(
        CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
             THEN 1 ELSE 0 END
    ) * 100, 2) AS on_time_percentage
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
GROUP BY City
ORDER BY total_orders DESC;

-- =============================================================================
-- 14. EXPORT-READY RESTAURANT SCORECARD
-- =============================================================================

SELECT
    Restaurant,
    COUNT(*) AS order_volume,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time_min,
    ROUND(AVG(
        CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
             THEN 1 ELSE 0 END
    ) * 100, 2) AS on_time_percentage,
    ROUND(AVG(Delivery_Time_Min - Expected_Delivery_Min), 2) AS avg_delay_min,
    ROUND(AVG(Rating), 2) AS avg_rating,
    ROUND(AVG(Distance_KM), 2) AS avg_distance_km,
    CASE
        WHEN AVG(Delivery_Time_Min <= Expected_Delivery_Min) >= 0.90
             AND AVG(Rating) >= 4 THEN 'Strong'
        WHEN AVG(Delivery_Time_Min <= Expected_Delivery_Min) < 0.70
             THEN 'Needs Improvement'
        ELSE 'Moderate'
    END AS performance_category
FROM orders
WHERE LOWER(TRIM(Order_Status)) = 'delivered'
  AND Delivery_Time_Min IS NOT NULL
  AND Expected_Delivery_Min IS NOT NULL
GROUP BY Restaurant
HAVING COUNT(*) >= 30
ORDER BY on_time_percentage DESC, avg_rating DESC;

-- =============================================================================
-- 15. HIGH-VOLUME UNDERPERFORMING RESTAURANTS
-- Rule: at least 30 completed orders and on-time rate below platform average.
-- =============================================================================

WITH completed AS (
    SELECT *,
           CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min
                THEN 1 ELSE 0 END AS on_time_flag
    FROM orders
    WHERE LOWER(TRIM(Order_Status)) = 'delivered'
      AND Delivery_Time_Min IS NOT NULL
      AND Expected_Delivery_Min IS NOT NULL
),
platform_rate AS (
    SELECT AVG(on_time_flag) AS overall_on_time_rate
    FROM completed
),
restaurant_rate AS (
    SELECT
        Restaurant,
        COUNT(*) AS total_orders,
        AVG(on_time_flag) AS restaurant_on_time_rate,
        AVG(Delivery_Time_Min) AS avg_delivery_time_min
    FROM completed
    GROUP BY Restaurant
    HAVING COUNT(*) >= 30
)
SELECT
    r.Restaurant,
    r.total_orders,
    ROUND(r.restaurant_on_time_rate * 100, 2) AS restaurant_on_time_percentage,
    ROUND(p.overall_on_time_rate * 100, 2) AS platform_on_time_percentage,
    ROUND(r.avg_delivery_time_min, 2) AS avg_delivery_time_min
FROM restaurant_rate r
CROSS JOIN platform_rate p
WHERE r.restaurant_on_time_rate < p.overall_on_time_rate
ORDER BY r.restaurant_on_time_rate ASC, r.avg_delivery_time_min DESC;

-- =============================================================================
-- END OF MEMBER 4 SQL ANALYSIS
-- =============================================================================
