from datetime import datetime
import logging
import pyodbc

# Setup logging
logging.basicConfig(filename='hotel_management_order.log', level=logging.INFO)

# Database connection
connection = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-0G3UH8F\\SQLEXPRESS;'
    'DATABASE=hotel_management;'
    'Trusted_Connection=yes;'
    # 'UID=DESKTOP-0G3UH8F\OmkarK;'
    # 'PWD='
)

cursor = connection.cursor()

# Define the classes
class MenuCard:
    def __init__(self, menu_id, menu_name, price, available):
        self.menu_id = menu_id
        self.menu_name = menu_name
        self.price = price
        self.available = available

class Order:
    def __init__(self, sr_no, tbl_id, menu_item, quantity):
        self.sr_no = sr_no
        self.tbl_id = tbl_id
        self.menu_item = menu_item
        self.quantity = quantity
        self.order_date = datetime.now()

        self.validate_order()
        self.log_order()
        self.save_to_db()

    def validate_order(self):
        if self.menu_item.available != 'Y':
            raise ValueError(f"Menu item '{self.menu_item.menu_name}' is not available.")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
    
    def log_order(self):
        logging.info(f"Order logged: Table {self.tbl_id}, Menu: {self.menu_item.menu_name}, Quantity: {self.quantity}, Date: {self.order_date}")

    def save_to_db(self):
        cursor.execute("""
            INSERT INTO hotel_management.Orders (sr_no, tbl_id, menu_id, quantity, order_date) 
            VALUES (?, ?, ?, ?, ?)""", 
            (self.sr_no, self.tbl_id, self.menu_item.menu_id, self.quantity, self.order_date))
        connection.commit()
        connection.close()

def generate_next_bill_id():
    cursor.execute("SELECT MAX(bill_id) FROM hotel_management.Final_bill")
    last_bill_id = cursor.fetchone()[0]

    if last_bill_id:
        # Assuming bill_id is of the form "BILL001", "BILL002", etc.
        last_number = int(last_bill_id.replace("BILL", ""))
        next_number = last_number + 1
    else:
        next_number = 1

    next_bill_id = f"BILL{str(next_number).zfill(3)}"  # e.g., "BILL001", "BILL002", etc.
    return next_bill_id

class FinalBill:
    
    def __init__(self, tbl_id, orders):
        self.bill_id = generate_next_bill_id()
        self.bill_date = datetime.now()
        self.tbl_id = tbl_id
        self.orders = orders

        self.total_amount = sum(order.menu_item.price * order.quantity for order in orders)
        self.gst_charges = self.total_amount * 0.09  # 09% GST
        self.final_amount = self.total_amount + self.gst_charges

        self.save_to_db()


    def generate_bill(self):
        print(f"---------------------------------")
        print(f"|   Welcome Hotel Name          |")
        print(f"|{self.bill_date.strftime('%Y-%m-%d')}       recpt: {self.bill_id}|")
        print(f"---------------------------------")
        print(f"|SR.   Menu           qnt   price  |")
        
        for idx, order in enumerate(self.orders, start=1):
            print(f"|{idx}     {order.menu_item.menu_name}    {order.quantity}    {order.menu_item.price * order.quantity:.2f}|")
        
        print(f"---------------------------------")
        print(f"|    total        {self.total_amount:.2f}  |")
        print(f"|including GST 09% = {self.gst_charges:.2f}  |")
        print(f"---------------------------------")
        print(f"|    Grand total        {self.final_amount:.2f}  |")
        print(f"---------------------------------")

        # Log bill generation
        logging.info(f"Bill generated: {self.bill_id} for Table {self.tbl_id} on {self.bill_date}")

    def save_to_db(self):
        cursor.execute("""
            INSERT INTO hotel_management.Final_bill (bill_id, bill_date, tbl_id, total_amount, gst_charges, final_amount) 
            VALUES (?, ?, ?, ?, ?, ?)""", 
            (self.bill_id, self.bill_date, self.tbl_id, self.total_amount, self.gst_charges, self.final_amount))
        connection.commit()
        connection.close()



