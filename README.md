# E-COMMERCE DATA PIPELINE & CRUD SYSTEM

## 🎯 Project Overview
This project implements a complete end-to-end Data Pipeline for a simulated E-Commerce dataset, demonstrating core skills in data engineering, data cleaning (ETL/ELT), database management (MySQL), object-oriented programming (Python), and business intelligence (Power BI).

The goal was to transform messy, inconsistent raw data into a clean, structured asset suitable for real-time analysis and reporting.

## 🛠 Technology Stack

<table align="center">
  <thead>
    <tr>
      <th align="left">Category</th>
      <th align="left">Tool / Language</th>
      <th align="left">Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Database</strong></td>
      <td>MySQL</td>
      <td>Central relational database for storage and data cleaning.</td>
    </tr>
    <tr>
      <td><strong>Programming</strong></td>
      <td>Python</td>
      <td>Data generation, scripting, and object-oriented database interaction (CRUD).</td>
    </tr>
    <tr>
      <td><strong>Libraries</strong></td>
      <td>Pandas, mysql-connector-python</td>
      <td>Efficient data handling, fetching, and Excel export.</td>
    </tr>
    <tr>
      <td><strong>Reporting</strong></td>
      <td>Power BI</td>
      <td>Final phase for visualization and KPI reporting.</td>
    </tr>
  </tbody>
</table>

## 🏗 Project Phases
The project was executed in five sequential phases, ensuring data integrity at every step.

### Phase 1 & 2: Data Generation and Profiling
*   **Generation**: Created a custom dataset (`raw_orders`) containing over 160 records with deliberate inconsistencies (duplicates, mixed date formats, text in numeric fields, etc.) using Python's Faker.
*   **Profiling**: Used SQL queries to systematically identify all major data quality issues, preparing the cleaning roadmap.

### Phase 3: Data Cleaning and Transformation (SQL)
The raw data was transformed into a clean, permanent table named `clean_orders`. All transformations were executed in MySQL to enforce data governance and performance.
*   **De-duplication**: Removed duplicate orders based on `Order_ID`.
*   **Data Type Correction**: Converted date strings to `DATE`, text representations of numbers (like 'FORTY') to numeric `DECIMAL` or `INT`.
*   **Standardization**: Used SQL functions to correct capitalization (e.g., 'upi' to 'Upi') and replaced missing values in `Region` (NULL, 'NA') with 'UNKNOWN'.
*   **Email Validation**: Invalid or NULL emails were standardized to a placeholder ('UNKNOWN@example.com') or set to `NULL` to maintain validity.

### Phase 4: Application Layer (Python CRUD & Export)
This phase established the software infrastructure to interact with the cleaned data.
*   **Structured OOP Code**: The database interaction logic was structured using Object-Oriented Programming (OOP) across four files:
    *   `db_connection.py`: Manages the MySQL connection details.
    *   `operations.py`: Contains the `OrderCRUD` class for Create, Read, Update, and Delete operations.
    *   `menu.py`: Provides the command-line interface (CLI) logic.
    *   `main.py`: The entry point for the application.
*   **Data Export (`export_orders_report.py`)**: A dedicated script was created using Pandas to fetch all records from the `clean_orders` table and export the result directly to an Excel file (`clean_orders_report.xlsx`) for external analysis.

### Phase 5: Reporting and Analysis
*   **KPI Calculation (SQL)**: Key performance indicators (KPIs) like Total Revenue, Average Order Value (AOV), and Regional Revenue were calculated using aggregate SQL queries.
*   **Visualization (Power BI)**: A dashboard blueprint was designed to visualize these KPIs, providing a clear overview of monthly trends, regional performance, and payment method popularity.

## ⚙️ Setup and Execution

### Prerequisites
1.  **MySQL Server**: Must be running with the `ecommerce_project` database created.
2.  **Python 3.x**
3.  **Dependencies**: Install the required Python packages:
    ```bash
    pip install pandas mysql-connector-python openpyxl
    ```

### Running the Project
1.  **Update Credentials**: Before running any script, ensure the `DB_CONFIG` dictionary in `db_connection.py` and `export_orders_report.py` contains your correct MySQL credentials.
2.  **Run CRUD Application**: To test real-time database manipulation:
    ```bash
    python main.py
    ```
3.  **Run Data Export**: To generate the Excel report:
    ```bash
    python export_orders_report.py
    ```
