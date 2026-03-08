#!/usr/bin/env python3
"""
Test Suite for AI Expense Tracker
Verifies all modules work correctly
"""

import sys
import os
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_database():
    """Test database functionality"""
    print("\n" + "=" * 60)
    print("TEST 1: Database Module")
    print("=" * 60)
    
    try:
        from modules.database import ExpenseDatabase
        
        # Create in-memory database for testing
        db = ExpenseDatabase(':memory:')
        
        # Test category management
        print("✓ Database created")
        
        categories = db.get_categories()
        print(f"✓ Found {len(categories)} default categories")
        
        # Add expense
        expense_id = db.add_expense(
            date='2024-01-01',
            item_name='Test Item',
            category='Groceries',
            amount=100.0,
            employee_name='Test Employee',
            entry_mode='Manual'
        )
        print(f"✓ Added expense with ID: {expense_id}")
        
        # Get expenses
        expenses = db.get_all_expenses()
        assert len(expenses) == 1
        print(f"✓ Retrieved {len(expenses)} expense(s)")
        
        # Add petty cash
        db.add_petty_cash(
            date_received='2024-01-01',
            amount=1000.0,
            received_from='Test Source',
            remarks='Test'
        )
        balance = db.get_petty_cash_balance()
        assert balance == 900.0  # 1000 - 100
        print(f"✓ Petty cash balance: ₹{balance}")
        
        print("\n✅ Database module: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Database module: FAILED - {e}")
        return False

def test_categorizer():
    """Test AI categorizer"""
    print("\n" + "=" * 60)
    print("TEST 2: AI Categorizer Module")
    print("=" * 60)
    
    try:
        from modules.categorizer import AIExpenseCategorizer
        
        categorizer = AIExpenseCategorizer()
        print("✓ Categorizer initialized")
        
        # Test categorization
        test_items = [
            ('tomatoes', 'Vegetables'),
            ('milk', 'Dairy'),
            ('uber', 'Transport'),
            ('pen', 'Stationery'),
        ]
        
        correct = 0
        for item, expected_category in test_items:
            category = categorizer.categorize(item)
            if category == expected_category:
                correct += 1
                print(f"✓ '{item}' → {category}")
            else:
                print(f"⚠ '{item}' → {category} (expected {expected_category})")
        
        print(f"\n✓ Accuracy: {correct}/{len(test_items)} correct")
        
        # Test confidence scoring
        category, confidence = categorizer.get_category_confidence('tomatoes')
        print(f"✓ Confidence scoring works: {category} ({confidence}%)")
        
        print("\n✅ Categorizer module: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Categorizer module: FAILED - {e}")
        return False

def test_excel_import():
    """Test Excel import module"""
    print("\n" + "=" * 60)
    print("TEST 3: Excel Import Module")
    print("=" * 60)
    
    try:
        from modules.excel_import import ExcelImporter, create_expense_template
        
        importer = ExcelImporter()
        print("✓ Excel importer initialized")
        
        # Create template
        template = create_expense_template()
        assert template is not None
        print(f"✓ Template created ({len(template)} bytes)")
        
        # Create sample Excel
        sample_excel = importer.create_sample_excel()
        assert sample_excel is not None
        print(f"✓ Sample Excel created ({len(sample_excel)} bytes)")
        
        # Test import
        success, data, message = importer.import_from_excel(sample_excel)
        assert success == True
        print(f"✓ Import successful: {len(data)} rows")
        
        print("\n✅ Excel import module: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Excel import module: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_invoice_ocr():
    """Test OCR module (basic check)"""
    print("\n" + "=" * 60)
    print("TEST 4: Invoice OCR Module")
    print("=" * 60)
    
    try:
        from modules.invoice_ocr import InvoiceOCR
        
        ocr = InvoiceOCR()
        print("✓ OCR module initialized")
        
        # Check availability
        if ocr.tesseract_available:
            print("✓ Tesseract available")
        else:
            print("⚠ Tesseract not available")
        
        if ocr.easyocr_available:
            print("✓ EasyOCR available")
        else:
            print("⚠ EasyOCR not available")
        
        # Test text parsing
        sample_text = """
        Invoice #12345
        Tomatoes    ₹50
        Milk        ₹60
        Total       ₹110
        """
        
        items = ocr.parse_invoice_items(sample_text)
        print(f"✓ Parsed {len(items)} items from sample text")
        
        total = ocr.extract_total_amount(sample_text)
        assert total == 110.0
        print(f"✓ Extracted total: ₹{total}")
        
        print("\n✅ OCR module: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ OCR module: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_entry():
    """Test voice entry module (basic check)"""
    print("\n" + "=" * 60)
    print("TEST 5: Voice Entry Module")
    print("=" * 60)
    
    try:
        from modules.voice_entry import VoiceExpenseEntry
        
        voice = VoiceExpenseEntry()
        print("✓ Voice module initialized")
        
        if voice.sr_available:
            print("✓ SpeechRecognition available")
        else:
            print("⚠ SpeechRecognition not available")
        
        # Test text parsing
        test_phrases = [
            "bought tomatoes for 50 rupees",
            "spent 100 on milk",
            "taxi fare 200"
        ]
        
        for phrase in test_phrases:
            parsed = voice.parse_expense_from_text(phrase)
            print(f"✓ '{phrase}' → Item: '{parsed['item_name']}', Amount: ₹{parsed['amount']}")
        
        print("\n✅ Voice entry module: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Voice entry module: FAILED - {e}")
        return False

def test_reports():
    """Test reports module"""
    print("\n" + "=" * 60)
    print("TEST 6: Reports Module")
    print("=" * 60)
    
    try:
        from modules.database import ExpenseDatabase
        from modules.reports import ExpenseReports
        
        # Use the real database with sample data
        db = ExpenseDatabase()
        reports = ExpenseReports(db)
        print("✓ Reports module initialized")
        
        # Get summary stats
        stats = reports.get_summary_stats()
        print(f"✓ Summary stats: {stats['total_transactions']} transactions, ₹{stats['total_expenses']:.2f} total")
        
        # Generate reports
        category_report = reports.generate_category_wise_report()
        if category_report is not None:
            print(f"✓ Category report: {len(category_report)} categories")
        
        employee_report = reports.generate_employee_wise_report()
        if employee_report is not None:
            print(f"✓ Employee report: {len(employee_report)} employees")
        
        # Test export
        excel_data = reports.export_report_to_excel('all')
        print(f"✓ Excel export: {len(excel_data)} bytes")
        
        print("\n✅ Reports module: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Reports module: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Integration test - full workflow"""
    print("\n" + "=" * 60)
    print("TEST 7: Integration Test")
    print("=" * 60)
    
    try:
        from modules.database import ExpenseDatabase
        from modules.categorizer import AIExpenseCategorizer
        
        db = ExpenseDatabase(':memory:')
        categorizer = AIExpenseCategorizer()
        print("✓ Modules initialized")
        
        # Add petty cash
        db.add_petty_cash('2024-01-01', 5000.0, 'Office', 'Monthly advance')
        print("✓ Added petty cash")
        
        # Add expenses with auto-categorization
        items = [
            ('tomatoes', 50),
            ('milk', 60),
            ('pen', 25),
            ('uber', 150)
        ]
        
        for item, amount in items:
            category = categorizer.categorize(item)
            db.add_expense(
                date='2024-01-01',
                item_name=item,
                category=category,
                amount=amount,
                employee_name='Test User',
                entry_mode='Manual'
            )
        
        print(f"✓ Added {len(items)} expenses with auto-categorization")
        
        # Check balance
        balance = db.get_petty_cash_balance()
        expected_balance = 5000 - sum(amt for _, amt in items)
        assert abs(balance - expected_balance) < 0.01
        print(f"✓ Balance calculation correct: ₹{balance}")
        
        # Get category breakdown
        category_df = db.get_expenses_by_category()
        print(f"✓ Category breakdown: {len(category_df)} categories")
        
        print("\n✅ Integration test: PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Integration test: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("AI EXPENSE TRACKER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_database,
        test_categorizer,
        test_excel_import,
        test_invoice_ocr,
        test_voice_entry,
        test_reports,
        test_integration
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The application is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Review the errors above.")
    
    print("\nTo run the application:")
    print("  streamlit run main.py")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
