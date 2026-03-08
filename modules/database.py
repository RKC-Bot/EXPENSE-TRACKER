import sqlite3
import pandas as pd
import hashlib
import os

class ExpenseDatabase:
    def __init__(self, db_path="db/expenses.db"):
        self.db_path = db_path
        self.is_memory = (db_path == ':memory:')
        self._conn = None  # Persistent connection for in-memory databases
        
        # Only create directory for non-memory databases
        if not self.is_memory and os.path.dirname(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.init_database()
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_connection(self):
        """Get database connection. For in-memory databases, use persistent connection."""
        if self.is_memory:
            if self._conn is None:
                self._conn = sqlite3.connect(self.db_path)
            return self._conn
        else:
            return sqlite3.connect(self.db_path)
    
    def close_connection(self, conn):
        """Close connection only for file-based databases"""
        if not self.is_memory and conn:
            conn.close()
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Staff/Users table (for authentication)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'staff',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Invoices table (for duplicate detection)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE NOT NULL,
                file_name TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                employee_name TEXT NOT NULL,
                invoice_id INTEGER,
                entry_mode TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
        ''')
        
        # Petty cash table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS petty_cash (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_received TEXT NOT NULL,
                amount REAL NOT NULL,
                received_from TEXT NOT NULL,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default categories if empty
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            default_categories = [
                'Vegetables', 'Fruits', 'Dairy', 'Groceries', 
                'Stationery', 'Transport', 'Utilities', 'Miscellaneous'
            ]
            for cat in default_categories:
                cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
        
        # Insert default admin user if no staff exists
        cursor.execute("SELECT COUNT(*) FROM staff")
        if cursor.fetchone()[0] == 0:
            admin_password = self._hash_password("admin@123")
            cursor.execute(
                "INSERT INTO staff (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                ("admin", admin_password, "Administrator", "admin")
            )

        # Staff permissions migration (for existing databases)
        cursor.execute("PRAGMA table_info(staff)")
        staff_columns = [row[1] for row in cursor.fetchall()]
        if "can_edit_expenses" not in staff_columns:
            cursor.execute("ALTER TABLE staff ADD COLUMN can_edit_expenses BOOLEAN DEFAULT 0")
        if "can_delete_expenses" not in staff_columns:
            cursor.execute("ALTER TABLE staff ADD COLUMN can_delete_expenses BOOLEAN DEFAULT 0")
        if "full_db_access" not in staff_columns:
            cursor.execute("ALTER TABLE staff ADD COLUMN full_db_access BOOLEAN DEFAULT 0")

        # Ensure admin always has full rights.
        cursor.execute("""
            UPDATE staff
            SET can_edit_expenses = 1,
                can_delete_expenses = 1,
                full_db_access = 1
            WHERE username = 'admin'
        """)
        
        # Insert default employees if empty
        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            default_employees = ['John Doe', 'Jane Smith']
            for emp in default_employees:
                cursor.execute("INSERT OR IGNORE INTO employees (name) VALUES (?)", (emp,))
        
        conn.commit()
        
        # Only close connection for file-based databases
        if not self.is_memory:
            self.close_connection(conn)
    
    # Category Management
    def add_category(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            return True, "Category added successfully"
        except sqlite3.IntegrityError:
            return False, "Category already exists"
        finally:
            self.close_connection(conn)
    
    def delete_category(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE name = ?", (name,))
        conn.commit()
        self.close_connection(conn)
        return True, "Category deleted successfully"
    
    def get_categories(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT name FROM categories ORDER BY name", conn)
        self.close_connection(conn)
        return df['name'].tolist()
    
    # Employee Management
    def add_employee(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        if name.strip().lower() == "admin":
            self.close_connection(conn)
            return False, "Admin cannot be added as an employee"
        try:
            cursor.execute("INSERT INTO employees (name) VALUES (?)", (name,))
            conn.commit()
            return True, "Employee added successfully"
        except sqlite3.IntegrityError:
            return False, "Employee already exists"
        finally:
            self.close_connection(conn)
    
    def delete_employee(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE name = ?", (name,))
        conn.commit()
        self.close_connection(conn)
        return True, "Employee deleted successfully"
    
    def update_employee(self, old_name, new_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE employees SET name = ? WHERE name = ?", (new_name, old_name))
            conn.commit()
            return True, "Employee updated successfully"
        except sqlite3.IntegrityError:
            return False, "Employee name already exists"
        finally:
            self.close_connection(conn)
    
    def get_employees(self):
        conn = self.get_connection()
        df = pd.read_sql_query(
            "SELECT name FROM employees WHERE LOWER(name) != 'admin' ORDER BY name",
            conn
        )
        self.close_connection(conn)
        return df['name'].tolist()
    
    # Staff/User Management
    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = self._hash_password(password)
        cursor.execute(
            """SELECT id, username, full_name, role,
                      COALESCE(can_edit_expenses, 0),
                      COALESCE(can_delete_expenses, 0),
                      COALESCE(full_db_access, 0)
               FROM staff
               WHERE username = ? AND password = ? AND is_active = 1""",
            (username, hashed_password)
        )
        user = cursor.fetchone()
        self.close_connection(conn)
        return user  # (id, username, full_name, role, can_edit, can_delete, full_db) or None
    
    def add_staff(self, username, password, full_name, role='staff'):
        """Add new staff member - admin only"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            hashed_password = self._hash_password(password)
            is_admin = (role == 'admin')
            cursor.execute(
                """INSERT INTO staff
                   (username, password, full_name, role, can_edit_expenses, can_delete_expenses, full_db_access)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    username,
                    hashed_password,
                    full_name,
                    role,
                    1 if is_admin else 0,
                    1 if is_admin else 0,
                    1 if is_admin else 0
                )
            )
            conn.commit()
            staff_id = cursor.lastrowid
            self.close_connection(conn)
            return True, "Staff member added successfully", staff_id
        except sqlite3.IntegrityError:
            self.close_connection(conn)
            return False, "Username already exists", None
        except Exception as e:
            self.close_connection(conn)
            return False, str(e), None
    
    def update_staff(self, username, full_name=None, role=None, is_active=None):
        """Update staff member details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            updates = []
            values = []
            
            if full_name:
                updates.append("full_name = ?")
                values.append(full_name)
            if role:
                updates.append("role = ?")
                values.append(role)
            if is_active is not None:
                updates.append("is_active = ?")
                values.append(is_active)
            
            if updates:
                update_str = ", ".join(updates)
                values.append(username)
                cursor.execute(f"UPDATE staff SET {update_str} WHERE username = ?", values)
                conn.commit()
                self.close_connection(conn)
                return True, "Staff member updated successfully"
            
            self.close_connection(conn)
            return False, "No updates provided"
        except Exception as e:
            self.close_connection(conn)
            return False, str(e)
    
    def reset_staff_password(self, username, new_password):
        """Reset staff password - admin only"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            hashed_password = self._hash_password(new_password)
            cursor.execute(
                "UPDATE staff SET password = ? WHERE username = ?",
                (hashed_password, username)
            )
            conn.commit()
            self.close_connection(conn)
            return True, "Password reset successfully"
        except Exception as e:
            self.close_connection(conn)
            return False, str(e)
    
    def delete_staff(self, username):
        """Delete staff member - admin only"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Prevent deletion of admin account
        if username == "admin":
            self.close_connection(conn)
            return False, "Cannot delete admin account"
        
        try:
            cursor.execute("DELETE FROM staff WHERE username = ?", (username,))
            conn.commit()
            self.close_connection(conn)
            return True, "Staff member deleted successfully"
        except Exception as e:
            self.close_connection(conn)
            return False, str(e)
    
    def get_all_staff(self):
        """Get all staff members"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            """SELECT id, username, full_name, role, is_active,
                      COALESCE(can_edit_expenses, 0) as can_edit_expenses,
                      COALESCE(can_delete_expenses, 0) as can_delete_expenses,
                      COALESCE(full_db_access, 0) as full_db_access,
                      created_at
               FROM staff ORDER BY username""",
            conn
        )
        self.close_connection(conn)
        return df

    def update_staff_permissions(self, username, can_edit_expenses=None, can_delete_expenses=None, full_db_access=None):
        """Update permission flags for a staff account."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            updates = []
            values = []
            if can_edit_expenses is not None:
                updates.append("can_edit_expenses = ?")
                values.append(1 if can_edit_expenses else 0)
            if can_delete_expenses is not None:
                updates.append("can_delete_expenses = ?")
                values.append(1 if can_delete_expenses else 0)
            if full_db_access is not None:
                updates.append("full_db_access = ?")
                values.append(1 if full_db_access else 0)

            if not updates:
                self.close_connection(conn)
                return False, "No permission updates provided"

            values.append(username)
            cursor.execute(f"UPDATE staff SET {', '.join(updates)} WHERE username = ?", values)
            conn.commit()
            self.close_connection(conn)
            return True, "Permissions updated successfully"
        except Exception as e:
            self.close_connection(conn)
            return False, str(e)
    
    def disable_staff(self, username):
        """Disable staff account without deleting"""
        return self.update_staff(username, is_active=False)
    
    def enable_staff(self, username):
        """Enable disabled staff account"""
        return self.update_staff(username, is_active=True)
    
    # Invoice Management
    def check_duplicate_invoice(self, file_hash):
        """Check if invoice already exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, file_name FROM invoices WHERE file_hash = ?", (file_hash,))
        result = cursor.fetchone()
        self.close_connection(conn)
        return result
    
    def add_invoice(self, file_hash, file_name):
        """Add new invoice"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO invoices (file_hash, file_name) VALUES (?, ?)", 
                          (file_hash, file_name))
            conn.commit()
            invoice_id = cursor.lastrowid
            self.close_connection(conn)
            return invoice_id
        except sqlite3.IntegrityError:
            self.close_connection(conn)
            return None
    
    # Expense Management
    def update_expense(self, expense_id, date, item_name, category, amount, employee_name):
        """Update an existing expense record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE expenses
            SET date = ?, item_name = ?, category = ?, amount = ?, employee_name = ?
            WHERE id = ?
        ''', (date, item_name, category, amount, employee_name, expense_id))
        conn.commit()
        self.close_connection(conn)
        return True

    def delete_expense(self, expense_id):
        """Delete an expense by id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        self.close_connection(conn)
        return deleted
    
    def add_expense(self, date, item_name, category, amount, employee_name, 
                    invoice_id=None, entry_mode='Manual'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (date, item_name, category, amount, employee_name, 
                                 invoice_id, entry_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, item_name, category, amount, employee_name, invoice_id, entry_mode))
        conn.commit()
        expense_id = cursor.lastrowid
        self.close_connection(conn)
        return expense_id
    
    def get_all_expenses(self):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT id, date, item_name, category, amount, employee_name, 
                   entry_mode, created_at
            FROM expenses 
            ORDER BY date DESC
        ''', conn)
        self.close_connection(conn)
        return df
    
    def get_expenses_by_date_range(self, start_date, end_date):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT * FROM expenses 
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        ''', conn, params=(start_date, end_date))
        self.close_connection(conn)
        return df
    
    def get_total_expenses(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")
        total = cursor.fetchone()[0]
        self.close_connection(conn)
        return total
    
    def get_expenses_by_category(self):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT category, SUM(amount) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        ''', conn)
        self.close_connection(conn)
        return df
    
    def get_expenses_by_employee(self):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT employee_name, SUM(amount) as total
            FROM expenses
            GROUP BY employee_name
            ORDER BY total DESC
        ''', conn)
        self.close_connection(conn)
        return df
    
    # Petty Cash Management
    def add_petty_cash(self, date_received, amount, received_from, remarks=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO petty_cash (date_received, amount, received_from, remarks)
            VALUES (?, ?, ?, ?)
        ''', (date_received, amount, received_from, remarks))
        conn.commit()
        self.close_connection(conn)
        return True
    
    def get_petty_cash_balance(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total received
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM petty_cash")
        total_received = cursor.fetchone()[0]
        
        # Total spent
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")
        total_spent = cursor.fetchone()[0]
        
        self.close_connection(conn)
        return total_received - total_spent
    
    def get_all_petty_cash(self):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT * FROM petty_cash 
            ORDER BY date_received DESC
        ''', conn)
        self.close_connection(conn)
        return df
    
    def get_total_petty_cash_received(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM petty_cash")
        total = cursor.fetchone()[0]
        self.close_connection(conn)
        return total

# Utility function to calculate file hash
def calculate_file_hash(file_content):
    """Calculate SHA256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()
