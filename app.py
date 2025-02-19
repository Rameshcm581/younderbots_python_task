import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error

def initialize_database():
    db = mysql.connector.connect(
            host="localhost",
            user="test",
            database="company_db"
        )
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_name VARCHAR(255) NOT NULL,
            percentage FLOAT NOT NULL
        )
        """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_shares (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        total_percentage FLOAT NOT NULL,
        stock_name VARCHAR(255) NOT NULL,
        allocated_percentage FLOAT NOT NULL
        );
        """)
    return cursor,db

def fetch_data():
    cursor.execute("SELECT stock_name, percentage FROM stock_data")
    return cursor.fetchall()

def fetch_allocated_shares():
    cursor.execute("SELECT customer_id, total_percentage, stock_name, allocated_percentage FROM customer_shares")
    return cursor.fetchall()

def add_data():
    dialog = tk.Toplevel(root)
    dialog.title("Add Stock")
    dialog.geometry("300x150")

    tk.Label(dialog, text="Stock Name:").grid(row=0, column=0, padx=10, pady=10)
    stock_name_entry = tk.Entry(dialog)
    stock_name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Percentage:").grid(row=1, column=0, padx=10, pady=10)
    percentage_entry = tk.Entry(dialog)
    percentage_entry.grid(row=1, column=1, padx=10, pady=10)

    def save_data():
        stock_name = stock_name_entry.get()
        percentage = percentage_entry.get()
        if stock_name and percentage:
            cursor.execute("INSERT INTO stock_data (stock_name, percentage) VALUES (%s, %s)", (stock_name, float(percentage)))
            db.commit()
            refresh_table()
            dialog.destroy() 
    
    tk.Button(dialog, text="Add", command=save_data()).grid(row=2, column=1, columnspan=2, pady=10)

def edit_data():
    selected_item = table.selection()
    if selected_item:
        selected_data = table.item(selected_item)['values']

        dialog = tk.Toplevel(root)
        dialog.title("Edit Stock")
        dialog.geometry("300x150")

        tk.Label(dialog, text="Stock Name:").grid(row=0, column=0, padx=10, pady=10)
        stock_name_entry = tk.Entry(dialog)
        stock_name_entry.grid(row=0, column=1, padx=10, pady=10)
        stock_name_entry.insert(0, selected_data[0])
          
        tk.Label(dialog, text="Percentage:").grid(row=1, column=0, padx=10, pady=10)
        percentage_entry = tk.Entry(dialog)
        percentage_entry.grid(row=1, column=1, padx=10, pady=10)
        percentage_entry.insert(0, selected_data[1])  

        def save_edit():
            new_stock_name = stock_name_entry.get()
            new_percentage = percentage_entry.get()
            if new_stock_name and new_percentage:
                cursor.execute("UPDATE stock_data SET stock_name=%s, percentage=%s WHERE stock_name=%s AND percentage=%s",
                (new_stock_name, float(new_percentage), selected_data[0], selected_data[1]))
                db.commit()
                refresh_table()
                dialog.destroy()

        tk.Button(dialog, text="Save", command=save_edit).grid(row=2, column=0, columnspan=2, pady=10)

def delete_data():
    selected_item = table.selection()
    if selected_item:
        selected_data = table.item(selected_item)['values']
        confirm = messagebox.askyesno("Delete Stock", f"Are you sure you want to delete {selected_data[0]}?")
        if confirm:
            cursor.execute("DELETE FROM stock_data WHERE stock_name=%s AND percentage=%s", (selected_data[0], selected_data[1]))
            db.commit()
            refresh_table()
            
def allocate_shares():
    dialog = tk.Toplevel(root)
    dialog.title("Allocate Shares")
    dialog.geometry("300x150")

    tk.Label(dialog, text="Customer ID:").grid(row=0, column=0, padx=10, pady=10)
    customer_id_entry = tk.Entry(dialog)
    customer_id_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Total Percentage:").grid(row=1, column=0, padx=10, pady=10)
    total_percentage_entry = tk.Entry(dialog)
    total_percentage_entry.grid(row=1, column=1, padx=10, pady=10)

    def save_allocation():
        customer_id = customer_id_entry.get()
        total_percentage = total_percentage_entry.get()
        if customer_id and total_percentage:
            cursor.execute("SELECT stock_name, percentage FROM stock_data")
            stocks = cursor.fetchall()

            total_stock_percentage = sum(stock[1] for stock in stocks)
            allocations = []
            for stock in stocks:
                stock_name, stock_percentage = stock
                allocated_percentage = (stock_percentage / total_stock_percentage) * float(total_percentage)
                allocations.append((customer_id, total_percentage, stock_name, allocated_percentage))

            cursor.executemany("""
                INSERT INTO customer_shares (customer_id, total_percentage, stock_name, allocated_percentage)
                VALUES (%s, %s, %s, %s)
                """, allocations)
            db.commit()
            messagebox.showinfo("Success", "Shares allocated successfully!")
            dialog.destroy()

    tk.Button(dialog, text="Allocate", command=save_allocation).grid(row=2, column=0, columnspan=2, pady=10)
    
def view_allocated_shares():
    view_window = tk.Toplevel(root)
    view_window.title("Allocated Shares")
    view_window.geometry("600x400")

    columns = ("Customer ID", "Total Percentage", "Stock Name", "Allocated Percentage")
    allocated_table = ttk.Treeview(view_window, columns=columns, show="headings")
    for col in columns:
        allocated_table.heading(col, text=col)
    allocated_table.pack(fill="both", expand=True)

    allocated_shares = fetch_allocated_shares()
    for share in allocated_shares:
        allocated_table.insert("", "end", values=share)

def refresh_table():
    for row in table.get_children():
        table.delete(row)
    data = fetch_data()
    for row in data:
        table.insert("", "end", values=row)

cursor,db = initialize_database()

root = tk.Tk()
root.title("Stock Manager")

columns = ("Stock Name", "Percentage")
table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
table.pack(side="left", fill="both", expand=True)

button_frame = tk.Frame(root)
button_frame.pack(side="right", fill="y")

add_button = tk.Button(button_frame, text="Add", command=add_data)
add_button.pack(fill="x",pady="5px")

edit_button = tk.Button(button_frame, text="Edit", command=edit_data)
edit_button.pack(fill="x",pady="5px")

delete_button = tk.Button(button_frame, text="Delete", command=delete_data)
delete_button.pack(fill="x",pady="5px")

allocate_button = tk.Button(button_frame, text="Allocate Share", command=allocate_shares)
allocate_button.pack(fill="x", pady=5)

view_button = tk.Button(button_frame, text="View Allocated Shares", command=view_allocated_shares)
view_button.pack(fill="x", pady=5)

refresh_table()

root.mainloop()
