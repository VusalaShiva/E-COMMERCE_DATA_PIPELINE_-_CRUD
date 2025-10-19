from operations import OrderCRUD
from datetime import date
import random
import time

def display_menu():
    """Prints the main menu options to the console."""
    print("\n" + "="*40)
    print(" E-Commerce Data Management System")
    print("="*40)
    print("1. CREATE (Add New Order)")
    print("2. READ (Fetch Order by ID)")
    print("3. UPDATE (Modify Order Revenue)")
    print("4. DELETE (Remove Order)")
    print("5. Exit")
    print("-" * 40)

def get_int_input(prompt: str):
    """Safely gets an integer input from the user."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("[WARNING] Invalid input. Please enter a whole number.")

def display_order(results):
    """Prints fetched order details."""
    if results:
        print("\nOrder Found:")
        for key, value in results[0].items():
            print(f"  {key}: {value}")
    else:
        print("[WARNING] Order not found.")

def handle_create(crud_manager: OrderCRUD, max_id: int):
    """Handles the user input and creation of a new order."""
    new_id = max_id + 1
    print(f"\n--- CREATE: Adding Order ID {new_id} ---")
    
    data = {
        'Order_ID': new_id,
        'Order_Date': date.today(),
        'Customer_ID': input("Enter Customer ID (e.g., CUST-123): "),
        'Region': input("Enter Region (e.g., North, East): "),
        'Payment_Method': input("Enter Payment Method: "),
        'Revenue': get_int_input("Enter Revenue: "),
        'Quantity': get_int_input("Enter Quantity: "),
        'Email': input("Enter Customer Email: ")
    }
    
    if crud_manager.add_new_order(data):
        print(f"\n[SUCCESS] New Order ID {new_id} created.")
    else:
        print(f"\n[FAILURE] Could not create Order ID {new_id}.")

def handle_read(crud_manager: OrderCRUD):
    """Handles fetching an order by ID."""
    order_id = get_int_input("\nEnter Order ID to fetch: ")
    results = crud_manager.fetch_order_by_id(order_id)
    display_order(results)

def handle_update(crud_manager: OrderCRUD):
    """Handles updating the revenue of an existing order."""
    order_id = get_int_input("\nEnter Order ID to update: ")
    new_revenue = get_int_input("Enter new Revenue value: ")
    
    if crud_manager.update_order_revenue(order_id, new_revenue):
        print(f"\n[SUCCESS] Order ID {order_id} updated.")
        # Show updated record
        display_order(crud_manager.fetch_order_by_id(order_id))
    else:
        print(f"\n[FAILURE] Could not update Order ID {order_id}. Does it exist?")

def handle_delete(crud_manager: OrderCRUD):
    """Handles deleting an order by ID."""
    order_id = get_int_input("\nEnter Order ID to DELETE: ")
    
    # Optional: Confirm deletion
    if input(f"Are you sure you want to delete Order ID {order_id}? (yes/no): ").lower() != 'yes':
        print("[INFO] Deletion cancelled.")
        return

    if crud_manager.delete_order(order_id) > 0:
        print(f"\n[SUCCESS] Order ID {order_id} deleted successfully.")
    else:
        print(f"\n[FAILURE] Could not delete Order ID {order_id}. Does it exist?")


def run_cli(crud_manager: OrderCRUD):
    """Main loop for the command-line interface."""
    running = True
    
    # Get max ID once for safe creation
    max_id = crud_manager.get_max_order_id()
    print(f"[INFO] Current max Order ID in table: {max_id}")
    
    while running:
        display_menu()
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            max_id = crud_manager.get_max_order_id() # Refresh max_id before creation
            handle_create(crud_manager, max_id)
        elif choice == '2':
            handle_read(crud_manager)
        elif choice == '3':
            handle_update(crud_manager)
        elif choice == '4':
            handle_delete(crud_manager)
        elif choice == '5':
            running = False
            print("\nExiting the E-Commerce Data Management System. Goodbye!")
        else:
            print("[WARNING] Invalid choice. Please select a number from 1 to 5.")
        
        if running:
            time.sleep(1) # Pause for readability
