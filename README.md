# Group C – Food Delivery Order Performance Analysis
## Member 4: SQL Queries & Analysis

### Deliverables
- `analysis_queries.sql` – MySQL database setup, data checks, KPIs, restaurant analysis and business queries.
- `screenshots/` – Add screenshots captured from your own MySQL Workbench execution.

### Requirements
- MySQL Server 8.0 or later
- MySQL Workbench
- `food_delivery_orders.csv` dataset supplied by the project team

### Database
- Database: `food_delivery_db`
- Table: `orders`

### How to run
1. Install and open MySQL Server and MySQL Workbench.
2. Connect to your local MySQL instance.
3. Open `analysis_queries.sql` in Workbench.
4. Execute the database/table setup section.
5. Import `food_delivery_orders.csv` into `food_delivery_db.orders` using **Table Data Import Wizard**.
6. During import, verify that the CSV headers match the table columns and that dates/times and numeric columns are mapped correctly.
7. Run the remaining SQL sections one at a time.
8. Check the result grid and save genuine screenshots in `screenshots/`.

### Important import note
The project brief suggests these columns: `Order_ID`, `Order_Date`, `Order_Time`, `Restaurant`, `Customer_ID`, `City`, `Distance_KM`, `Preparation_Time_Min`, `Delivery_Time_Min`, `Expected_Delivery_Min`, `On_Time`, `Rating`, `Order_Value`, `Delivery_Fee`, `Vehicle_Type`, `Customer_Type`, and `Order_Status`.

If the actual CSV has different headers or date formats, adjust the table/import mapping before running the analysis. Do not claim results until the dataset has been imported and the queries have executed successfully.

### Analysis included
1. Database and table setup
2. Data inspection and data-quality checks
3. Completed-order filtering
4. Overall KPIs: completed orders, average delivery time, on-time percentage, average rating, average distance and late orders
5. Delivery delay analysis
6. Restaurant performance scorecard
7. Top and bottom 10 restaurants (minimum 30 completed orders)
8. Delivery distance bands
9. Restaurant rating analysis
10. Monthly performance
11. Vehicle-type and city-wise performance
12. High-volume underperforming restaurants

### Business-rule notes
- Core performance analysis uses rows whose `Order_Status` is `Delivered`.
- On-time status is calculated from `Delivery_Time_Min <= Expected_Delivery_Min`, rather than trusting the imported `On_Time` field.
- The minimum restaurant volume is 30 completed orders, following the project brief. The brief describes this threshold as illustrative, not a universal industry standard.
- The scorecard categories are simple documented rules for demonstration. They should be reviewed with the project team before presenting as business standards.
- The queries identify associations and rankings; they do not prove why a restaurant is delayed.

### Screenshot checklist
Save genuine screenshots with clear query text and result grids:
- `01_database_creation.png`
- `02_table_structure.png`
- `03_total_orders.png`
- `04_overall_kpis.png`
- `05_restaurant_performance.png`
- `06_top_restaurants.png`
- `07_bottom_restaurants.png`
- `08_distance_analysis.png`
- `09_monthly_analysis.png`

### GitHub
Upload this folder to the shared Group C repository, or create a dedicated repository if the team has agreed to that approach. Add the dataset only if the team has permission to share it and it is not too large or restricted. Never upload passwords, database credentials, or private connection details.
