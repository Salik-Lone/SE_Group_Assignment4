import os
import sqlite3
from datetime import datetime
import subprocess

# Database file
DATABASE_FILE = "inventory.db"

# Initialize Git repository
def init_git():
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"])
        print("Initialized Git repository.")

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
   
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            sku TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Purchases (
            transaction_id TEXT PRIMARY KEY,
            sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (sku) REFERENCES Products(sku)
        )
    ''')
   
    conn.commit()
    conn.close()

# Commit changes to Git
def git_commit(message):
    subprocess.run(["git", "add", DATABASE_FILE])
    subprocess.run(["git", "commit", "-m", message])

# Add a new product
def add_product(sku, name, price, quantity):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
   
    try:
        cursor.execute('''
            INSERT INTO Products (sku, name, price, quantity)
            VALUES (?, ?, ?, ?)
        ''', (sku, name, price, quantity))
       
        conn.commit()
        git_commit("Added new product: " + name)
        print("Product '" + name + "' added successfully.")
    except sqlite3.IntegrityError:
        print("Product with SKU " + sku + " already exists.")
    finally:
        conn.close()

# Update product quantity
def update_product_quantity(sku, quantity):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
   
    cursor.execute('''
        UPDATE Products
        SET quantity = quantity + ?
        WHERE sku = ?
    ''', (quantity, sku))
   
    if cursor.rowcount > 0:
        conn.commit()
        git_commit("Updated quantity for product SKU: " + sku)
        print("Quantity for product SKU " + sku + " updated successfully.")
    else:
        print("Product with SKU " + sku + " not found.")
   
    conn.close()

# Make a purchase
def make_purchase(sku, quantity):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
   
    # Check product availability
    cursor.execute('''
        SELECT name, price, quantity FROM Products WHERE sku = ?
    ''', (sku,))
    product = cursor.fetchone()
   
    if product:
        name, price, available_quantity = product
        if available_quantity >= quantity:
            # Update product quantity
            cursor.execute('''
                UPDATE Products
                SET quantity = quantity - ?
                WHERE sku = ?
            ''', (quantity, sku))
           
            # Log purchase
            transaction_id = "txn" + datetime.now().strftime('%Y%m%d%H%M%S')
            total_price = price * quantity
            timestamp = datetime.now().isoformat()
           
            cursor.execute('''
                INSERT INTO Purchases (transaction_id, sku, quantity, total_price, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (transaction_id, sku, quantity, total_price, timestamp))
           
            conn.commit()
            git_commit("Purchase: " + str(quantity) + "x " + name + " sold")
            print("Purchase successful. " + str(quantity) + "x " + name + " sold.")
        else:
            print("Insufficient stock for product SKU " + sku + ".")
    else:
        print("Product with SKU " + sku + " not found.")
   
    conn.close()

# Display products
def display_products():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
   
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
   
    if not products:
        print("No products available.")
    else:
        print("Product Catalog:")
        for product in products:
            print("SKU: " + product[0] + ", Name: " + product[1] + ", Price: $" + str(product[2]) + ", Quantity: " + str(product[3]))
   
    conn.close()

# Display purchase history
def display_purchase_history():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
   
    cursor.execute('SELECT * FROM Purchases')
    purchases = cursor.fetchall()
   
    if not purchases:
        print("No purchase history available.")
    else:
        print("Purchase History:")
        for purchase in purchases:
            print("Transaction ID: " + purchase[0] + ", SKU: " + purchase[1] + ", Quantity: " + str(purchase[2]) + ", Total Price: $" + str(purchase[3]) + ", Timestamp: " + purchase[4])
   
    conn.close()

# Main function
def main():
    init_git()
    init_db()
   
    while True:
        print("\nInventory Management System")
        print("1. Add Product")
        print("2. Update Product Quantity")
        print("3. Make Purchase")
        print("4. Display Products")
        print("5. Display Purchase History")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            sku = input("Enter SKU: ")
            name = input("Enter product name: ")
            price = float(input("Enter price: "))
            quantity = int(input("Enter quantity: "))
            add_product(sku, name, price, quantity)

        elif choice == "2":
            sku = input("Enter SKU: ")
            quantity = int(input("Enter quantity to add/subtract: "))
            update_product_quantity(sku, quantity)

        elif choice == "3":
            sku = input("Enter SKU: ")
            quantity = int(input("Enter quantity to purchase: "))
            make_purchase(sku, quantity)

        elif choice == "4":
            display_products()

        elif choice == "5":
            display_purchase_history()

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
