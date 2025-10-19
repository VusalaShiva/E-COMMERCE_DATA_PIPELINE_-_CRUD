import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker and set seed for reproducibility
fake = Faker()
random.seed(42)

# --- Configuration ---
NUM_RECORDS = 160  # Generating 160 records (150+ as requested)
REGIONS = ['North', 'South', 'East', 'West', 'Central']
PAYMENT_METHODS = ['UPI', 'Credit Card', 'Cash on Delivery', 'NetBanking', 'Debit Card']

# --- Lists to hold data ---
order_ids = []
order_dates = []
customer_ids = []
regions = []
payment_methods = []
revenues = []
quantities = []
emails = []

# --- Data Generation Loop ---
for i in range(1, NUM_RECORDS + 1):
    # 1. Base Data
    order_id = 1000 + i
    order_date = fake.date_between(start_date='-1y', end_date='today')
    customer_id = f'CUST-{random.randint(10, 99)}'
    region = random.choice(REGIONS)
    payment_method = random.choice(PAYMENT_METHODS)
    revenue = round(random.uniform(10.00, 500.00), 2)
    quantity = random.randint(1, 10)
    email = fake.email()

    # --- Injecting Intentional Errors (Approx. 10-15% Error Rate) ---

    # 2. Duplicate Order IDs (Goal: 5% of records)
    if i % 20 == 0:
        order_id = 1000 + random.randint(1, 15)  # Duplicate a previous, random ID

    # 3. Null/Missing Values (Goal: 10% of records)
    if i % 10 == 0:
        customer_id = None
    if i % 15 == 0:
        regions.append('NULL')  # String 'NULL'
    else:
        regions.append(region)

    # 4. Invalid Date Formats (Goal: 5% of records)
    if i % 25 == 0:
        order_date = datetime.strftime(order_date, '%m/%d/%Y') # MM/DD/YYYY format
    elif i % 50 == 0:
        order_date = datetime.strftime(order_date, '%d-%m-%y') # DD-MM-YY format
    else:
        order_date = datetime.strftime(order_date, '%Y-%m-%d') # Standard format

    # 5. Textual Inconsistencies (Goal: 15% of records)
    if i % 7 == 0:
        payment_method = payment_method.lower() # e.g., 'upi' instead of 'UPI'
    elif i % 13 == 0:
        payment_method = payment_method.replace(' ', '.') # e.g., 'Cash.on.Delivery'
    
    # 6. Incorrect Data Types (Goal: 5% of records)
    if i % 30 == 0:
        revenue = random.choice(['ZERO', 'thirty-five', 'NA']) # Text in Revenue
    elif i % 40 == 0:
        quantity = random.choice(['one', 'two', '100+']) # Text in Quantity
    
    # 7. Invalid Email Addresses (Goal: 5% of records)
    if i % 22 == 0:
        email = email.replace('.', '_at_') # Missing '@' and '.'

    # --- Append to lists ---
    order_ids.append(order_id)
    order_dates.append(order_date)
    customer_ids.append(customer_id)
    payment_methods.append(payment_method)
    revenues.append(revenue)
    quantities.append(quantity)
    emails.append(email)

# --- Create DataFrame and Export ---
raw_data = pd.DataFrame({
    'Order_ID': order_ids,
    'Order_Date': order_dates,
    'Customer_ID': customer_ids,
    'Region': regions,
    'Payment_Method': payment_methods,
    'Revenue': revenues,
    'Quantity': quantities,
    'Email': emails
})

# Export the DataFrame to a CSV file
file_name = 'raw_ecommerce_data_160_rows.csv'
raw_data.to_csv(file_name, index=False)
print(f"🎉 Successfully generated and saved {len(raw_data)} messy records to {file_name}")

# Display the first few rows to confirm errors are present
print("\nSample of generated messy data:")
print(raw_data.head(10).to_markdown(index=False))