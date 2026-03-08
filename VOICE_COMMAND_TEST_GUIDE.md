# 🎤 Voice Command Entry - User Test Guide

## App Status
✅ **App Running at:** http://localhost:8505

---

## 🧪 Quick Test Steps

### Test 1: Login
1. Open http://localhost:8505
2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. Click **Login**

### Test 2: Navigate to Voice Entry
1. In sidebar, look for **🎤 Voice Entry** menu option
2. Click to open voice entry feature
3. You should see:
   - Title: "🎤 Voice Command Entry"
   - Info: "Enter expense details by voice"
   - Examples section with suggested voice commands
   - Text area for entering expense description

### Test 3: Test Voice Command Parsing
**Try these commands in the text area:**

#### ✅ Commands That Work Well:
1. "Bought tomatoes for 250 rupees"
   - Expected: Item=tomatoes, Amount=₹250.00
2. "Spent 150 on milk"
   - Expected: Item=milk, Amount=₹150.00
3. "Taxi fare 200 rupees"
   - Expected: Item=taxi, Amount=₹200.00
4. "Purchased notebook 25 rupees"
   - Expected: Item=notebook, Amount=₹25.00
5. "Coffee for 100 rupees"
   - Expected: Item=coffee, Amount=₹100.00

#### ⚠️ Commands Needing More Detail:
1. "500" → Need to specify item (e.g., "groceries 500")
2. "Tomatoes" → Need amount (e.g., "tomatoes 250")

### Test 4: Process Command
1. Enter a voice command (use examples above)
2. Click **🎤 Process Voice Command** button
3. Should see:
   - ✅ Message: "Parsed Successfully"
   - Item metric showing parsed item
   - Amount metric showing parsed amount (₹XXX.XX)

### Test 5: Confirm & Add Expense
After parsing:
1. Review the parsed **Item** and **Amount**
2. Edit if needed (fields are editable)
3. **Category** should auto-populate based on item
4. Select **Employee** from dropdown
5. **Date** defaults to today's date
6. Click **✅ Add Expense** button

### Test 6: Verify in Database
1. Go to **📋 Manage Expenses** menu
2. Look for your newly added expense in the list
3. Verify details:
   - Item name
   - Amount (₹)
   - Category
   - Employee
   - Date

---

## 📋 Sample Voice Commands to Try

### Grocery Shopping 🛒
- "Bought 2kg tomatoes for 250 rupees"
- "Onions 1kg cost 150"
- "Spent 100 on potatoes"

### Office Supplies 📚
- "Purchased notebooks for 300 rupees"
- "Pen set cost 150 Rs"
- "Bought file folders 200"

### Transport 🚕
- "Taxi fare 200 rupees"
- "Bus travel 50"
- "Auto ride 80 rupees"

### Miscellaneous 🛍️
- "Coffee for 100 rupees"
- "Lunch spent 250"
- "Groceries 500 rupees"

---

## ✅ Success Indicators

When the voice command is processed successfully, you'll see:

```
✅ Parsed Successfully

Item: [extracted item name]
Amount: ₹[extracted amount]
```

And a form with fields:
- ✏️ Item Name (editable)
- 🏷️ Category (auto-suggested)
- 💰 Amount (editable)
- 👤 Employee
- 📅 Date

---

## 🚨 Troubleshooting

### Issue: Command not parsing
**Solution:** Include both item name and amount. Example:
- ❌ "500" 
- ✅ "Tomatoes 500"

### Issue: Item name seems wrong
**Solution:** Use clearer description. Example:
- ❌ "Stuff for 250"
- ✅ "Groceries for 250"

### Issue: Amount not detected
**Solution:** Make amount more explicit. Example:
- ❌ "Tomatoes very cheap"
- ✅ "Tomatoes 250 rupees"

### Issue: Menu option not showing
**Solution:** 
1. Logout and login again
2. Refresh the browser (F5)
3. Check if other menu options appear

---

## 📊 Test Checklist

- [ ] Login works
- [ ] Voice Entry menu visible
- [ ] Text input area functional
- [ ] Can enter test command
- [ ] Process button works
- [ ] Parsing shows correct item
- [ ] Parsing shows correct amount
- [ ] Can edit parsed data
- [ ] Category auto-populates
- [ ] Can select employee
- [ ] Can change date
- [ ] Add Expense button saves to DB
- [ ] Expense appears in Manage Expenses tab
- [ ] All fields saved correctly

---

## 🎯 Expected Behavior

1. **Input:** "Bought tomatoes for 250 rupees"
2. **Parse:** Item="tomatoes", Amount="250"
3. **Display:** Shows parsed values with edit option
4. **Save:** Adds to database when "Add Expense" clicked
5. **Verify:** Appears in Manage Expenses list

---

## 💡 Tips

- Use complete sentences for best results
- Include currency (rupees, Rs, or ₹)
- State amount clearly
- Edit auto-populated category if needed
- Check "Manage Expenses" tab to verify save

---

**Voice Command Feature Testing Ready!** ✅

