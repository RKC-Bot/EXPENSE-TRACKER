# 🏗️ Technical Architecture - AI Expense Tracker

## System Overview

The AI Expense Tracker is a modular, full-stack application built with Python and Streamlit, featuring:
- **Backend**: SQLite database with Python ORM
- **Frontend**: Streamlit web interface
- **AI/ML**: Keyword-based categorization with extensibility for LLM integration
- **OCR**: Tesseract (printed) + EasyOCR (handwritten)
- **Voice**: SpeechRecognition with Google Speech API
- **Reports**: Plotly interactive visualizations

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                 Streamlit UI Layer                  │
│                    (main.py)                        │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  Business Logic                     │
├─────────────────┬─────────────────┬─────────────────┤
│  categorizer.py │  invoice_ocr.py │  voice_entry.py │
│  excel_import.py│   reports.py    │                 │
└─────────────────┴─────────────────┴─────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Data Access Layer                      │
│                 database.py                         │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│             Storage Layer                           │
├─────────────────┬───────────────────────────────────┤
│   SQLite DB     │   File Storage                    │
│ (expenses.db)   │   (invoices/)                     │
└─────────────────┴───────────────────────────────────┘
```

---

## Module Breakdown

### 1. **main.py** - Streamlit Application
**Purpose**: Main UI and user interaction logic

**Key Features**:
- Multi-page navigation using radio buttons
- Session state management
- Form handling and validation
- Real-time data visualization
- File upload processing

**Pages**:
- Dashboard: Summary metrics and charts
- Add Expense: Manual entry form
- Upload Invoice: OCR processing workflow
- Upload Excel: Bulk import
- Voice Entry: Speech-to-text capture
- Petty Cash: Cash receipt management
- Manage Categories: CRUD operations
- Manage Employees: CRUD operations
- Reports: Analytics and export

**Dependencies**:
```python
import streamlit as st
import pandas as pd
from modules.database import ExpenseDatabase
from modules.categorizer import AIExpenseCategorizer
# ... other modules
```

---

### 2. **database.py** - Data Access Layer
**Purpose**: All database operations and queries

**Database Schema**:

```sql
-- Categories
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices (for duplicate detection)
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_hash TEXT UNIQUE NOT NULL,
    file_name TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Expenses
CREATE TABLE expenses (
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
);

-- Petty Cash
CREATE TABLE petty_cash (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_received TEXT NOT NULL,
    amount REAL NOT NULL,
    received_from TEXT NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Methods**:
- `add_expense()`: Insert expense record
- `get_all_expenses()`: Retrieve all expenses
- `get_expenses_by_category()`: Group by category
- `add_petty_cash()`: Record cash receipt
- `get_petty_cash_balance()`: Calculate balance
- `check_duplicate_invoice()`: Hash-based duplicate detection

**Special Handling**:
- Persistent connections for in-memory databases (testing)
- Automatic directory creation for file-based databases
- Default categories and employees on first run

---

### 3. **categorizer.py** - AI Classification Engine
**Purpose**: Intelligent expense categorization

**Algorithm**:
```
1. Convert item name to lowercase
2. For each category:
   a. Check exact keyword match (score +10)
   b. Check partial match (score +5)
   c. Check word boundary match (score +7)
3. Return category with highest score
4. Default to "Miscellaneous" if no match
```

**Category Keywords**:
```python
{
    'Vegetables': ['tomato', 'potato', 'onion', ...],
    'Fruits': ['apple', 'banana', 'orange', ...],
    'Dairy': ['milk', 'curd', 'paneer', ...],
    'Transport': ['taxi', 'uber', 'metro', ...],
    'Utilities': ['electricity', 'water', 'internet', ...],
    # ... more categories
}
```

**Confidence Scoring**:
```python
confidence = min(100, (score / 10) * 100)
```

**Extension Point**:
```python
def categorize_with_llm(item_name, categories, api_key=None):
    """
    Future: Use Claude or GPT API for better categorization
    """
    # Call LLM API
    # Return category with reasoning
```

---

### 4. **invoice_ocr.py** - OCR Processing
**Purpose**: Extract text and data from invoices

**OCR Engines**:

**A. Tesseract OCR** (Printed Text)
- Fast, accurate for typed/printed invoices
- Uses pytesseract Python wrapper
- Installed system-wide

**B. EasyOCR** (Handwritten Text)
- Deep learning-based (PyTorch)
- Better for handwritten receipts
- Downloads models on first use (~100MB)

**Processing Pipeline**:
```
1. Image Upload
   ↓
2. OCR Text Extraction
   ↓
3. Text Parsing
   ↓
4. Item/Amount Detection
   ↓
5. Total Calculation
   ↓
6. Return Structured Data
```

**Text Parsing Patterns**:
```python
# Amount patterns
r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)'     # ₹123.45
r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)' # Rs 123.45
r'(\d+(?:,\d+)*(?:\.\d+)?)\s*/-'    # 123.45/-

# Total patterns
r'total[:\s]+₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
r'grand\s+total[:\s]+₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
```

**PDF Support**:
- Uses pdf2image to convert PDF to images
- Fallback to PyPDF2 for text-based PDFs

---

### 5. **voice_entry.py** - Speech Recognition
**Purpose**: Voice-to-text expense entry

**Audio Processing**:
```
1. Microphone Input
   ↓
2. Ambient Noise Adjustment
   ↓
3. Audio Capture (5s timeout)
   ↓
4. Google Speech Recognition
   ↓
5. Text Transcription
   ↓
6. Expense Parsing
```

**Text Parsing Logic**:
```python
# Extract amount
patterns = [
    r'(\d+)\s*(?:rupees|rs|inr)',
    r'for\s*(\d+)',
    r'spent\s*(\d+)',
]

# Extract item
# Remove amount-related words
# Remaining text = item name
```

**Example Transformations**:
```
"bought tomatoes for 50 rupees"
→ item: "tomatoes", amount: 50

"spent 100 on milk"
→ item: "milk", amount: 100
```

---

### 6. **excel_import.py** - Bulk Import/Export
**Purpose**: Excel file processing

**Import Pipeline**:
```
1. File Upload (XLSX/XLS)
   ↓
2. Column Normalization
   ↓
3. Data Validation
   ↓
4. Error Reporting
   ↓
5. Batch Insert
```

**Column Mapping**:
```python
col_mapping = {
    'date' → 'Date',
    'item/description/particular' → 'Item',
    'category/type' → 'Category',
    'amount/price/cost' → 'Amount',
    'employee/person/name' → 'Employee'
}
```

**Validation Rules**:
- Date: Convert to YYYY-MM-DD format
- Amount: Must be > 0
- Item: Required, non-empty
- Category: Default to 'Miscellaneous' if missing
- Employee: Default to 'Unknown' if missing

**Export Features**:
- Multiple sheets (expenses, categories, employees, petty cash)
- Auto-formatting
- Summary statistics
- Template generation

---

### 7. **reports.py** - Analytics & Visualization
**Purpose**: Generate reports and charts

**Report Types**:

**A. Summary Statistics**
```python
{
    'total_expenses': float,
    'petty_cash_balance': float,
    'total_cash_received': float,
    'total_transactions': int,
    'avg_expense': float
}
```

**B. Category-wise Report**
- Total amount per category
- Percentage breakdown
- Transaction count

**C. Employee-wise Report**
- Total per employee
- Average per transaction
- Transaction count

**D. Date-wise Report**
- Filter by date range
- Daily/monthly aggregation
- Trend analysis

**Visualization Library**: Plotly

**Chart Types**:
1. Pie Chart: Category distribution
2. Bar Chart: Employee comparison
3. Line Chart: Daily trends
4. Area Chart: Category trends over time
5. Stacked Bar: Monthly comparison

**Export Formats**:
- Excel (.xlsx) with multiple sheets
- Google Sheets (optional integration)

---

## Data Flow Examples

### Example 1: Manual Expense Entry
```
User → Streamlit Form
  ↓
  Validate input
  ↓
  AI Categorizer (suggest category)
  ↓
  User confirms
  ↓
  Database.add_expense()
  ↓
  SQLite INSERT
  ↓
  Update UI (success message)
```

### Example 2: Invoice Upload
```
User → Upload Image/PDF
  ↓
  Calculate SHA256 hash
  ↓
  Check Database.check_duplicate_invoice()
  ↓
  If duplicate: Alert user
  ↓
  If new: Save to data/invoices/
  ↓
  OCR.process_invoice()
  ↓
  Parse items and amounts
  ↓
  AI Categorizer (auto-categorize)
  ↓
  Display for user review
  ↓
  User confirms each item
  ↓
  Database.add_expense() for each
  ↓
  Database.add_invoice() (record hash)
```

### Example 3: Petty Cash Flow
```
Cash Received:
  Database.add_petty_cash(amount)
  ↓
  SQLite INSERT into petty_cash

Expense Made:
  Database.add_expense(amount)
  ↓
  SQLite INSERT into expenses

Balance Calculation:
  SUM(petty_cash.amount) - SUM(expenses.amount)
```

---

## Security Considerations

### 1. SQL Injection Prevention
- Parameterized queries throughout
- No string concatenation in SQL

```python
# ✅ Safe
cursor.execute("INSERT INTO expenses (item) VALUES (?)", (item,))

# ❌ Unsafe
cursor.execute(f"INSERT INTO expenses (item) VALUES ('{item}')")
```

### 2. File Upload Security
- Validate file types (whitelist)
- Calculate hash before processing
- Store files with hashed names
- Limit file sizes

### 3. Duplicate Detection
- SHA256 cryptographic hash
- Collision resistance
- Fast lookup via indexed column

```python
file_hash = hashlib.sha256(file_content).hexdigest()
```

### 4. Database Security
- Local storage by default
- File permissions (owner read/write)
- Regular backups recommended
- No external API calls with sensitive data

---

## Performance Optimizations

### 1. Database Indexing
```sql
-- Index on frequently queried columns
CREATE INDEX idx_expense_date ON expenses(date);
CREATE INDEX idx_expense_category ON expenses(category);
CREATE INDEX idx_invoice_hash ON invoices(file_hash);
```

### 2. Lazy Loading
- EasyOCR reader initialized on first use
- Reduces startup time
- Saves memory when OCR not needed

### 3. Batch Operations
- Excel import uses single transaction
- Reduces database I/O
- Faster bulk inserts

### 4. Caching
- Session state for database connection
- Avoid repeated initialization
- Streamlit caching for expensive operations

---

## Extension Points

### 1. LLM Integration
**Location**: `categorizer.py`

```python
def categorize_with_llm(item_name, categories):
    """Use Claude or GPT for categorization"""
    prompt = f"""
    Categorize this expense item: {item_name}
    Categories: {categories}
    Return only the category name.
    """
    # Call API
    # Parse response
    return category
```

### 2. Email Integration
**New Module**: `email_parser.py`

```python
def parse_gmail_receipts():
    """Extract expenses from Gmail receipts"""
    # Connect to Gmail API
    # Search for receipts
    # Extract PDF attachments
    # Process with OCR
    # Auto-import expenses
```

### 3. Google Sheets Sync
**Location**: `reports.py`

```python
def sync_to_google_sheets(credentials_file):
    """Sync expenses to Google Sheets"""
    import gspread
    # Authenticate
    # Create/update spreadsheet
    # Push data
```

### 4. Budget Tracking
**New Module**: `budget.py`

```python
def set_budget(category, amount, period):
    """Set monthly budget for category"""
    
def check_budget_status():
    """Alert when approaching budget limit"""
```

---

## Testing Strategy

### 1. Unit Tests
- Each module tested independently
- Mock database connections
- Test edge cases

### 2. Integration Tests
- Full workflow testing
- Database → UI → Reports
- End-to-end scenarios

### 3. Performance Tests
- Large dataset handling (10,000+ expenses)
- OCR processing time
- Report generation speed

### 4. User Acceptance Tests
- Manual testing checklist
- Real invoice samples
- Voice entry accuracy

---

## Deployment Options

### 1. Local Development
```bash
streamlit run main.py
```

### 2. Docker Container
```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y tesseract-ocr
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "main.py"]
```

### 3. Cloud Deployment
**Streamlit Cloud**:
- Push to GitHub
- Connect Streamlit Cloud
- Auto-deploy

**Heroku/AWS/GCP**:
- Add Procfile
- Configure buildpacks
- Set environment variables

### 4. Desktop Executable
```bash
pyinstaller --onefile main.py
```

---

## Database Migration Strategy

### Adding New Columns
```python
def migrate_v1_to_v2():
    cursor.execute("""
        ALTER TABLE expenses 
        ADD COLUMN notes TEXT DEFAULT ''
    """)
    conn.commit()
```

### Data Migration
```python
def migrate_old_database(old_db_path, new_db_path):
    # Read from old database
    # Transform data
    # Insert into new database
```

---

## Monitoring & Logging

### Application Logs
```python
import logging

logging.basicConfig(
    filename='expense_tracker.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Expense added: {item}")
logging.error("OCR failed: {error}")
```

### Performance Metrics
- Track OCR processing time
- Monitor database query speed
- Log user actions
- Error rate tracking

---

## Future Architecture Enhancements

### 1. Microservices Architecture
```
API Gateway
    ↓
┌─────────────┬─────────────┬─────────────┐
│ Expense API │  OCR API    │ Report API  │
└─────────────┴─────────────┴─────────────┘
```

### 2. Real-time Sync
- WebSocket for live updates
- Multi-user support
- Conflict resolution

### 3. Machine Learning
- Train custom OCR models
- Predict future expenses
- Anomaly detection

### 4. Mobile-First
- React Native frontend
- Shared API backend
- Offline-first architecture

---

**Built with**: Python 3.12, Streamlit, SQLite, Tesseract, EasyOCR, Plotly

**License**: Open Source

**Maintainability**: Modular design for easy extension and modification
