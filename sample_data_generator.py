#!/usr/bin/env python3
"""
Sample Data Generator for AI Expense Tracker
Generates realistic test data for demonstration and testing
"""

import sys
import os
from datetime import datetime, timedelta
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.database import ExpenseDatabase

def generate_sample_data(db, num_expenses=50):
    """Generate sample expense data"""
    
    print("Generating sample data...")
    print("-" * 60)
    
    # Sample data
    vegetables = ['Tomatoes', 'Potatoes', 'Onions', 'Carrots', 'Spinach', 'Cabbage']
    fruits = ['Apples', 'Bananas', 'Oranges', 'Mangoes', 'Grapes', 'Watermelon']
    dairy = ['Milk', 'Curd', 'Paneer', 'Cheese', 'Butter']
    groceries = ['Rice', 'Wheat Flour', 'Dal', 'Sugar', 'Tea', 'Oil', 'Salt']
    stationery = ['Pens', 'Notebooks', 'Files', 'Stapler', 'Paper', 'Markers']
    transport = ['Taxi', 'Uber', 'Auto', 'Metro', 'Bus', 'Parking']
    utilities = ['Electricity Bill', 'Water Bill', 'Internet', 'Mobile Recharge']
    food = ['Lunch', 'Dinner', 'Snacks', 'Coffee', 'Pizza', 'Burger']
    
    item_categories = {
        'Vegetables': vegetables,
        'Fruits': fruits,
        'Dairy': dairy,
        'Groceries': groceries,
        'Stationery': stationery,
        'Transport': transport,
        'Utilities': utilities,
        'Food & Beverages': food
    }
    
    employees = db.get_employees()
    entry_modes = ['Manual', 'Excel Import', 'Invoice OCR', 'Voice']
    
    # Generate expenses over the last 60 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=60)
    
    expenses_added = 0
    
    for i in range(num_expenses):
        # Random date in the range
        random_days = random.randint(0, 60)
        expense_date = (end_date - timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        # Random category and item
        category = random.choice(list(item_categories.keys()))
        item_name = random.choice(item_categories[category])
        
        # Random amount based on category
        if category in ['Vegetables', 'Fruits']:
            amount = round(random.uniform(20, 100), 2)
        elif category in ['Dairy', 'Groceries']:
            amount = round(random.uniform(30, 150), 2)
        elif category == 'Transport':
            amount = round(random.uniform(50, 300), 2)
        elif category == 'Utilities':
            amount = round(random.uniform(200, 1000), 2)
        elif category == 'Stationery':
            amount = round(random.uniform(25, 200), 2)
        else:
            amount = round(random.uniform(50, 500), 2)
        
        # Random employee
        employee = random.choice(employees)
        
        # Random entry mode
        entry_mode = random.choice(entry_modes)
        
        # Add to database
        db.add_expense(
            date=expense_date,
            item_name=item_name,
            category=category,
            amount=amount,
            employee_name=employee,
            entry_mode=entry_mode
        )
        
        expenses_added += 1
        
        if (i + 1) % 10 == 0:
            print(f"Added {i + 1} expenses...")
    
    print(f"✓ Added {expenses_added} sample expenses")
    
    return expenses_added

def generate_petty_cash_data(db, num_entries=10):
    """Generate sample petty cash receipts"""
    
    print("\nGenerating petty cash data...")
    print("-" * 60)
    
    sources = ['Company', 'Self', 'Office Advance', 'Reimbursement', 'Petty Cash Fund']
    
    end_date = datetime.now().date()
    
    cash_added = 0
    
    for i in range(num_entries):
        # Random date in the last 60 days
        random_days = random.randint(0, 60)
        cash_date = (end_date - timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        # Random amount
        amount = round(random.uniform(500, 5000), 2)
        
        # Random source
        received_from = random.choice(sources)
        
        # Random remarks
        remarks_options = [
            'Monthly petty cash',
            'Office expenses advance',
            'Reimbursement for previous expenses',
            'Emergency fund',
            ''
        ]
        remarks = random.choice(remarks_options)
        
        # Add to database
        db.add_petty_cash(
            date_received=cash_date,
            amount=amount,
            received_from=received_from,
            remarks=remarks
        )
        
        cash_added += 1
    
    print(f"✓ Added {cash_added} petty cash entries")
    
    return cash_added

def display_summary(db):
    """Display summary of generated data"""
    
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    
    # Get statistics
    total_expenses = db.get_total_expenses()
    total_cash = db.get_total_petty_cash_received()
    balance = db.get_petty_cash_balance()
    
    expenses_df = db.get_all_expenses()
    petty_cash_df = db.get_all_petty_cash()
    
    print(f"Total Expenses:        ₹{total_expenses:,.2f}")
    print(f"Total Cash Received:   ₹{total_cash:,.2f}")
    print(f"Petty Cash Balance:    ₹{balance:,.2f}")
    print(f"Number of Expenses:    {len(expenses_df)}")
    print(f"Number of Cash Entries: {len(petty_cash_df)}")
    
    print("\nExpenses by Category:")
    category_df = db.get_expenses_by_category()
    for _, row in category_df.iterrows():
        print(f"  {row['category']:<20} ₹{row['total']:>10,.2f}")
    
    print("\nExpenses by Employee:")
    employee_df = db.get_expenses_by_employee()
    for _, row in employee_df.iterrows():
        print(f"  {row['employee_name']:<20} ₹{row['total']:>10,.2f}")
    
    print("\nExpenses by Entry Mode:")
    mode_summary = expenses_df.groupby('entry_mode')['amount'].sum()
    for mode, total in mode_summary.items():
        print(f"  {mode:<20} ₹{total:>10,.2f}")
    
    print("\n" + "=" * 60)

def main():
    """Main function to generate sample data"""
    
    print("\n" + "=" * 60)
    print("AI Expense Tracker - Sample Data Generator")
    print("=" * 60)
    print()
    
    # Initialize database
    print("Initializing database...")
    db = ExpenseDatabase()
    print("✓ Database initialized")
    
    # Check if data already exists
    existing_expenses = db.get_all_expenses()
    if not existing_expenses.empty:
        print(f"\n⚠ Warning: Database already contains {len(existing_expenses)} expenses")
        response = input("Do you want to add more sample data? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Aborted.")
            return
    
    print()
    
    # Generate sample data
    num_expenses = 50
    num_cash_entries = 10
    
    expenses_added = generate_sample_data(db, num_expenses)
    cash_added = generate_petty_cash_data(db, num_cash_entries)
    
    # Display summary
    display_summary(db)
    
    print("\n✓ Sample data generation complete!")
    print("\nYou can now run the application:")
    print("  streamlit run main.py")
    print()

if __name__ == "__main__":
    main()
