import mysql.connector
import pandas as pd
from mysql.connector import Error

# ==============================================================================
# 1. DATABASE CONFIGURATION
# IMPORTANT: Replace these with your actual MySQL database credentials.
# ==============================================================================
DB_CONFIG = {
    'host': 'localhost',        # Your MySQL server address
    'user': 'root',  # Your MySQL username
    'password': 'Mysql@143', # Your MySQL password
    'database': 'ecommerce_project',
}

# ==============================================================================
# 2. DataExporter Class (Handles Fetching and Exporting)
# ==============================================================================
class DataExporter:
    """
    Handles connecting to the database, fetching all clean order data, 
    and exporting the results to an Excel file.
    """
    def __init__(self, config: dict):
        self.config = config
        # Renaming the output file to match the new script purpose
        self.output_file = 'clean_orders_report.xlsx' 

    def fetch_all_data(self):
        """
        Connects to MySQL, executes a SELECT * query, and returns the data 
        as a Pandas DataFrame.
        """
        print("[INFO] Attempting to connect to the database...")
        conn = None
        try:
            # 1. Establish connection
            conn = mysql.connector.connect(**self.config)
            if conn.is_connected():
                print("[INFO] Connection successful.")
            
            # 2. Define the query
            sql_query = "SELECT * FROM clean_orders ORDER BY Order_Date DESC;"
            print(f"[INFO] Executing query: {sql_query}")

            # 3. Use Pandas to read the entire SQL query result directly
            # This is highly efficient compared to looping through a cursor.
            df = pd.read_sql(sql_query, conn)
            
            print(f"[SUCCESS] Fetched {len(df)} records from 'clean_orders' table.")
            return df

        except Error as e:
            print(f"[ERROR] Database error occurred: {e}")
            return pd.DataFrame() # Return an empty DataFrame on failure
        
        finally:
            if conn and conn.is_connected():
                conn.close()
                print("[INFO] Database connection closed.")

    def export_to_excel(self, df: pd.DataFrame):
        """
        Saves the Pandas DataFrame to an Excel file (.xlsx).
        
        Args:
            df (pd.DataFrame): The DataFrame containing the data to export.
        """
        if df.empty:
            print("[WARNING] Cannot export. DataFrame is empty.")
            return

        try:
            # Save the DataFrame to the specified Excel file
            df.to_excel(self.output_file, index=False, sheet_name='Clean Orders Data')
            print("-" * 50)
            print(f"🎉 Successfully exported data to: {self.output_file}")
            print(f"Total rows exported: {len(df)}")
            print("-" * 50)
        except Exception as e:
            print(f"[ERROR] Failed to write to Excel file: {e}")


# ==============================================================================
# 3. Main Execution Block
# ==============================================================================
if __name__ == "__main__":
    # 1. Initialize the Exporter
    exporter = DataExporter(DB_CONFIG)
    
    # 2. Fetch the data
    clean_data_df = exporter.fetch_all_data()
    
    # 3. Export the data to Excel
    exporter.export_to_excel(clean_data_df)
