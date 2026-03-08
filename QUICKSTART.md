# 🚀 QUICK START GUIDE - AI Expense Tracker

## ⚡ Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd expense_tracker
python setup_check.py
```

This automatically:
- Checks for all required packages
- Installs missing dependencies
- Verifies Tesseract OCR installation
- Runs basic tests
- Creates necessary directories

### Step 2: Generate Sample Data (Optional)
```bash
python sample_data_generator.py
```

This creates:
- 50 sample expenses across different categories
- 10 petty cash receipts
- Realistic test data for exploring the app

### Step 3: Run the Application
```bash
streamlit run main.py
```

Your browser will automatically open to: `http://localhost:8501`

---

## 📋 System Requirements

### Required
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

---

## 🎯 Core Features

### 1. Dashboard
View your expense summary, charts, and recent transactions at a glance.

### 2. Add Expense (Manual)
- Simple form-based entry
- Auto-categorization suggestions
- Date, item, category, amount, employee

### 3. Upload Invoice (OCR)
- Upload JPG/PNG/PDF invoices
- Automatic text extraction (printed & handwritten)
- Smart item and amount detection
- Duplicate detection using SHA256 hash
- One-click categorization

### 4. Upload Excel
- Bulk import from Excel files
- Download template with correct format
- Auto-validation and error reporting
- Supports columns: Date | Item | Category | Amount | Employee

### 5. Voice Entry
- Speak your expense
- Example: "Bought tomatoes for 50 rupees"
- Automatic parsing and categorization
- Review before saving

### 6. Petty Cash Management
- Track cash received
- Monitor running balance
- Complete transaction history

### 7. Reports
- Date-wise, Category-wise, Employee-wise
- Interactive charts (Plotly)
- Excel export
- Trend analysis

### 8. Category & Employee Management
- Add/delete categories
- Add/delete employees
- 8+ default categories included

---

## 📊 Excel Template Format

When uploading Excel files, use this format:

| Date       | Item      | Category    | Amount | Employee   |
|------------|-----------|-------------|--------|------------|
| 2024-01-15 | Tomatoes  | Vegetables  | 50     | John Doe   |
| 2024-01-15 | Milk      | Dairy       | 60     | Jane Smith |
| 2024-01-16 | Notebook  | Stationery  | 25     | John Doe   |

Download the template from the app: **Upload Excel → Download Template**

---

## 🎤 Voice Entry Examples

Speak naturally. The system will parse item and amount:

- "Bought tomatoes for 50 rupees"
- "Spent 100 on milk"
- "Taxi fare 200"
- "Purchased notebook 25 rupees"

---

## 📄 Invoice Upload Tips

### For Best Results:
1. **Good Lighting**: Clear, well-lit images
2. **High Resolution**: At least 1024x768
3. **Straight Angle**: Avoid tilted or angled photos
4. **Clean Background**: Minimal shadows or clutter

### Supported Formats:
- Images: JPG, JPEG, PNG
- Documents: PDF

### OCR Options:
- **Tesseract**: Fast, accurate for printed text
- **EasyOCR**: Better for handwritten notes (slower)

---

## 🗂️ Project Structure

```
expense_tracker/
│
├── main.py                      # Main Streamlit app
├── requirements.txt             # Python dependencies
├── setup_check.py              # Auto-installer & checker
├── sample_data_generator.py    # Test data generator
├── test_suite.py               # Comprehensive tests
├── README.md                   # Full documentation
│
├── modules/
│   ├── database.py             # SQLite operations
│   ├── categorizer.py          # AI categorization
│   ├── invoice_ocr.py          # OCR processing
│   ├── voice_entry.py          # Voice recognition
│   ├── excel_import.py         # Excel import/export
│   └── reports.py              # Charts & reports
│
├── data/
│   └── invoices/               # Stored invoice files
│
└── db/
    └── expenses.db             # SQLite database
```

---

## 🧪 Testing the Application

### Run Comprehensive Tests:
```bash
python test_suite.py
```

Tests include:
- Database operations
- AI categorization accuracy
- Excel import/export
- OCR text parsing
- Voice entry parsing
- Reports generation
- Full integration workflow

Expected Result: **6/7 tests pass** (Plotly requires manual install)

---

## 🔧 Troubleshooting

### "Tesseract not found"
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# MacOS
brew install tesseract

# Check installation
tesseract --version
```

### "Module not found"
```bash
# Re-run setup
python setup_check.py

# Or install manually
pip install -r requirements.txt --break-system-packages
```

### "SpeechRecognition not working"
```bash
# Install PyAudio for microphone support
pip install PyAudio --break-system-packages
```

### "Database locked"
- Close any open database connections
- Restart the application
- Check file permissions

---

## 📱 Future Enhancements

### Coming Soon:
- [ ] LLM-powered smart categorization (Claude/GPT)
- [ ] Mobile app (React Native/Flutter)
- [ ] Email parser (auto-import from Gmail)
- [ ] Receipt auto-fetch (Amazon, Swiggy, etc.)
- [ ] Budget tracking & alerts
- [ ] Multi-currency support
- [ ] Cloud sync

---

## 🎓 Learning Resources

### AI Categorization
The system uses keyword matching for categorization. Test it:
1. Go to "Add Expense"
2. Use the "AI Category Suggestion" section
3. Enter different items to see how they're categorized

### Understanding the Database
- SQLite database stored in `db/expenses.db`
- 5 tables: expenses, petty_cash, invoices, categories, employees
- View with: `sqlite3 db/expenses.db`

### Extending Categories
Add your own keywords to `modules/categorizer.py`:
```python
self.category_keywords = {
    'Your Category': ['keyword1', 'keyword2', 'keyword3']
}
```

---

## 💡 Pro Tips

### 1. Bulk Import
Use Excel upload for monthly expense dumps

### 2. OCR Accuracy
For handwritten receipts, enable "handwriting recognition"

### 3. Duplicate Prevention
Upload invoices immediately - duplicate detection prevents double-entry

### 4. Quick Entry
Use voice entry for single items on-the-go

### 5. Regular Backups
Export reports weekly and backup the database:
```bash
cp db/expenses.db db/expenses_backup_$(date +%Y%m%d).db
```

---

## 🔐 Security Notes

- Database stored locally (no cloud by default)
- Invoice images saved in `data/invoices/`
- Use HTTPS in production deployments
- Regular backups recommended
- No personal data sent to external services (OCR runs locally)

---

## 📞 Support

For issues:
1. Check this guide
2. Run `python test_suite.py` to diagnose
3. Review `setup_check.py` output
4. Check README.md for detailed docs

---

## ✅ Checklist Before First Run

- [ ] Python 3.8+ installed
- [ ] Tesseract OCR installed
- [ ] Ran `python setup_check.py`
- [ ] Generated sample data (optional)
- [ ] Ready to run `streamlit run main.py`

---

**Happy Expense Tracking! 💰📊**

Made with ❤️ using Python, Streamlit, and AI
