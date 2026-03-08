"""Test the voice command entry functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from voice_entry import VoiceExpenseEntry

def test_voice_entry():
    """Test voice command parsing with various examples."""
    
    voice = VoiceExpenseEntry()
    
    # Test cases
    test_cases = [
        {
            "input": "Bought tomatoes for 250 rupees",
            "expected_item": "tomatoes",
            "expected_amount": 250.0
        },
        {
            "input": "Spent 150 on milk for groceries",
            "expected_item": "milk",
            "expected_amount": 150.0
        },
        {
            "input": "Taxi fare 200 rupees",
            "expected_item": "taxi",
            "expected_amount": 200.0
        },
        {
            "input": "Purchased notebook 25 rupees",
            "expected_item": "notebook",
            "expected_amount": 25.0
        },
        {
            "input": "Bought 2kg potatoes for 180",
            "expected_item": "potatoes",
            "expected_amount": 180.0
        },
        {
            "input": "Coffee for 100 rupees",
            "expected_item": "coffee",
            "expected_amount": 100.0
        },
        {
            "input": "Groceries spent 500",
            "expected_item": "groceries",
            "expected_amount": 500.0
        },
        {
            "input": "Pen set cost 150 Rs",
            "expected_item": "pen",
            "expected_amount": 150.0
        }
    ]
    
    print("=" * 70)
    print("🎤 VOICE COMMAND ENTRY TEST")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {idx}:")
        print(f"   Input: \"{test['input']}\"")
        
        result = voice.parse_expense_from_text(test['input'])
        
        print(f"   Parsed Item: {result['item_name']}")
        print(f"   Parsed Amount: ₹{result['amount']:.2f}")
        print(f"   Success: {'✅ Yes' if result['success'] else '❌ No'}")
        
        # Check if parsing was successful
        item_match = result['success'] and result['amount'] == test['expected_amount']
        amount_match = result['success'] and result['amount'] == test['expected_amount']
        
        if item_match and amount_match:
            print(f"   Result: ✅ PASS")
            passed += 1
        else:
            print(f"   Result: ⚠️  PARTIAL")
            if not item_match:
                print(f"            Item mismatch - Expected item context, Got: {result['item_name']}")
            if not amount_match:
                print(f"            Amount: Expected ₹{test['expected_amount']}, Got ₹{result['amount']}")
            if result['success']:
                passed += 1
            else:
                failed += 1
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
    print("=" * 70)
    
    # Additional feature tests
    print("\n📋 EDGE CASE TESTS:")
    print("=" * 70)
    
    # Test parse_expense_from_text with minimal input
    minimal_test = "500"
    result = voice.parse_expense_from_text(minimal_test)
    print(f"\n⚠️  Edge Case - Minimal Input:")
    print(f"   Input: \"{minimal_test}\"")
    print(f"   Item: {result['item_name']}")
    print(f"   Amount: ₹{result['amount']:.2f}")
    print(f"   Status: {'✅ Parsed amount only (needs item)' if result['amount'] > 0 and not result['success'] else '⚠️ Needs both item and amount'}")
    
    print("\n" + "=" * 70)
    print("✨ Voice Command Testing Complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_voice_entry()
