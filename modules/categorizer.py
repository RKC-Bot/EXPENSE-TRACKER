import re
import os
import json

class AIExpenseCategorizer:
    """
    AI-based expense categorization using keyword matching and pattern recognition.
    Can be upgraded to use LLM API for more accurate classification.
    """
    
    def __init__(self):
        # Category keywords mapping
        self.category_keywords = {
            'Vegetables': [
                'tomato', 'potato', 'onion', 'carrot', 'cabbage', 'spinach',
                'brinjal', 'cauliflower', 'beans', 'peas', 'capsicum', 'cucumber',
                'lettuce', 'broccoli', 'beetroot', 'radish', 'ladyfinger', 'okra'
            ],
            'Fruits': [
                'apple', 'banana', 'orange', 'mango', 'grape', 'watermelon',
                'papaya', 'pineapple', 'strawberry', 'kiwi', 'pomegranate',
                'guava', 'lemon', 'lime', 'cherry', 'peach', 'pear', 'plum'
            ],
            'Dairy': [
                'milk', 'curd', 'yogurt', 'paneer', 'cheese', 'butter',
                'ghee', 'cream', 'amul', 'mother dairy', 'nestle', 'dairy'
            ],
            'Groceries': [
                'rice', 'wheat', 'flour', 'atta', 'dal', 'lentil', 'oil',
                'sugar', 'salt', 'spice', 'masala', 'tea', 'coffee',
                'biscuit', 'bread', 'jam', 'sauce', 'pickle', 'papad'
            ],
            'Stationery': [
                'pen', 'pencil', 'paper', 'notebook', 'file', 'folder',
                'stapler', 'clip', 'tape', 'marker', 'highlighter',
                'eraser', 'sharpener', 'ruler', 'calculator', 'printer'
            ],
            'Transport': [
                'taxi', 'uber', 'ola', 'auto', 'bus', 'train', 'metro',
                'fuel', 'petrol', 'diesel', 'parking', 'toll', 'cab',
                'rickshaw', 'rapido', 'bike'
            ],
            'Utilities': [
                'electricity', 'water', 'gas', 'internet', 'wifi', 'mobile',
                'phone', 'bill', 'recharge', 'broadband', 'maintenance',
                'repair', 'plumber', 'electrician', 'cleaning'
            ],
            'Food & Beverages': [
                'restaurant', 'cafe', 'pizza', 'burger', 'sandwich', 'snack',
                'swiggy', 'zomato', 'lunch', 'dinner', 'breakfast', 'meal',
                'food', 'beverage', 'drink', 'juice', 'soda'
            ],
            'Medical': [
                'medicine', 'doctor', 'hospital', 'pharmacy', 'tablet',
                'injection', 'bandage', 'medical', 'health', 'clinic',
                'thermometer', 'first aid', 'prescription'
            ],
            'Entertainment': [
                'movie', 'cinema', 'ticket', 'netflix', 'amazon prime',
                'hotstar', 'spotify', 'game', 'subscription', 'book',
                'magazine', 'concert', 'event'
            ]
        }

        # High-priority regex rules for common OCR/invoice item names.
        self.priority_rules = [
            (r'\b(tomato|potato|onion|carrot|beetroot|cabbage|spinach|okra|ladyfinger|capsicum)\b', 'Vegetables'),
            (r'\b(apple|banana|orange|mango|grape|strawberry|papaya|pineapple|watermelon)\b', 'Fruits'),
            (r'\b(milk|curd|yogurt|paneer|cheese|butter|ghee|chach|lassi|eggs?)\b', 'Dairy'),
            (r'\b(bread|biscuit|rice|atta|flour|dal|lentil|oil|sugar|salt|tea|coffee|masala|spice)\b', 'Groceries'),
            (r'\b(uber|ola|taxi|auto|metro|bus|train|fuel|petrol|diesel|parking|toll|rickshaw|rapido)\b', 'Transport'),
            (r'\b(electricity|water|gas|internet|wifi|mobile|broadband|recharge|repair|maintenance)\b', 'Utilities'),
            (r'\b(pen|pencil|notebook|paper|stapler|marker|folder|file|calculator|printer)\b', 'Stationery'),
            (r'\b(restaurant|cafe|pizza|burger|sandwich|snack|swiggy|zomato|juice|soda)\b', 'Food & Beverages'),
            (r'\b(medicine|doctor|hospital|pharmacy|clinic|prescription|tablet|injection)\b', 'Medical'),
            (r'\b(movie|cinema|ticket|netflix|spotify|hotstar|game|subscription|concert)\b', 'Entertainment'),
        ]
        self.keywords_file = os.path.join("data", "category_keywords.json")
        self._load_custom_keywords()

    def _normalize_item(self, item_name):
        """Normalize OCR text for stable keyword matching."""
        text = item_name.lower().strip()
        # Remove common OCR punctuation noise.
        text = re.sub(r'[|:;,_+<>#*`~"\'\[\]{}()]', ' ', text)
        # Remove units/quantities.
        text = re.sub(r'\b\d+(\.\d+)?\s*(kg|g|gm|ml|l|ltr|litre|liter|pcs?|pack|pkt|dozen)\b', ' ', text)
        text = re.sub(r'\b\d+(\.\d+)?\b', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _score_categories(self, item_name):
        """Return category->score map with priority and keyword scoring."""
        normalized = self._normalize_item(item_name)
        category_scores = {category: 0 for category in self.category_keywords}

        for pattern, category in self.priority_rules:
            if re.search(pattern, normalized):
                category_scores[category] += 30

        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                kw = keyword.lower()
                if kw == normalized:
                    category_scores[category] += 20
                elif re.search(r'\b' + re.escape(kw) + r'\b', normalized):
                    category_scores[category] += 12
                elif kw in normalized:
                    category_scores[category] += 6

        return category_scores
    
    def categorize(self, item_name):
        """
        Categorize an item based on its name using keyword matching.
        Returns the most likely category.
        """
        category_scores = self._score_categories(item_name)
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        return 'Miscellaneous'
    
    def categorize_batch(self, items):
        """Categorize multiple items at once"""
        return [self.categorize(item) for item in items]
    
    def add_keyword(self, category, keyword):
        """Add a new keyword to a category"""
        if category in self.category_keywords:
            normalized = keyword.lower().strip()
            if normalized and normalized not in self.category_keywords[category]:
                self.category_keywords[category].append(normalized)
                self._save_custom_keywords()
                return True
        return False

    def remove_keyword(self, category, keyword):
        """Remove a keyword from a category."""
        if category not in self.category_keywords:
            return False
        normalized = keyword.lower().strip()
        if normalized in self.category_keywords[category]:
            self.category_keywords[category].remove(normalized)
            self._save_custom_keywords()
            return True
        return False

    def get_keywords(self, category):
        """Get keyword list for a category."""
        return sorted(self.category_keywords.get(category, []))

    def _load_custom_keywords(self):
        """Load persisted keyword overrides if present."""
        try:
            if not os.path.exists(self.keywords_file):
                return
            with open(self.keywords_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for category, keywords in data.items():
                    if category in self.category_keywords and isinstance(keywords, list):
                        clean = []
                        for kw in keywords:
                            kw = str(kw).strip().lower()
                            if kw:
                                clean.append(kw)
                        self.category_keywords[category] = list(dict.fromkeys(clean))
        except Exception:
            # Keep defaults if file is malformed or unavailable.
            pass

    def _save_custom_keywords(self):
        """Persist current category keywords for future app runs."""
        try:
            os.makedirs(os.path.dirname(self.keywords_file), exist_ok=True)
            with open(self.keywords_file, "w", encoding="utf-8") as f:
                json.dump(self.category_keywords, f, indent=2, ensure_ascii=True)
        except Exception:
            pass
    
    def get_category_confidence(self, item_name):
        """Get categorization with confidence score"""
        category_scores = self._score_categories(item_name)
        
        if max(category_scores.values()) > 0:
            best_category = max(category_scores, key=category_scores.get)
            max_score = category_scores[best_category]
            
            # Calculate confidence (0-100%)
            confidence = min(100, (max_score / 30) * 100)
            
            return best_category, confidence
        
        return 'Miscellaneous', 0

# Optional: LLM-based categorization (for future upgrade)
def categorize_with_llm(item_name, categories, api_key=None):
    """
    Use Claude API or OpenAI API for more accurate categorization.
    This is a placeholder for future implementation.
    """
    # Placeholder for LLM integration
    # You can integrate Anthropic Claude API or OpenAI API here
    pass
