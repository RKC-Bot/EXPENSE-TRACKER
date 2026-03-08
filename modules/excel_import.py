import pandas as pd
from datetime import datetime
import io
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Protection

class ExcelImporter:
    """
    Import expenses from Excel files.
    Expected columns: Date | Item | Category | Amount | Employee
    """
    
    def __init__(self):
        self.required_columns = ['Date', 'Item', 'Category', 'Amount', 'Employee']
    
    def validate_excel(self, df):
        """Validate that Excel file has required columns"""
        # Check if required columns exist (case-insensitive)
        df_columns_lower = [col.lower() for col in df.columns]
        required_lower = [col.lower() for col in self.required_columns]
        
        missing_columns = []
        for req_col in required_lower:
            if req_col not in df_columns_lower:
                missing_columns.append(req_col)
        
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"
        
        return True, "Valid"
    
    def normalize_column_names(self, df):
        """Normalize column names to match expected format"""
        # Create a mapping of lowercase to original columns
        col_mapping = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'date' in col_lower:
                col_mapping[col] = 'Date'
            elif 'item' in col_lower or 'description' in col_lower or 'particular' in col_lower:
                col_mapping[col] = 'Item'
            elif 'category' in col_lower or 'type' in col_lower:
                col_mapping[col] = 'Category'
            elif 'amount' in col_lower or 'price' in col_lower or 'cost' in col_lower:
                col_mapping[col] = 'Amount'
            elif 'employee' in col_lower or 'person' in col_lower or 'name' in col_lower:
                col_mapping[col] = 'Employee'
        
        # Rename columns
        df = df.rename(columns=col_mapping)
        return df
    
    def clean_and_validate_data(self, df):
        """Clean and validate the data"""
        errors = []
        cleaned_rows = []
        
        for idx, row in df.iterrows():
            try:
                # Parse date
                if pd.isna(row['Date']):
                    date_str = datetime.now().strftime('%Y-%m-%d')
                else:
                    date_obj = pd.to_datetime(row['Date'], dayfirst=True)
                    date_str = date_obj.strftime('%Y-%m-%d')
                
                # Get item name
                item = str(row['Item']).strip() if not pd.isna(row['Item']) else 'Unknown'
                
                # Get category
                category = str(row['Category']).strip() if not pd.isna(row['Category']) else 'Miscellaneous'
                
                # Parse amount
                amount = float(row['Amount']) if not pd.isna(row['Amount']) else 0.0
                
                # Get employee
                employee = str(row['Employee']).strip() if not pd.isna(row['Employee']) else 'Unknown'
                
                # Validate amount
                if amount <= 0:
                    errors.append(f"Row {idx + 2}: Invalid amount ({amount})")
                    continue
                
                cleaned_rows.append({
                    'date': date_str,
                    'item_name': item,
                    'category': category,
                    'amount': amount,
                    'employee_name': employee
                })
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        return cleaned_rows, errors
    
    def import_from_excel(self, file):
        """
        Import expenses from Excel file.
        Returns: (success, data/errors, message)
        """
        try:
            # Read Excel file
            if isinstance(file, bytes):
                df = pd.read_excel(io.BytesIO(file))
            else:
                df = pd.read_excel(file)
            
            # Check if empty
            if df.empty:
                return False, None, "Excel file is empty"
            
            # Normalize column names
            df = self.normalize_column_names(df)
            
            # Validate columns
            is_valid, message = self.validate_excel(df)
            if not is_valid:
                return False, None, message
            
            # Clean and validate data
            cleaned_data, errors = self.clean_and_validate_data(df)
            
            if not cleaned_data:
                error_msg = "No valid rows found.\n" + "\n".join(errors[:5])
                return False, None, error_msg
            
            # Return success with data and any errors
            success_msg = f"Successfully imported {len(cleaned_data)} expenses"
            if errors:
                success_msg += f"\nWarnings: {len(errors)} rows skipped"
            
            return True, cleaned_data, success_msg
            
        except Exception as e:
            return False, None, f"Error reading Excel file: {str(e)}"
    
    def create_sample_excel(self, output_path=None):
        """Create a sample Excel template for reference"""
        sample_data = {
            'Date': ['2024-01-15', '2024-01-15', '2024-01-16'],
            'Item': ['Tomatoes', 'Milk', 'Notebook'],
            'Category': ['Vegetables', 'Dairy', 'Stationery'],
            'Amount': [50, 60, 25],
            'Employee': ['John Doe', 'Jane Smith', 'John Doe']
        }
        
        df = pd.DataFrame(sample_data)
        
        if output_path:
            df.to_excel(output_path, index=False)
            return output_path
        else:
            # Return as bytes
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Expenses')
            output.seek(0)
            return output.getvalue()
    
    def export_to_excel(self, expenses_df, output_path=None):
        """Export expenses to Excel format"""
        try:
            if output_path:
                expenses_df.to_excel(output_path, index=False)
                return True, output_path
            else:
                # Return as bytes
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    expenses_df.to_excel(writer, index=False, sheet_name='Expenses')
                output.seek(0)
                return True, output.getvalue()
        except Exception as e:
            return False, f"Error exporting to Excel: {str(e)}"

def create_expense_template(is_admin=False, staff_name=None, employee_options=None):
    """Create a template Excel file for users to fill"""
    category_options = [
        'Vegetables', 'Fruits', 'Dairy', 'Groceries',
        'Stationery', 'Transport', 'Utilities', 'Miscellaneous'
    ]
    employee_options = employee_options or []

    if is_admin:
        employee_values = ["", "", ""]
    else:
        fixed_staff_name = (staff_name or "Staff User").strip() or "Staff User"
        employee_values = [fixed_staff_name, fixed_staff_name, fixed_staff_name]

    template_data = {
        'Date': [
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 3)
        ],
        'Item': ['Example Item 1', 'Example Item 2', 'Example Item 3'],
        'Category': ['Groceries', 'Transport', 'Utilities'],
        'Amount': [100, 200, 150],
        'Employee': employee_values
    }
    
    df = pd.DataFrame(template_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Expenses Template')

        sheet = writer.book['Expenses Template']
        list_sheet = writer.book.create_sheet(title='Lists')
        for idx, category in enumerate(category_options, start=1):
            list_sheet[f'A{idx}'] = category
        for idx, employee_name in enumerate(employee_options, start=1):
            list_sheet[f'B{idx}'] = employee_name
        list_sheet.sheet_state = 'hidden'

        # Format Date column as dd/mm/yy for user entry.
        for row_idx in range(2, 2001):
            sheet[f'A{row_idx}'].number_format = 'DD/MM/YY'
            sheet[f'A{row_idx}'].protection = Protection(locked=False)
            sheet[f'B{row_idx}'].protection = Protection(locked=False)
            sheet[f'C{row_idx}'].protection = Protection(locked=False)
            sheet[f'D{row_idx}'].protection = Protection(locked=False)

        # Add category dropdown list in Category column.
        category_validation = DataValidation(
            type="list",
            formula1=f"=Lists!$A$1:$A${len(category_options)}",
            allow_blank=True,
            showDropDown=False
        )
        sheet.add_data_validation(category_validation)
        category_validation.add('C2:C2000')

        if is_admin and employee_options:
            employee_validation = DataValidation(
                type="list",
                formula1=f"=Lists!$B$1:$B${len(employee_options)}",
                allow_blank=True,
                showDropDown=False
            )
            sheet.add_data_validation(employee_validation)
            employee_validation.add('E2:E2000')
            for row_idx in range(2, 2001):
                sheet[f'E{row_idx}'].protection = Protection(locked=False)
        else:
            for row_idx in range(2, 2001):
                sheet[f'E{row_idx}'] = employee_values[0]
                sheet[f'E{row_idx}'].protection = Protection(locked=True)

        sheet.protection.sheet = True
        
        # Add instructions sheet
        employee_instruction = (
            '5. Select employee from dropdown in Employee column (Admin template)'
            if is_admin else
            '5. Employee column is auto-filled and locked to your account name'
        )
        instructions = pd.DataFrame({
            'Instructions': [
                '1. Fill in the Date column with dates in DD/MM/YY format',
                '2. Fill in the Item column with the item/service name',
                '3. Select Category from the dropdown list in Category column',
                '4. Fill in the Amount column with numeric values only',
                employee_instruction,
                '6. Delete the example rows and add your own data',
                '7. Save and upload this file to the application'
            ]
        })
        instructions.to_excel(writer, index=False, sheet_name='Instructions')
    
    output.seek(0)
    return output.getvalue()
