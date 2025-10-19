from db_connection import DBConnector, DB_CONFIG
from operations import OrderCRUD
from menu import run_cli

# ==============================================================================
# 4. Main Execution Block
# ==============================================================================
if __name__ == "__main__":
    # 1. Initialize Connector
    connector = DBConnector(DB_CONFIG)
    
    # 2. Initialize CRUD Manager
    crud_manager = OrderCRUD(connector)
    
    # 3. Start the Command Line Interface
    run_cli(crud_manager)
