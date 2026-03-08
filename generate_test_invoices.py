"""Generate sample invoice images for testing OCR functionality."""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def create_invoice_image(filename, items_data, total_amount):
    """Create a sample invoice image with text."""
    # Create a new image with white background
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        header_font = ImageFont.truetype("arial.ttf", 14)
        text_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    y_position = 20
    
    # Title
    draw.text((150, y_position), "INVOICE RECEIPT", fill='black', font=title_font)
    y_position += 50
    
    # Invoice details
    draw.text((50, y_position), "Date: 2024-03-07", fill='black', font=text_font)
    draw.text((50, y_position + 25), "Invoice #: INV-2024-001", fill='black', font=text_font)
    y_position += 70
    
    # Items header
    draw.text((50, y_position), "ITEMS PURCHASED:", fill='black', font=header_font)
    y_position += 35
    
    # Items
    item_num = 1
    for item_name, amount in items_data:
        line = f"{item_num}. {item_name} ₹{amount:.2f}"
        draw.text((70, y_position), line, fill='black', font=text_font)
        y_position += 25
        item_num += 1
    
    # Total
    y_position += 20
    draw.text((50, y_position), "=" * 50, fill='black', font=text_font)
    y_position += 25
    draw.text((50, y_position), f"TOTAL AMOUNT: ₹{total_amount:.2f}", fill='black', font=header_font)
    y_position += 30
    draw.text((50, y_position), "=" * 50, fill='black', font=text_font)
    
    # Footer
    y_position += 40
    draw.text((150, y_position), "Thank you for your purchase!", fill='black', font=text_font)
    
    # Save image
    os.makedirs('data/invoices', exist_ok=True)
    img.save(filename)
    print(f"✅ Created: {filename}")

# Generate sample invoices
print("🚀 Generating sample test invoices...")

# Invoice 1: Groceries
items1 = [
    ("Tomatoes (2 kg)", 250.00),
    ("Onions (1 kg)", 150.00),
    ("Potatoes (3 kg)", 180.00),
    ("Carrots (1 kg)", 100.00),
    ("Lettuce (1 bunch)", 75.00),
]
create_invoice_image('data/invoices/sample_invoice_groceries.png', items1, 755.00)

# Invoice 2: Office Supplies
items2 = [
    ("Ballpoint Pens (pack of 10)", 150.00),
    ("Notebooks (5 units)", 250.00),
    ("File Folders (pack)", 120.00),
    ("Stapler", 200.00),
    ("Sticky Notes", 100.00),
]
create_invoice_image('data/invoices/sample_invoice_office.png', items2, 820.00)

# Invoice 3: Mixed Items
items3 = [
    ("Coffee Beans (500g)", 450.00),
    ("Sugar (1 kg)", 80.00),
    ("Milk (1 liter, pack of 2)", 120.00),
    ("Bread (2 loaves)", 100.00),
    ("Butter (200g)", 150.00),
]
create_invoice_image('data/invoices/sample_invoice_mixed.png', items3, 900.00)

print("\n✨ All sample invoices generated successfully!")
print("\n📂 Generated files in 'data/invoices/':")
print("  1. sample_invoice_groceries.png - Grocery store invoice")
print("  2. sample_invoice_office.png - Office supplies invoice")
print("  3. sample_invoice_mixed.png - Mixed items invoice")
print("\n💡 You can now upload these files in the 'Upload Invoice' tab!")
