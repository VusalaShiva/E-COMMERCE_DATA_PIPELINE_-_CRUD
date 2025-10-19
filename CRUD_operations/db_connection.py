import mysql.connector

# ==============================================================================
# 1. DATABASE CONFIGURATION
# IMPORTANT: Fill in your MySQL database credentials below.
# ==============================================================================
DB_CONFIG = {
    'host': 'localhost',        # Your MySQL server address
    'user': 'root',  # Your MySQL username
    'password': 'Mysql@143', # Your MySQL password
    'database': 'ecommerce_project',
}

# ==============================================================================
# 2. DBConnector Class (Handles Connection Management)
# ==============================================================================
class DBConnector:
    """Manages the MySQL database connection."""
    
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """Establishes a connection to the database."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("[INFO] Database connection successful.")
            return self.connection
        except mysql.connector.Error as err:
            print(f"[ERROR] Error connecting to MySQL: {err}")
            return None

    def close(self):
        """Closes the active database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            # print("[INFO] Database connection closed.") # Suppress for cleaner output
