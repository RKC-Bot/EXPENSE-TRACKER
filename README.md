# 💰 AI Expense & Petty Cash Tracker

A comprehensive, AI-powered expense tracking application built with Streamlit featuring OCR invoice processing, voice entry, Excel import, and intelligent categorization.

## 🌟 Features

### 1. **Dashboard**
- Real-time expense overview
- Petty cash balance tracking
- Interactive charts (Category-wise, Employee-wise)
- Recent transactions view

### 2. **Multiple Entry Modes**

#### A. Manual Entry
- Simple form-based entry
- Date, Item, Category, Amount, Employee
- Real-time validation

#### B. Excel Upload
- Bulk import from Excel files
- Template download available
- Auto-validation and error reporting
- Expected columns: Date | Item | Category | Amount | Employee

#### C. Voice Entry
- Speech-to-text conversion
- Automatic parsing of item and amount
- AI-powered categorization
- Confirmation before saving

### 3. **Invoice Processing (OCR)**
- Upload invoice images (JPG, PNG) or PDFs
- **Tesseract OCR** for printed text
- **EasyOCR** for handwritten notes
- Automatic item and amount extraction
- Smart categorization
- **Duplicate detection** using SHA256 hash
- Invoice storage in `data/invoices/`

### 4. **Petty Cash Management**
- Track cash received
- Calculate running balance
- Fields: Date, Amount, Source, Remarks
- Complete transaction history

### 5. **Smart Categorization**
- AI-powered category suggestions
- Keyword-based classification
- Confidence scoring
- 10+ pre-defined categories
- Custom category support

### 6. **Category & Employee Management**
- Add/delete categories
- Add/delete employees
- Default categories included
- Persistent storage

### 7. **Comprehensive Reporting**
- **Date-wise reports** - Filter by date range
- **Category-wise reports** - Spending breakdown
- **Employee-wise reports** - Per-person expenses
- **Trend analysis** - Daily, monthly charts
- **Excel export** - Download reports
- **Google Sheets sync** (optional)

### 8. **Visualizations (Plotly)**
- Interactive pie charts
- Bar charts
- Line graphs
- Trend analysis
- Top expenses view

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (for invoice processing)

### Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**MacOS:**
```bash
brew install tesseract
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Quick Start

1. **Clone or extract the project:**
```bash
cd expense_tracker
```

2. **Run setup checker (automatically installs dependencies):**
```bash
python setup_check.py
```

This will:
- Check for required packages
- Install missing dependencies
- Verify Tesseract installation
- Run basic tests
- Create necessary directories

3. **Generate sample data (optional, for testing):**
```bash
python sample_data_generator.py
```

This creates 50 sample expenses and 10 petty cash entries.

4. **Run the application:**
```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
expense_tracker/
│
├── main.py                      # Main Streamlit application
├── requirements.txt             # Python dependencies
├── setup_check.py              # Dependency checker & installer
├── sample_data_generator.py    # Sample data generator
├── README.md                   # This file
│
├── modules/
│   ├── database.py             # SQLite database operations
│   ├── categorizer.py          # AI categorization engine
│   ├── invoice_ocr.py          # OCR processing (Tesseract + EasyOCR)
│   ├── voice_entry.py          # Voice recognition
│   ├── excel_import.py         # Excel import/export
│   └── reports.py              # Report generation & charts
│
├── data/
│   └── invoices/               # Stored invoice files
│
└── db/
    └── expenses.db             # SQLite database
```

## 🚀 Usage Guide

### 1. Adding Expenses Manually
1. Navigate to **"Add Expense"**
2. Fill in: Item Name, Category, Amount, Employee, Date
3. Click **"Add Expense"**

### 2. Uploading Invoices
1. Go to **"Upload Invoice"**
2. Upload JPG/PNG/PDF invoice
3. Select OCR type (Printed/Handwritten)
4. Click **"Process Invoice"**
5. Review extracted items
6. Confirm and add to database

### 3. Importing from Excel
1. Go to **"Upload Excel"**
2. Download template (optional)
3. Upload filled Excel file
4. Review preview
5. Click **"Confirm and Import All"**

### 4. Voice Entry
1. Navigate to **"Voice Entry"**
2. Click **"Start Recording"**
3. Speak clearly: "Bought tomatoes for 50 rupees"
4. Review parsed data
5. Confirm and add

### 5. Managing Petty Cash
1. Go to **"Petty Cash Received"**
2. Enter: Date, Amount, Source
3. Add remarks (optional)
4. Click **"Add Cash Receipt"**

### 6. Generating Reports
1. Navigate to **"Reports"**
2. Select report type:
   - Date-wise
   - Category-wise
   - Employee-wise
   - Trends & Charts
3. Set parameters (if applicable)
4. View/download report

## 🎯 Advanced Features

### AI Categorization
The system uses intelligent keyword matching to automatically categorize expenses:
- **Vegetables**: tomato, potato, onion, etc.
- **Fruits**: apple, banana, orange, etc.
- **Dairy**: milk, curd, paneer, cheese, etc.
- **Transport**: taxi, uber, metro, etc.
- **Utilities**: electricity, water, internet, etc.

Test categorization in **"Add Expense"** → AI Category Suggestion

### Duplicate Invoice Detection
Uses SHA256 hashing to prevent duplicate invoice uploads:
- Each uploaded invoice is hashed
- System checks database before processing
- Alerts user if invoice already exists

### Excel Template
Download pre-formatted Excel template with:
- Correct column headers
- Sample data
- Instructions sheet

## 📊 Database Schema

### Tables
1. **expenses** - Main expense records
2. **petty_cash** - Cash received records
3. **invoices** - Invoice metadata & hashes
4. **categories** - Expense categories
5. **employees** - Employee list

### Fields
**Expenses:**
- id, date, item_name, category, amount
- employee_name, invoice_id, entry_mode
- created_at

**Petty Cash:**
- id, date_received, amount
- received_from, remarks, created_at

## 🔧 Configuration

### Default Categories
- Vegetables, Fruits, Dairy
- Groceries, Stationery
- Transport, Utilities
- Food & Beverages, Medical
- Entertainment, Miscellaneous

### Entry Modes
- Manual
- Excel Import
- Invoice OCR
- Voice

## 🐛 Troubleshooting

### Common Issues

**1. "Tesseract not found"**
```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr  # Ubuntu
brew install tesseract              # MacOS
```

**2. "SpeechRecognition not working"**
```bash
# Install PyAudio (required for microphone)
pip install PyAudio --break-system-packages
```

**3. "EasyOCR slow on first run"**
- EasyOCR downloads models on first use
- Subsequent runs will be faster

**4. "Module not found"**
```bash
# Re-run setup
python setup_check.py
```

## 🔮 Future Enhancements

### Planned Features
1. **LLM Integration** - Claude/GPT for smarter categorization
2. **Mobile App** - React Native/Flutter version
3. **Auto Email Parser** - Extract expenses from emails
4. **Receipt Auto-fetch** - Gmail, Amazon, Swiggy integration
5. **Budget Tracking** - Set limits and alerts
6. **Multi-currency** - International expense support
7. **Cloud Sync** - Real-time multi-device sync
8. **Analytics Dashboard** - Predictive insights

## 📱 Converting to Mobile/Desktop

### Create Desktop Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile main.py

# Output in dist/ folder
```

### Mobile App Options
1. **Kivy** - Native Python mobile framework
2. **BeeWare** - Cross-platform Python apps
3. **Progressive Web App** - Streamlit + wrapper

## 🔐 Security Notes

- Database stored locally
- No cloud sync by default
- Invoice images saved locally
- Use HTTPS in production
- Regular backups recommended

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review setup_check.py output
3. Verify all dependencies installed

## 📚 Dependencies

Core libraries:
- `streamlit` - Web interface
- `pandas` - Data manipulation
- `openpyxl` - Excel support
- `pytesseract` - OCR (printed)
- `easyocr` - OCR (handwritten)
- `plotly` - Interactive charts
- `SpeechRecognition` - Voice input
- `scikit-learn` - ML utilities
- `pillow` - Image processing

## 🎉 Getting Started Checklist

- [ ] Install Python 3.8+
- [ ] Install Tesseract OCR
- [ ] Run `python setup_check.py`
- [ ] Generate sample data (optional)
- [ ] Run `streamlit run main.py`
- [ ] Explore the dashboard
- [ ] Try adding an expense
- [ ] Upload a test invoice
- [ ] Generate a report

---

**Happy Expense Tracking! 💰📊**
