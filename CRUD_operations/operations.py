import mysql.connector
from db_connection import DBConnector

# ==============================================================================
# 3. OrderCRUD Class (Handles all E-commerce Data Operations)
# ==============================================================================
class OrderCRUD:
    """Performs CRUD operations on the clean_orders table."""

    def __init__(self, connector: DBConnector):
        self.connector = connector

    def _execute_query(self, query, params=None, fetch=False):
        """Internal helper to execute a query and handle commit/fetch."""
        conn = self.connector.connect()
        if not conn:
            return None if fetch else False

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            
            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount if not fetch else True
        except mysql.connector.Error as err:
            print(f"[ERROR] Database Query Error: {err}")
            conn.rollback()
            return None if fetch else 0
        finally:
            cursor.close()
            self.connector.close()

    def fetch_order_by_id(self, order_id: int):
        """
        READ Operation: Fetches a single order record by its unique Order_ID.
        """
        sql_query = "SELECT * FROM clean_orders WHERE Order_ID = %s;"
        return self._execute_query(sql_query, (order_id,), fetch=True)

    def add_new_order(self, data: dict):
        """
        CREATE Operation: Adds a new record to the clean_orders table.
        """
        required_keys = ['Order_ID', 'Order_Date', 'Customer_ID', 'Region', 
                         'Payment_Method', 'Revenue', 'Quantity', 'Email']
        
        if not all(key in data for key in required_keys):
            print("[ERROR] Input data is missing required fields.")
            return False

        sql_query = """
        INSERT INTO clean_orders (
            Order_ID, Order_Date, Customer_ID, Region, Payment_Method, 
            Revenue, Quantity, Email
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        params = (
            data['Order_ID'], data['Order_Date'], data['Customer_ID'], 
            data['Region'], data['Payment_Method'], data['Revenue'], 
            data['Quantity'], data['Email']
        )

        return self._execute_query(sql_query, params)

    def update_order_revenue(self, order_id: int, new_revenue: float):
        """
        UPDATE Operation: Modifies the Revenue field for a specific Order_ID.
        """
        sql_query = "UPDATE clean_orders SET Revenue = %s WHERE Order_ID = %s;"
        params = (new_revenue, order_id)
        return self._execute_query(sql_query, params)

    def delete_order(self, order_id: int):
        """
        DELETE Operation: Removes an order record from the table.
        """
        sql_query = "DELETE FROM clean_orders WHERE Order_ID = %s;"
        return self._execute_query(sql_query, (order_id,))

    def get_max_order_id(self):
        """Fetches the current maximum Order_ID for safe insertion."""
        sql_query = "SELECT MAX(Order_ID) AS max_id FROM clean_orders;"
        result = self._execute_query(sql_query, fetch=True)
        return result[0]['max_id'] if result and result[0]['max_id'] else 100000
