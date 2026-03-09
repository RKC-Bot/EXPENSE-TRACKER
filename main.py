import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import sys

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.database import ExpenseDatabase, calculate_file_hash
from modules.categorizer import AIExpenseCategorizer
from modules.invoice_ocr import InvoiceOCR, extract_from_pdf
from modules.voice_entry import VoiceExpenseEntry
from modules.excel_import import ExcelImporter, create_expense_template
from modules.reports import ExpenseReports

# Page configuration
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = ExpenseDatabase()
if 'categorizer' not in st.session_state:
    st.session_state.categorizer = AIExpenseCategorizer()
if 'ocr' not in st.session_state:
    st.session_state.ocr = None  # Lazy initialization
if 'voice' not in st.session_state:
    st.session_state.voice = None  # Lazy initialization
if 'excel_importer' not in st.session_state:
    st.session_state.excel_importer = ExcelImporter()
if 'reports' not in st.session_state:
    st.session_state.reports = ExpenseReports(st.session_state.db)

# Lazy initialization helper
def get_ocr():
    if st.session_state.ocr is None:
        st.session_state.ocr = InvoiceOCR()
    return st.session_state.ocr

def get_voice():
    if st.session_state.voice is None:
        st.session_state.voice = VoiceExpenseEntry()
    return st.session_state.voice

# Admin authentication
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'admin_username' not in st.session_state:
    st.session_state.admin_username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_full_name' not in st.session_state:
    st.session_state.user_full_name = None
if 'can_edit_expenses' not in st.session_state:
    st.session_state.can_edit_expenses = False
if 'can_delete_expenses' not in st.session_state:
    st.session_state.can_delete_expenses = False
if 'full_db_access' not in st.session_state:
    st.session_state.full_db_access = False

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Login Page
if not st.session_state.admin_logged_in:
    st.markdown('<h1 class="main-header">💰 Expense Tracker</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### 🔐 Staff Login")
        st.info("Login with your assigned user ID and password.")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit_btn = st.form_submit_button("Login", use_container_width=True)
            
            if submit_btn:
                user = st.session_state.db.authenticate_user(username, password)
                if user:
                    user_id, uname, full_name, role, can_edit, can_delete, full_db_access = user
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = uname
                    st.session_state.user_role = role
                    st.session_state.user_id = user_id
                    st.session_state.user_full_name = full_name
                    st.session_state.can_edit_expenses = bool(can_edit)
                    st.session_state.can_delete_expenses = bool(can_delete)
                    st.session_state.full_db_access = bool(full_db_access)
                    st.success("✅ Login successful! Reloading...")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()  # Stop execution until user logs in

# Sidebar menu (only shown after login)
st.sidebar.title("📊 Navigation")

# Logout button in sidebar
if st.sidebar.button("🚪 Logout", type="secondary"):
    st.session_state.admin_logged_in = False
    st.session_state.admin_username = None
    st.session_state.user_role = None
    st.session_state.user_id = None
    st.session_state.user_full_name = None
    st.session_state.can_edit_expenses = False
    st.session_state.can_delete_expenses = False
    st.session_state.full_db_access = False
    st.rerun()

st.sidebar.markdown(
    f"**Logged in as:** {st.session_state.admin_username} ({st.session_state.user_role}) 🔐"
)
st.sidebar.divider()

menu_options = [
    "🏠 Dashboard",
    "➕ Add Expense",
    "📋 Manage Expenses",
    "📝 Text Entry",
    "📄 Upload Invoice",
    "📊 Upload Excel",
    "📸 Camera Capture",
    "💵 Cash Received",
    "📁 Manage Categories",
    "📈 Reports"
]
if st.session_state.user_role == "admin":
    menu_options.append("👥 Manage Employees")
    menu_options.append("👤 Manage Staff")
    menu_options.append("🧠 Category Rules")
selected_menu = st.sidebar.radio("Menu", menu_options)

is_admin_user = st.session_state.user_role == "admin"
current_staff_name = (
    st.session_state.user_full_name
    or st.session_state.admin_username
    or "Staff User"
)
staff_can_edit = is_admin_user or st.session_state.can_edit_expenses
staff_can_delete = is_admin_user or st.session_state.can_delete_expenses
has_full_db_access = is_admin_user or st.session_state.full_db_access


def scoped_expenses_df():
    df = st.session_state.db.get_all_expenses()
    if has_full_db_access:
        return df
    if df.empty:
        return df
    return df[df["employee_name"].str.lower() == current_staff_name.lower()]

# Main content
if selected_menu == "🏠 Dashboard":
    st.markdown('<h1 class="main-header">💰 Expense Tracker</h1>', unsafe_allow_html=True)
    
    # Get summary stats (scoped for staff without full DB access)
    scoped_df = scoped_expenses_df()
    if has_full_db_access:
        stats = st.session_state.reports.get_summary_stats()
    else:
        stats = {
            'total_expenses': scoped_df['amount'].sum() if not scoped_df.empty else 0,
            'petty_cash_balance': 0,
            'total_cash_received': 0,
            'total_transactions': len(scoped_df) if not scoped_df.empty else 0,
            'avg_expense': scoped_df['amount'].mean() if not scoped_df.empty else 0,
        }
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Expenses", f"₹{stats['total_expenses']:,.2f}")
    
    with col2:
        st.metric("Cash Balance", f"₹{stats['petty_cash_balance']:,.2f}" if has_full_db_access else "Restricted")
    
    with col3:
        st.metric("Total Cash Received", f"₹{stats['total_cash_received']:,.2f}" if has_full_db_access else "Restricted")
    
    with col4:
        st.metric("Total Transactions", stats['total_transactions'])
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Expenses by Category")
        if has_full_db_access:
            fig = st.session_state.reports.create_category_pie_chart()
        else:
            fig = None
            if not scoped_df.empty:
                category_df = scoped_df.groupby('category', as_index=False)['amount'].sum().rename(columns={'amount': 'total'})
                import plotly.express as px
                fig = px.pie(category_df, values='total', names='category', title='Expenses by Category')
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available")
    
    with col2:
        st.subheader("👥 Expenses by Employee")
        if has_full_db_access:
            fig = st.session_state.reports.create_employee_bar_chart()
        else:
            fig = None
            if not scoped_df.empty:
                employee_df = scoped_df.groupby('employee_name', as_index=False)['amount'].sum().rename(columns={'amount': 'total'})
                import plotly.express as px
                fig = px.bar(employee_df, x='employee_name', y='total', title='Expenses by Employee')
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available")
    
    # Recent expenses
    st.subheader("📋 Recent Expenses")
    expenses_df = scoped_df
    if not expenses_df.empty:
        st.dataframe(expenses_df.head(10), use_container_width=True)
    else:
        st.info("No expenses recorded yet")

elif selected_menu == "➕ Add Expense":
    st.title("➕ Add New Expense")
    
    # Get categories and employees
    categories = st.session_state.db.get_categories()
    employees = st.session_state.db.get_employees()
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("Item Name*", placeholder="e.g., Tomatoes, Milk")
            category = st.selectbox("Category*", categories)
            amount = st.number_input("Amount (₹)*", min_value=0.0, step=0.01)
        
        with col2:
            if has_full_db_access:
                employee = st.selectbox("Employee*", employees)
            else:
                employee = current_staff_name
                st.text_input("Employee*", value=employee, disabled=True)
            expense_date = st.date_input("Date*", value=date.today())
        
        submitted = st.form_submit_button("Add Expense", type="primary")
        
        if submitted:
            if item_name and amount > 0:
                # Add to database
                expense_id = st.session_state.db.add_expense(
                    date=expense_date.strftime('%Y-%m-%d'),
                    item_name=item_name,
                    category=category,
                    amount=amount,
                    employee_name=employee,
                    entry_mode='Manual'
                )
                
                st.success(f"✅ Expense added successfully! (ID: {expense_id})")
                st.balloons()
            else:
                st.error("Please fill all required fields")
    
    # Auto-categorize suggestion
    st.divider()
    st.subheader("🤖 AI Category Suggestion")
    test_item = st.text_input("Test item for auto-categorization:", placeholder="Enter item name")
    if test_item:
        suggested_cat, confidence = st.session_state.categorizer.get_category_confidence(test_item)
        st.info(f"Suggested Category: **{suggested_cat}** (Confidence: {confidence:.1f}%)")

elif selected_menu == "📝 Text Entry":
    st.title("📝 Text Entry")
    st.info("✏️ Enter expense details as text. Simply describe the expense and the app will extract the item and amount.")
    st.divider()
    if "text_entry_parsed" not in st.session_state:
        st.session_state.text_entry_parsed = None
    if "clear_text_entry_input" not in st.session_state:
        st.session_state.clear_text_entry_input = False
    if st.session_state.clear_text_entry_input:
        st.session_state.text_entry_input = ""
        st.session_state.clear_text_entry_input = False
    
    # Text input mode
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📝 Describe your expense")
        st.markdown("""
        **Examples of what you can enter:**
        - "Bought tomatoes for 250 rupees"
        - "Spent 100 on milk for groceries"
        - "Taxi fare 200 rupees"
        - "Purchased notebook 25 rupees"
        """)
    
    # Text input for expense description
    voice_text = st.text_area(
        "📝 Expense Description",
        placeholder="E.g., 'Bought 2kg tomatoes for 250 rupees'",
        height=80,
        help="Describe your expense in natural language",
        key="text_entry_input"
    )
    
    # Try to parse text input
    if st.button("✏️ Process Text Entry", type="primary", use_container_width=True):
        with st.spinner("Processing text input..."):
            if not voice_text or not voice_text.strip():
                st.warning("Please enter expense details before processing.")
                st.session_state.text_entry_parsed = None
            else:
                # Parse the text
                parsed = get_voice().parse_expense_from_text(voice_text)
            
                if parsed['success']:
                    st.session_state.text_entry_parsed = parsed
                else:
                    st.session_state.text_entry_parsed = None
                    st.warning("⚠️ Could not parse expense. Please try again with more details.")
                    st.info(f"Raw text received: {voice_text}")
    
    parsed = st.session_state.text_entry_parsed
    if parsed:
        st.success("✅ Parsed Successfully")
        
        # Show parsed data
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Item", parsed['item_name'])
        with col2:
            st.metric("Amount (₹)", f"{parsed['amount']:.2f}")
        
        st.divider()
        
        # Allow user to confirm and edit
        with st.form("voice_expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                final_item = st.text_input(
                    "Item Name",
                    value=parsed['item_name'],
                    help="Edit if needed"
                )
                categories = st.session_state.db.get_categories()
                suggested = st.session_state.categorizer.categorize(final_item) if final_item else None
                default_idx = categories.index(suggested) if suggested in categories else 0
                final_category = st.selectbox(
                    "Category",
                    categories,
                    index=default_idx
                )
            
            with col2:
                final_amount = st.number_input(
                    "Amount (₹)",
                    value=float(parsed['amount']),
                    min_value=0.0,
                    step=0.01,
                    help="Edit if needed"
                )
                if has_full_db_access:
                    final_employee = st.selectbox(
                        "Employee",
                        st.session_state.db.get_employees() or ["Default"]
                    )
                else:
                    final_employee = current_staff_name
                    st.text_input("Employee", value=final_employee, disabled=True)
                final_date = st.date_input(
                    "Date",
                    value=datetime.now().date()
                )
            
            submitted = st.form_submit_button("✅ Add Expense", type="primary", use_container_width=True)
            
            if submitted and final_item and final_amount > 0:
                st.session_state.db.add_expense(
                    final_date.strftime('%Y-%m-%d'),
                    final_item,
                    final_category,
                    final_amount,
                    final_employee,
                    entry_mode='Text Entry'
                )
                st.session_state.text_entry_parsed = None
                st.session_state.clear_text_entry_input = True
                st.success(f"✅ Expense added: {final_item} - ₹{final_amount:.2f}")
                st.balloons()
                st.rerun()
    
    st.divider()
    st.subheader("💡 Tips for Text Entry")
    st.markdown("""
    1. **Be specific**: Include both item and amount
    2. **Use clear amount**: Say \"rupees\" or \"Rs\" after the number
    3. **Complete sentence**: \"Bought X for Y rupees\" works best
    4. **Examples that work**:
       - ✅ \"Purchased 1kg tomatoes for 250 rupees\"
       - ✅ \"Spent 150 on groceries\"
       - ✅ \"Taxi fare was 200 rupees\"
       - ❌ \"500\" (need item name)
       - ❌ \"Groceries\" (need amount)
    """)

elif selected_menu == "📄 Upload Invoice":
    st.title("📄 Upload Invoice")
    
    st.info("📤 Upload an invoice in any format (JPG, PNG, PDF, DOCX, DOC). The system will extract items and amounts automatically.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "📁 Choose invoice file",
            type=['jpg', 'jpeg', 'png', 'pdf', 'docx', 'doc', 'bmp', 'tiff', 'gif'],
            help="Supported formats: JPG, PNG, PDF, DOCX, DOC, BMP, TIFF, GIF"
        )
    
    with col2:
        prefer_handwriting = st.checkbox("🖊️ Use handwriting recognition", value=False)
    
    if uploaded_file:
        st.success(f"✅ File selected: {uploaded_file.name}")
        
        # Calculate file hash
        file_content = uploaded_file.read()
        file_hash = calculate_file_hash(file_content)
        
        # Check for duplicates
        duplicate = st.session_state.db.check_duplicate_invoice(file_hash)
        
        if duplicate:
            st.error(f"⚠️ Duplicate invoice detected! Already uploaded: {duplicate[1]}")
        else:
            st.info(f"✅ New invoice - Ready to process")
            
            # Display invoice preview
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff']:
                try:
                    st.image(file_content, caption=f"Invoice Preview: {uploaded_file.name}", width=400)
                except:
                    st.warning("Could not preview image")
            elif file_extension == 'pdf':
                st.info("📄 PDF file uploaded. Click 'Process Invoice' to extract text.")
            elif file_extension in ['docx', 'doc']:
                st.info("📝 Word document uploaded. Click 'Process Invoice' to extract text.")
            
            # Save invoice file
            invoice_dir = "data/invoices"
            os.makedirs(invoice_dir, exist_ok=True)
            file_path = os.path.join(invoice_dir, f"{file_hash[:16]}_{uploaded_file.name}")
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            if st.button("🔍 Process Invoice & Extract Items", type="primary", use_container_width=True):
                with st.spinner("Processing invoice with OCR..."):
                    try:
                        # Process based on file type
                        result = None
                        
                        if file_extension == 'pdf':
                            result = extract_from_pdf(file_content)
                        elif file_extension in ['docx', 'doc']:
                            # Handle Word documents
                            try:
                                from docx import Document
                                from io import BytesIO
                                doc = Document(BytesIO(file_content))
                                extracted_text = '\n'.join([para.text for para in doc.paragraphs])
                                result = {'text': extracted_text, 'items': []}
                            except:
                                st.error("Could not read Word document. Ensure python-docx is installed.")
                        else:
                            # Handle images
                            from PIL import Image
                            import io
                            image = Image.open(io.BytesIO(file_content))
                            result = get_ocr().process_invoice(image, prefer_handwriting)
                        
                        if result and result.get('text'):
                            # Add invoice to database
                            invoice_id = st.session_state.db.add_invoice(file_hash, uploaded_file.name)
                            
                            st.success(f"✅ Invoice processed successfully!")
                            
                            # Show extracted text
                            with st.expander("📋 View Extracted Text"):
                                st.text(result['text'])
                            
                            # Display items if found
                            if result.get('items'):
                                st.subheader("📦 Extracted Items")
                                st.info(f"Found {len(result['items'])} items")
                                parsed_rows = result.get('parsed_items') or [
                                    {"item_name": item, "amount": amount, "category": None}
                                    for item, amount in result['items']
                                ]
                                parsed_preview_df = pd.DataFrame(parsed_rows)
                                if not parsed_preview_df.empty:
                                    if "confidence" not in parsed_preview_df.columns:
                                        parsed_preview_df["confidence"] = 0.0
                                    parsed_preview_df = parsed_preview_df.rename(
                                        columns={
                                            "item_name": "Item",
                                            "amount": "Amount",
                                            "category": "Category",
                                            "confidence": "Confidence (%)",
                                        }
                                    )
                                    st.markdown("**🧠 Parser Confidence Panel**")
                                    st.dataframe(parsed_preview_df, use_container_width=True)
                                    low_conf_count = int((parsed_preview_df["Confidence (%)"] < 60).sum())
                                    if low_conf_count > 0:
                                        st.warning(f"⚠️ {low_conf_count} item(s) have low confidence (<60%). Please review before adding.")
                                
                                employees = st.session_state.db.get_employees()
                                if st.button("✅ Add All Extracted Items", key="add_all_upload_items"):
                                    added = 0
                                    for row in parsed_rows:
                                        item_name = row.get("item_name", "")
                                        amount = float(row.get("amount", 0))
                                        suggested_cat = row.get("category") or st.session_state.categorizer.categorize(item_name) or "Miscellaneous"
                                        employee_name = current_staff_name if not has_full_db_access else (employees[0] if employees else current_staff_name)
                                        st.session_state.db.add_expense(
                                            date=date.today().strftime('%Y-%m-%d'),
                                            item_name=item_name,
                                            category=suggested_cat,
                                            amount=float(amount),
                                            employee_name=employee_name,
                                            invoice_id=invoice_id,
                                            entry_mode='Invoice OCR'
                                        )
                                        added += 1
                                    st.success(f"✅ Added {added} items from invoice.")
                                    st.rerun()
                                
                                # Create form for each item
                                for idx, row in enumerate(parsed_rows):
                                    with st.form(f"item_form_{idx}"):
                                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                                        
                                        with col1:
                                            item = row.get("item_name", "")
                                            item_name = st.text_input("Item", value=item, key=f"item_{idx}")
                                        
                                        with col2:
                                            # Auto-categorize
                                            suggested_cat = row.get("category") or st.session_state.categorizer.categorize(item)
                                            categories = st.session_state.db.get_categories()
                                            default_idx = categories.index(suggested_cat) if suggested_cat in categories else 0
                                            category = st.selectbox("Category", categories, index=default_idx, key=f"cat_{idx}")
                                        
                                        with col3:
                                            amount_val = st.number_input("Amount", value=float(row.get("amount", 0.0)), key=f"amt_{idx}")
                                        
                                        with col4:
                                            if has_full_db_access:
                                                employee = st.selectbox("Employee", employees, key=f"emp_{idx}")
                                            else:
                                                employee = current_staff_name
                                                st.text_input("Employee", value=employee, disabled=True, key=f"emp_fixed_{idx}")
                                        
                                        if st.form_submit_button(f"Add Item {idx+1}"):
                                            st.session_state.db.add_expense(
                                                date=date.today().strftime('%Y-%m-%d'),
                                                item_name=item_name,
                                                category=category,
                                                amount=amount_val,
                                                employee_name=employee,
                                                invoice_id=invoice_id,
                                                entry_mode='Invoice OCR'
                                            )
                                            st.success(f"✅ Added: {item_name}")
                            else:
                                st.info("No items with specific amounts found, but text was extracted. Please add items manually or review extracted text above.")
                        else:
                            st.warning("No content could be extracted from the invoice. Please enter manually.")
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")





elif selected_menu == "📊 Upload Excel":
    st.title("📊 Upload Excel File")
    
    st.info("Upload an Excel file with columns: Date, Item, Category, Amount, Employee")
    
    # Download template
    col1, col2 = st.columns([1, 3])
    with col1:
        template_data = create_expense_template(
            is_admin=is_admin_user,
            staff_name=current_staff_name,
            employee_options=st.session_state.db.get_employees() if is_admin_user else []
        )
        st.download_button(
            label="📥 Download Template",
            data=template_data,
            file_name="expense_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file:
        success, data, message = st.session_state.excel_importer.import_from_excel(uploaded_file)
        
        if success:
            st.success(message)
            
            # Show preview
            st.subheader("Preview Data")
            preview_df = pd.DataFrame(data)
            st.dataframe(preview_df, use_container_width=True)
            
            # Confirm import
            if st.button("Confirm and Import All", type="primary"):
                count = 0
                for row in data:
                    employee_name = row['employee_name'] if has_full_db_access else current_staff_name
                    st.session_state.db.add_expense(
                        date=row['date'],
                        item_name=row['item_name'],
                        category=row['category'],
                        amount=row['amount'],
                        employee_name=employee_name,
                        entry_mode='Excel Import'
                    )
                    count += 1
                
                st.success(f"✅ Successfully imported {count} expenses!")
                st.balloons()
        else:
            st.error(message)

elif selected_menu == "📸 Camera Capture":
    st.title("📸 Camera Capture Invoice")
    
    st.info("📷 Capture invoice photos using your camera to automatically extract expenses")
    if not get_ocr().tesseract_available and get_ocr().easyocr_available:
        st.warning("Tesseract OCR engine not available. Using EasyOCR fallback.")
    elif not get_ocr().tesseract_available and not get_ocr().easyocr_available:
        st.error("No OCR engine available. Install Tesseract or EasyOCR.")
        st.stop()
    
    prefer_handwriting_cam = st.checkbox("🖊️ Prefer handwriting OCR", value=True)
    
    camera_image = st.camera_input("Take a photo of your invoice")
    
    if camera_image is not None:
        st.image(camera_image, caption="Captured Image")
        
        # Process image
        if st.button("📖 Extract from Image", type="primary"):
            with st.spinner("Processing image..."):
                try:
                    image_bytes = camera_image.read()
                    from PIL import Image
                    from io import BytesIO
                    image = Image.open(BytesIO(image_bytes))

                    result = get_ocr().process_invoice(image, prefer_handwriting_cam)
                    if result and result.get('text'):
                        st.success("✅ Image processed successfully!")

                        with st.expander("📋 View Extracted Text"):
                            st.text(result['text'])

                        if result.get('items'):
                            st.subheader("📦 Extracted Items")
                            st.info(f"Found {len(result['items'])} items")
                            parsed_rows = result.get('parsed_items') or [
                                {"item_name": item, "amount": amount, "category": None}
                                for item, amount in result['items']
                            ]
                            parsed_preview_df = pd.DataFrame(parsed_rows)
                            if not parsed_preview_df.empty:
                                if "confidence" not in parsed_preview_df.columns:
                                    parsed_preview_df["confidence"] = 0.0
                                parsed_preview_df = parsed_preview_df.rename(
                                    columns={
                                        "item_name": "Item",
                                        "amount": "Amount",
                                        "category": "Category",
                                        "confidence": "Confidence (%)",
                                    }
                                )
                                st.markdown("**🧠 Parser Confidence Panel**")
                                st.dataframe(parsed_preview_df, use_container_width=True)
                                low_conf_count = int((parsed_preview_df["Confidence (%)"] < 60).sum())
                                if low_conf_count > 0:
                                    st.warning(f"⚠️ {low_conf_count} item(s) have low confidence (<60%). Please review before adding.")

                            employees = st.session_state.db.get_employees()
                            if st.button("✅ Add All Extracted Items", key="add_all_camera_items"):
                                added = 0
                                for row in parsed_rows:
                                    item_name = row.get("item_name", "")
                                    amount = float(row.get("amount", 0))
                                    suggested_cat = row.get("category") or st.session_state.categorizer.categorize(item_name) or "Miscellaneous"
                                    employee_name = current_staff_name if not has_full_db_access else (employees[0] if employees else current_staff_name)
                                    st.session_state.db.add_expense(
                                        date=date.today().strftime('%Y-%m-%d'),
                                        item_name=item_name,
                                        category=suggested_cat,
                                        amount=float(amount),
                                        employee_name=employee_name,
                                        entry_mode='Camera OCR'
                                    )
                                    added += 1
                                st.success(f"✅ Added {added} items from camera capture.")
                                st.rerun()

                            for idx, row in enumerate(parsed_rows):
                                with st.form(f"cam_item_form_{idx}"):
                                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                                    with col1:
                                        item = row.get("item_name", "")
                                        item_name = st.text_input("Item", value=item, key=f"cam_item_{idx}")
                                    with col2:
                                        suggested_cat = row.get("category") or st.session_state.categorizer.categorize(item)
                                        categories = st.session_state.db.get_categories()
                                        default_idx = categories.index(suggested_cat) if suggested_cat in categories else 0
                                        category = st.selectbox("Category", categories, index=default_idx, key=f"cam_cat_{idx}")
                                    with col3:
                                        amount_val = st.number_input("Amount", value=float(row.get("amount", 0.0)), key=f"cam_amt_{idx}")
                                    with col4:
                                        if has_full_db_access:
                                            employee = st.selectbox("Employee", employees, key=f"cam_emp_{idx}")
                                        else:
                                            employee = current_staff_name
                                            st.text_input("Employee", value=employee, disabled=True, key=f"cam_emp_fixed_{idx}")

                                    if st.form_submit_button(f"Add Item {idx+1}"):
                                        st.session_state.db.add_expense(
                                            date=date.today().strftime('%Y-%m-%d'),
                                            item_name=item_name,
                                            category=category,
                                            amount=amount_val,
                                            employee_name=employee,
                                            entry_mode='Camera OCR'
                                        )
                                        st.success(f"✅ Added: {item_name}")
                        else:
                            st.info("No items with specific amounts found. Please review text and add manually.")
                    else:
                        st.warning("No content could be extracted from captured image.")
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")


elif selected_menu == "💵 Cash Received":
    st.title("💵 Cash Received")
    
    # Current balance
    balance = st.session_state.db.get_petty_cash_balance()
    st.metric("Current Cash Balance", f"₹{balance:,.2f}")
    
    st.divider()
    
    # Add new petty cash
    with st.form("add_petty_cash"):
        st.subheader("Add Cash Received")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cash_date = st.date_input("Date Received", value=date.today())
            amount = st.number_input("Amount Received (₹)", min_value=0.0, step=0.01)
        
        with col2:
            received_from = st.text_input("Received From", placeholder="e.g., Company, Self")
            remarks = st.text_area("Remarks (Optional)", placeholder="Any additional notes")
        
        if st.form_submit_button("Add Cash Receipt", type="primary"):
            if amount > 0 and received_from:
                st.session_state.db.add_petty_cash(
                    date_received=cash_date.strftime('%Y-%m-%d'),
                    amount=amount,
                    received_from=received_from,
                    remarks=remarks
                )
                st.success("✅ Cash receipt added successfully!")
                st.rerun()
            else:
                st.error("Please fill all required fields")
    
    st.divider()
    
    # Show all petty cash records
    st.subheader("📋 All Cash Receipts")
    petty_cash_df = st.session_state.db.get_all_petty_cash()
    if not petty_cash_df.empty:
        st.dataframe(petty_cash_df, use_container_width=True)
    else:
        st.info("No cash receipts recorded yet")

elif selected_menu == "📁 Manage Categories":
    st.title("📁 Manage Categories")
    
    categories = st.session_state.db.get_categories()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Add Category")
        new_category = st.text_input("Category Name")
        if st.button("Add Category", type="primary"):
            if new_category:
                success, message = st.session_state.db.add_category(new_category)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        st.subheader("🗑️ Delete Category")
        delete_category = st.selectbox("Select Category to Delete", categories)
        if st.button("Delete Category", type="secondary"):
            if delete_category:
                st.session_state.db.delete_category(delete_category)
                st.success(f"Deleted category: {delete_category}")
                st.rerun()
    
    st.divider()
    st.subheader("📋 All Categories")
    st.write(", ".join(categories))

elif selected_menu == "👥 Manage Employees":
    if not is_admin_user:
        st.error("Only admin can manage employees.")
        st.stop()

    st.title("👥 Manage Employees")
    
    employees = st.session_state.db.get_employees()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("➕ Add Employee")
        new_employee = st.text_input("Employee Name")
        if st.button("Add Employee", type="primary"):
            if new_employee:
                success, message = st.session_state.db.add_employee(new_employee)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        st.subheader("✏️ Edit Employee")
        edit_employee = st.selectbox("Select Employee to Edit", employees, key="edit_emp_select")
        new_name = st.text_input("New Name", key="edit_emp_name")
        if st.button("Update Employee", type="secondary"):
            if edit_employee and new_name:
                success, message = st.session_state.db.update_employee(edit_employee, new_name)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with col3:
        st.subheader("🗑️ Delete Employee")
        delete_employee = st.selectbox("Select Employee to Delete", employees, key="del_emp_select")
        if st.button("Delete Employee", type="secondary"):
            if delete_employee:
                st.session_state.db.delete_employee(delete_employee)
                st.success(f"Deleted employee: {delete_employee}")
                st.rerun()
    
    st.divider()
    st.subheader("📋 All Employees")
    for emp in employees:
        st.write(f"• {emp}")

elif selected_menu == "📋 Manage Expenses":
    st.title("📋 Manage Expenses")
    st.info("🔐 Rights-based access: Edit/Delete allowed per your assigned permissions.")
    if not has_full_db_access:
        st.warning("Database access is scoped to your own entries.")
    
    categories = st.session_state.db.get_categories()
    employees = st.session_state.db.get_employees()
    
    expenses_df = scoped_expenses_df()
    if expenses_df.empty:
        st.info("No expenses to manage.")
    else:
        # list all expenses with action buttons
        for _, row in expenses_df.iterrows():
            cols = st.columns([3,1,1])
            with cols[0]:
                st.write(f"{row['date']} – {row['item_name']} (₹{row['amount']}) – {row['category']} – {row['employee_name']}")
            with cols[1]:
                if st.button(
                    "✏️ Edit",
                    key=f"edit_{row['id']}",
                    help="Requires Edit permission",
                    disabled=not staff_can_edit
                ):
                    st.session_state.edit_expense = row.to_dict()
                    st.rerun()
            with cols[2]:
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{row['id']}",
                    help="Requires Delete permission",
                    disabled=not staff_can_delete
                ):
                    st.session_state.db.delete_expense(row['id'])
                    st.success("✅ Expense deleted successfully!")
                    st.rerun()

        # edit form if requested
        if 'edit_expense' in st.session_state:
            e = st.session_state.edit_expense
            edit_categories = categories[:] if categories else []
            edit_employees = employees[:] if employees else []
            if e.get('category') and e['category'] not in edit_categories:
                edit_categories.append(e['category'])
            if e.get('employee_name') and e['employee_name'] not in edit_employees:
                edit_employees.append(e['employee_name'])

            st.divider()
            st.subheader("✏️ Edit Expense")
            with st.form("edit_expense_form"):
                col1, col2 = st.columns(2)
                with col1:
                    edit_date = st.date_input("Date", value=pd.to_datetime(e['date']).date())
                    edit_item = st.text_input("Item Name", value=e['item_name'])
                    edit_category = st.selectbox(
                        "Category",
                        edit_categories,
                        index=edit_categories.index(e['category']) if e['category'] in edit_categories else 0
                    )
                with col2:
                    edit_amount = st.number_input("Amount (₹)", value=e['amount'], min_value=0.0, step=0.01)
                    if has_full_db_access:
                        edit_employee = st.selectbox(
                            "Employee",
                            edit_employees,
                            index=edit_employees.index(e['employee_name']) if e['employee_name'] in edit_employees else 0
                        )
                    else:
                        edit_employee = current_staff_name
                        st.text_input("Employee", value=edit_employee, disabled=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("✅ Update Expense", type="primary")
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        del st.session_state['edit_expense']
                        st.rerun()
                
                if submitted:
                    st.session_state.db.update_expense(
                        e['id'],
                        edit_date.strftime('%Y-%m-%d'),
                        edit_item,
                        edit_category,
                        edit_amount,
                        edit_employee
                    )
                    st.success("✅ Expense updated successfully!")
                    del st.session_state['edit_expense']
                    st.rerun()

    st.divider()

elif selected_menu == "👤 Manage Staff":
    if not is_admin_user:
        st.error("Only admin can manage staff accounts.")
        st.stop()

    st.title("👤 Manage Staff Accounts")
    st.info("Admin can create unique user IDs and passwords for staff to access their portal.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("➕ Create Staff Login")
        with st.form("add_staff_form"):
            new_username = st.text_input("Staff Username (unique)")
            new_full_name = st.text_input("Full Name")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["staff", "admin"])
            add_staff_submit = st.form_submit_button("Create Staff ID", type="primary")

            if add_staff_submit:
                if new_username and new_full_name and new_password:
                    success, message, staff_id = st.session_state.db.add_staff(
                        username=new_username.strip(),
                        password=new_password,
                        full_name=new_full_name.strip(),
                        role=new_role
                    )
                    if success:
                        st.success(f"Created staff account successfully. Staff ID: {staff_id}")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all fields.")

    with col2:
        st.subheader("🔑 Reset Staff Password")
        staff_df = st.session_state.db.get_all_staff()
        non_admin_users = [u for u in staff_df["username"].tolist() if u != "admin"] if not staff_df.empty else []
        if non_admin_users:
            with st.form("reset_staff_password_form"):
                reset_user = st.selectbox("Select Staff", non_admin_users)
                reset_pass = st.text_input("New Password", type="password")
                reset_submit = st.form_submit_button("Reset Password")
                if reset_submit:
                    if reset_pass:
                        success, msg = st.session_state.db.reset_staff_password(reset_user, reset_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.error("Password cannot be empty.")
        else:
            st.info("No non-admin staff accounts available.")

    st.divider()
    st.subheader("📋 All Staff Accounts")
    staff_df = st.session_state.db.get_all_staff()
    if not staff_df.empty:
        st.dataframe(staff_df, use_container_width=True)

        st.subheader("⚙️ Activate / Disable Staff")
        staff_users = [u for u in staff_df["username"].tolist() if u != "admin"]
        if staff_users:
            col_a, col_b = st.columns(2)
            with col_a:
                disable_user = st.selectbox("Disable Staff User", staff_users, key="disable_staff_user")
                if st.button("Disable User", type="secondary"):
                    ok, msg = st.session_state.db.disable_staff(disable_user)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            with col_b:
                enable_user = st.selectbox("Enable Staff User", staff_users, key="enable_staff_user")
                if st.button("Enable User", type="secondary"):
                    ok, msg = st.session_state.db.enable_staff(enable_user)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        st.divider()
        st.subheader("🛡️ Expense Rights Per Staff")
        rights_users = [u for u in staff_df["username"].tolist() if u != "admin"]
        if rights_users:
            selected_user = st.selectbox("Select Staff User", rights_users, key="rights_user_select")
            selected_row = staff_df[staff_df["username"] == selected_user].iloc[0]
            with st.form("staff_rights_form"):
                can_edit_exp = st.checkbox("Allow Edit Expenses", value=bool(selected_row["can_edit_expenses"]))
                can_delete_exp = st.checkbox("Allow Delete Expenses", value=bool(selected_row["can_delete_expenses"]))
                full_db = st.checkbox(
                    "Allow Full Database Access (view/post for all staff)",
                    value=bool(selected_row["full_db_access"])
                )
                rights_submit = st.form_submit_button("Save Rights", type="primary")
                if rights_submit:
                    ok, msg = st.session_state.db.update_staff_permissions(
                        selected_user,
                        can_edit_expenses=can_edit_exp,
                        can_delete_expenses=can_delete_exp,
                        full_db_access=full_db
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
    else:
        st.info("No staff accounts found.")

elif selected_menu == "🧠 Category Rules":
    if not is_admin_user:
        st.error("Only admin can manage category keyword rules.")
        st.stop()

    st.title("🧠 Category Rules")
    st.info("Manage keyword mappings used for automatic category prediction.")

    categories = list(st.session_state.categorizer.category_keywords.keys())
    selected_category = st.selectbox("Select Category", categories, key="rules_category_select")

    st.subheader("Current Keywords")
    current_keywords = st.session_state.categorizer.get_keywords(selected_category)
    if current_keywords:
        st.write(", ".join(current_keywords))
    else:
        st.info("No keywords configured for this category.")

    col1, col2 = st.columns(2)
    with col1:
        with st.form("add_keyword_rule_form"):
            new_kw = st.text_input("Add Keyword")
            add_kw_submit = st.form_submit_button("Add Keyword", type="primary")
            if add_kw_submit:
                if new_kw.strip():
                    if st.session_state.categorizer.add_keyword(selected_category, new_kw):
                        st.success("Keyword added.")
                        st.rerun()
                    else:
                        st.warning("Keyword already exists or invalid.")
                else:
                    st.error("Enter a keyword.")

    with col2:
        with st.form("remove_keyword_rule_form"):
            remove_kw = st.selectbox("Remove Keyword", current_keywords if current_keywords else [""], key="remove_kw_select")
            remove_kw_submit = st.form_submit_button("Remove Keyword", type="secondary")
            if remove_kw_submit and remove_kw:
                if st.session_state.categorizer.remove_keyword(selected_category, remove_kw):
                    st.success("Keyword removed.")
                    st.rerun()
                else:
                    st.warning("Could not remove keyword.")

elif selected_menu == "📈 Reports":

    st.title("📈 Reports & Analytics")
    report_source_df = scoped_expenses_df()
    if not has_full_db_access:
        st.info("Showing reports for your own entries only.")
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Date-wise Report", "Category-wise Report", "Employee-wise Report", "Advanced Filter Report", "Trends & Charts"]
    )
    
    if report_type == "Date-wise Report":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        
        if st.button("Generate Report"):
            if has_full_db_access:
                result = st.session_state.reports.generate_date_wise_report(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
            else:
                df = report_source_df.copy()
                df = df[(df['date'] >= start_date.strftime('%Y-%m-%d')) & (df['date'] <= end_date.strftime('%Y-%m-%d'))]
                result = None if df.empty else (
                    df,
                    {
                        'total_amount': df['amount'].sum(),
                        'total_transactions': len(df),
                        'average_amount': df['amount'].mean(),
                        'date_range': f"{start_date} to {end_date}"
                    }
                )
            
            if result:
                df, summary = result
                
                st.subheader("Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Amount", f"₹{summary['total_amount']:,.2f}")
                with col2:
                    st.metric("Transactions", summary['total_transactions'])
                with col3:
                    st.metric("Average", f"₹{summary['average_amount']:,.2f}")
                
                st.subheader("Detailed Transactions")
                st.dataframe(df, use_container_width=True)
                
                # Export button
                if has_full_db_access:
                    excel_data = st.session_state.reports.export_report_to_excel(
                        'date_wise',
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d')
                    )
                    st.download_button(
                        "📥 Download Excel",
                        data=excel_data,
                        file_name=f"date_wise_report_{start_date}_{end_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("No data found for selected date range")
    
    elif report_type == "Category-wise Report":
        if has_full_db_access:
            df = st.session_state.reports.generate_category_wise_report()
        else:
            df = None
            if not report_source_df.empty:
                df = report_source_df.groupby('category', as_index=False)['amount'].sum().rename(columns={'amount': 'total'})
                total_amt = df['total'].sum()
                df['percentage'] = (df['total'] / total_amt * 100).round(2) if total_amt > 0 else 0
        
        if df is not None:
            st.dataframe(df, use_container_width=True)
            
            # Chart
            if has_full_db_access:
                fig = st.session_state.reports.create_category_pie_chart()
            else:
                fig = None
                if df is not None and not df.empty:
                    import plotly.express as px
                    fig = px.pie(df, values='total', names='category', title='Expenses by Category')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Export
            if has_full_db_access:
                excel_data = st.session_state.reports.export_report_to_excel('category_wise')
                st.download_button(
                    "📥 Download Excel",
                    data=excel_data,
                    file_name="category_wise_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No expense data available")
    
    elif report_type == "Employee-wise Report":
        if has_full_db_access:
            df = st.session_state.reports.generate_employee_wise_report()
        else:
            df = None
            if not report_source_df.empty:
                df = report_source_df.groupby('employee_name', as_index=False)['amount'].sum().rename(columns={'amount': 'total'})
                total_amt = df['total'].sum()
                df['percentage'] = (df['total'] / total_amt * 100).round(2) if total_amt > 0 else 0
                df['transactions'] = report_source_df.groupby('employee_name').size().values
                df['avg_per_transaction'] = (df['total'] / df['transactions']).round(2)
        
        if df is not None:
            st.dataframe(df, use_container_width=True)
            
            # Chart
            if has_full_db_access:
                fig = st.session_state.reports.create_employee_bar_chart()
            else:
                fig = None
                if df is not None and not df.empty:
                    import plotly.express as px
                    fig = px.bar(df, x='employee_name', y='total', title='Expenses by Employee')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Export
            if has_full_db_access:
                excel_data = st.session_state.reports.export_report_to_excel('employee_wise')
                st.download_button(
                    "📥 Download Excel",
                    data=excel_data,
                    file_name="employee_wise_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No expense data available")
    


    elif report_type == "Advanced Filter Report":
        st.subheader("Advanced Filter Report")

        period_option = st.selectbox(
            "Select Period",
            ["Today", "This Week", "This Month", "Last 30 Days", "Custom Range"]
        )

        today = date.today()
        if period_option == "Today":
            start_date = today
            end_date = today
        elif period_option == "This Week":
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif period_option == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        elif period_option == "Last 30 Days":
            start_date = today - timedelta(days=29)
            end_date = today
        else:
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=today.replace(day=1), key="adv_start")
            with col2:
                end_date = st.date_input("End Date", value=today, key="adv_end")

        if period_option != "Custom Range":
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Start Date", value=start_date.strftime("%Y-%m-%d"), disabled=True)
            with col2:
                st.text_input("End Date", value=end_date.strftime("%Y-%m-%d"), disabled=True)

        categories = sorted(report_source_df["category"].dropna().unique().tolist()) if not report_source_df.empty else []
        employees = sorted(report_source_df["employee_name"].dropna().unique().tolist()) if not report_source_df.empty else []

        col1, col2 = st.columns(2)
        with col1:
            selected_categories = st.multiselect("Category Filter", options=categories)
        with col2:
            selected_employees = st.multiselect("Employee Filter", options=employees)

        if st.button("Generate Advanced Report", type="primary"):
            if start_date > end_date:
                st.error("Start date cannot be after end date.")
            elif report_source_df.empty:
                st.info("No expense data available.")
            else:
                filtered_df = report_source_df.copy()
                filtered_df["date_dt"] = pd.to_datetime(filtered_df["date"], errors="coerce")
                filtered_df = filtered_df[(filtered_df["date_dt"].dt.date >= start_date) & (filtered_df["date_dt"].dt.date <= end_date)]

                if selected_categories:
                    filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
                if selected_employees:
                    filtered_df = filtered_df[filtered_df["employee_name"].isin(selected_employees)]

                filtered_df = filtered_df.drop(columns=["date_dt"], errors="ignore")

                if filtered_df.empty:
                    st.info("No data found for selected filters.")
                else:
                    st.subheader("Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Amount", f"INR {filtered_df['amount'].sum():,.2f}")
                    with col2:
                        st.metric("Transactions", len(filtered_df))
                    with col3:
                        st.metric("Average", f"INR {filtered_df['amount'].mean():,.2f}")

                    st.subheader("Filtered Transactions")
                    st.dataframe(filtered_df, use_container_width=True)

                    category_view = filtered_df.groupby("category", as_index=False)["amount"].sum().rename(columns={"amount": "total"})
                    if not category_view.empty:
                        import plotly.express as px
                        fig = px.pie(category_view, values="total", names="category", title="Filtered Category Split")
                        st.plotly_chart(fig, use_container_width=True)

                    st.download_button(
                        "Download Filtered CSV",
                        data=filtered_df.to_csv(index=False),
                        file_name=f"advanced_report_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
    elif report_type == "Trends & Charts":
        st.subheader("📈 Expense Trends")
        
        # Daily trend
        fig = st.session_state.reports.create_daily_trend_chart(days=30)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Monthly comparison
        fig = st.session_state.reports.create_monthly_comparison_chart(months=6)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Top expenses
        fig = st.session_state.reports.create_top_expenses_chart(top_n=10)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.divider()
st.sidebar.info("""
**Expense Tracker**
Version 10.2@2026
""")
