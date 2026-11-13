-- =============================================================================
-- Group C: Food Delivery Order Performance Analysis
-- Deliverable for Member 4: SQL Queries & Analysis
-- Database System: MySQL
-- File Name: analysis_queries.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. Database Selection
-- -----------------------------------------------------------------------------
USE food_delivery_db;

-- -----------------------------------------------------------------------------
-- 1. Core Platform KPIs
-- Business Questions: 1, 2, 7, 8
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(Order_ID) AS Total_Completed_Orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS Overall_Avg_Delivery_Time_Min,
    ROUND(AVG(Distance_KM), 2) AS Overall_Avg_Distance_KM,
    ROUND(AVG(Rating), 2) AS Overall_Avg_Rating,
    ROUND(SUM(CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min THEN 1 ELSE 0 END) * 100.0 / COUNT(Order_ID), 2) AS On_Time_Delivery_Percentage,
    SUM(CASE WHEN Delivery_Time_Min > Expected_Delivery_Min THEN 1 ELSE 0 END) AS Total_Late_Orders
FROM orders;


-- -----------------------------------------------------------------------------
-- 2. Restaurant Performance & Benchmarking
-- Business Questions: 3, 4, 5, 6
-- -----------------------------------------------------------------------------

-- 2.1 Restaurant Summary Metrics View
CREATE OR REPLACE VIEW v_restaurant_performance AS
SELECT 
    Restaurant,
    COUNT(Order_ID) AS Order_Volume,
    ROUND(AVG(Delivery_Time_Min), 2) AS Avg_Delivery_Time_Min,
    ROUND(SUM(CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min THEN 1 ELSE 0 END) * 100.0 / COUNT(Order_ID), 2) AS On_Time_Percentage,
    ROUND(AVG(Delivery_Time_Min - Expected_Delivery_Min), 2) AS Avg_Delay_Min,
    ROUND(AVG(Rating), 2) AS Avg_Rating,
    ROUND(AVG(Distance_KM), 2) AS Avg_Distance_KM
FROM orders
GROUP BY Restaurant;

-- 2.2 Top 10 Performing Restaurants (Threshold >= 30 Orders)
SELECT *
FROM v_restaurant_performance
WHERE Order_Volume >= 30
ORDER BY On_Time_Percentage DESC, Avg_Rating DESC
LIMIT 10;

-- 2.3 Bottom 10 Performing Restaurants (Threshold >= 30 Orders)
SELECT *
FROM v_restaurant_performance
WHERE Order_Volume >= 30
ORDER BY On_Time_Percentage ASC, Avg_Delivery_Time_Min DESC
LIMIT 10;

-- 2.4 Fastest Restaurants by Average Delivery Time (Threshold >= 30 Orders)
SELECT Restaurant, Order_Volume, Avg_Delivery_Time_Min, On_Time_Percentage
FROM v_restaurant_performance
WHERE Order_Volume >= 30
ORDER BY Avg_Delivery_Time_Min ASC
LIMIT 10;

-- 2.5 Highest Rated Restaurants (Threshold >= 30 Orders)
SELECT Restaurant, Order_Volume, Avg_Rating, Avg_Delivery_Time_Min, On_Time_Percentage
FROM v_restaurant_performance
WHERE Order_Volume >= 30
ORDER BY Avg_Rating DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 3. High-Risk / Underperforming Identification
-- Business Question: 10
-- Rule: Volume >= 30 orders AND On-Time % lower than platform average
-- -----------------------------------------------------------------------------
SET @overall_on_time_pct = (
    SELECT ROUND(SUM(CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
    FROM orders
);

SELECT 
    Restaurant,
    Order_Volume,
    Avg_Delivery_Time_Min,
    On_Time_Percentage,
    Avg_Delay_Min,
    Avg_Rating,
    'Underperforming - Requires Action' AS Status_Flag
FROM v_restaurant_performance
WHERE Order_Volume >= 30 
  AND On_Time_Percentage < @overall_on_time_pct
ORDER BY On_Time_Percentage ASC, Avg_Delivery_Time_Min DESC;


-- -----------------------------------------------------------------------------
-- 4. Distance Band Analysis
-- Business Question: 9
-- Categorizes delivery performance into 5 distance buckets
-- -----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN Distance_KM <= 2 THEN '0-2 KM'
        WHEN Distance_KM > 2 AND Distance_KM <= 5 THEN '2-5 KM'
        WHEN Distance_KM > 5 AND Distance_KM <= 10 THEN '5-10 KM'
        WHEN Distance_KM > 10 AND Distance_KM <= 20 THEN '10-20 KM'
        ELSE '20+ KM'
    END AS Distance_Band,
    COUNT(Order_ID) AS Order_Volume,
    ROUND(AVG(Delivery_Time_Min), 2) AS Avg_Delivery_Time_Min,
    ROUND(SUM(CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min THEN 1 ELSE 0 END) * 100.0 / COUNT(Order_ID), 2) AS On_Time_Percentage
FROM orders
GROUP BY Distance_Band
ORDER BY 
    CASE Distance_Band
        WHEN '0-2 KM' THEN 1
        WHEN '2-5 KM' THEN 2
        WHEN '5-10 KM' THEN 3
        WHEN '10-20 KM' THEN 4
        ELSE 5
    END;


-- -----------------------------------------------------------------------------
-- 5. Monthly Delivery Performance Trends
-- Business Question: 11
-- Tracks delivery metrics across months
-- -----------------------------------------------------------------------------
SELECT 
    DATE_FORMAT(Order_Date, '%Y-%m') AS Order_Month,
    COUNT(Order_ID) AS Order_Volume,
    ROUND(AVG(Delivery_Time_Min), 2) AS Avg_Delivery_Time_Min,
    ROUND(SUM(CASE WHEN Delivery_Time_Min <= Expected_Delivery_Min THEN 1 ELSE 0 END) * 100.0 / COUNT(Order_ID), 2) AS On_Time_Percentage,
    ROUND(AVG(Rating), 2) AS Avg_Rating
FROM orders
GROUP BY Order_Month
ORDER BY Order_Month ASC;


-- -----------------------------------------------------------------------------
-- 6. Recommended Restaurant Scorecard Export
-- Project Deliverable: Exportable scorecard table
-- -----------------------------------------------------------------------------
SELECT 
    Restaurant,
    Order_Volume,
    Avg_Delivery_Time_Min,
    On_Time_Percentage,
    Avg_Delay_Min,
    Avg_Rating,
    Avg_Distance_KM,
    CASE 
        WHEN Order_Volume >= 30 AND On_Time_Percentage >= 90 AND Avg_Rating >= 4.2 THEN 'Top Performer'
        WHEN Order_Volume >= 30 AND On_Time_Percentage < @overall_on_time_pct THEN 'Underperforming'
        ELSE 'Moderate / Average'
    END AS Performance_Category
FROM v_restaurant_performance
ORDER BY Order_Volume DESC;