import io
import os
import re
from PIL import Image
from modules.categorizer import AIExpenseCategorizer

_POPLER_BIN_CACHE = None


def _find_poppler_bin():
    """Locate Poppler bin directory so pdf2image can run without relying on PATH."""
    global _POPLER_BIN_CACHE
    if _POPLER_BIN_CACHE is not None:
        return _POPLER_BIN_CACHE

    if os.system("where pdftoppm >nul 2>nul") == 0:
        _POPLER_BIN_CACHE = None
        return _POPLER_BIN_CACHE

    candidates = [
        r"C:\\Program Files\\poppler\\Library\\bin",
        r"C:\\Program Files\\poppler\\bin",
        r"C:\\Program Files (x86)\\poppler\\Library\\bin",
        r"C:\\Program Files (x86)\\poppler\\bin",
    ]

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        winget_root = os.path.join(local_appdata, "Microsoft", "WinGet", "Packages")
        if os.path.isdir(winget_root):
            for pkg in os.listdir(winget_root):
                if not pkg.lower().startswith("oschwartz10612.poppler"):
                    continue
                pkg_dir = os.path.join(winget_root, pkg)
                if not os.path.isdir(pkg_dir):
                    continue
                for child in os.listdir(pkg_dir):
                    if child.lower().startswith("poppler-"):
                        candidates.append(os.path.join(pkg_dir, child, "Library", "bin"))
                        candidates.append(os.path.join(pkg_dir, child, "bin"))

    for path in candidates:
        exe = os.path.join(path, "pdftoppm.exe")
        if os.path.isfile(exe):
            _POPLER_BIN_CACHE = path
            return _POPLER_BIN_CACHE

    _POPLER_BIN_CACHE = None
    return _POPLER_BIN_CACHE


class InvoiceOCR:
    """
    Process invoices using OCR to extract items and amounts.
    Supports both printed text (Tesseract) and handwritten text (EasyOCR).
    """

    def __init__(self):
        self.tesseract_available = False
        self.easyocr_available = False
        self.easyocr = None  # Lazy import
        self.pytesseract = None
        self.reader = None
        self.categorizer = AIExpenseCategorizer()

        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.tesseract_available = True
        except ImportError:
            pass  # Fail silently, will check availability later

    def _init_easyocr_import(self):
        """Lazy initialization of EasyOCR module."""
        if self.easyocr is None:
            try:
                import easyocr
                self.easyocr = easyocr
                self.easyocr_available = True
            except ImportError:
                self.easyocr_available = False

    def initialize_easyocr(self):
        """Lazy initialization of EasyOCR reader."""
        self._init_easyocr_import()  # Ensure module is imported first
        if self.easyocr_available and self.reader is None:
            try:
                self.reader = self.easyocr.Reader(["en"])
            except Exception as e:
                print(f"Error initializing EasyOCR: {e}")
                self.easyocr_available = False

    def extract_text_tesseract(self, image):
        """Extract text from image using Tesseract."""
        if not self.tesseract_available:
            return "Tesseract not available"

        try:
            if isinstance(image, bytes):
                image = Image.open(io.BytesIO(image))
            return self.pytesseract.image_to_string(image)
        except Exception as e:
            return f"Error: {e}"

    def extract_text_easyocr(self, image):
        """Extract text from image using EasyOCR."""
        self._init_easyocr_import()  # Lazy import
        if not self.easyocr_available:
            return "EasyOCR not available"

        try:
            self.initialize_easyocr()
            if isinstance(image, bytes):
                image = Image.open(io.BytesIO(image))

            import numpy as np

            img_array = np.array(image)
            result = self.reader.readtext(img_array)
            return " ".join([item[1] for item in result])
        except Exception as e:
            return f"Error: {e}"

    def extract_text_auto(self, image, prefer_easyocr=False):
        """Try both OCR engines and return the best result."""
        results = []

        if self.tesseract_available and not prefer_easyocr:
            tesseract_text = self.extract_text_tesseract(image)
            if tesseract_text and len(tesseract_text.strip()) > 10:
                results.append(("tesseract", tesseract_text))

        self._init_easyocr_import()  # Lazy import before checking
        if self.easyocr_available:
            easyocr_text = self.extract_text_easyocr(image)
            if easyocr_text and len(easyocr_text.strip()) > 10:
                results.append(("easyocr", easyocr_text))

        if results:
            best_result = max(results, key=lambda x: len(x[1]))
            return best_result[1], best_result[0]

        return "No text detected", "none"

    def parse_invoice_items(self, text):
        """Parse invoice text to extract (item_name, amount) tuples."""
        items = []

        amount_patterns = [
            r"(?:\u20B9|Rs\.?|INR|\$)\s*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"\$\s*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:/-|@)",
            r"(?:price|cost|rate|amount)[:\s]+(\d+(?:,\d+)*(?:\.\d{2})?)",
        ]

        lines = text.split("\n")
        processed_amounts = set()

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue

            lower_line = line.lower()
            if lower_line.startswith(
                (
                    "invoice",
                    "tax invoice",
                    "bill to",
                    "ship to",
                    "seller",
                    "order no",
                    "invoice no",
                    "date",
                    "gstin",
                    "fssai",
                    "amount in words",
                    "whether tax is payable",
                    "place of",
                    "billing address",
                    "shipping address",
                    "authorized signatory",
                )
            ):
                continue
            if lower_line.startswith(("item total", "invoice value", "total:")):
                continue

            for pattern in amount_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    try:
                        amount = float(match.group(1).replace(",", ""))
                        if amount <= 0 or amount > 1000000:
                            continue
                        if amount in processed_amounts:
                            continue

                        item_part = line[: match.start()].strip()
                        item_name = re.sub(r"^\d+\s*[xX*]\s*", "", item_part, flags=re.IGNORECASE)
                        item_name = re.sub(
                            r"\s*(?:kg|gm|g|liter|l|ml|dozen|pcs|pieces?|units?)[\s,]*$",
                            "",
                            item_name,
                            flags=re.IGNORECASE,
                        )
                        item_name = re.sub(r"^\d+[\.\)\s]+", "", item_name)
                        item_name = re.sub(r"\s+", " ", item_name).strip()

                        if item_name and len(item_name) > 2:
                            items.append((item_name, amount))
                            processed_amounts.add(amount)
                            break
                    except (ValueError, AttributeError):
                        continue

        unique_items = []
        for item, amount in items:
            is_duplicate = False
            for existing_item, existing_amount in unique_items:
                if existing_item.lower() == item.lower():
                    if abs(amount - existing_amount) / max(amount, existing_amount) < 0.1:
                        is_duplicate = True
                        break
            if not is_duplicate:
                unique_items.append((item, amount))

        if not unique_items:
            unique_items = self._parse_table_style_items(lines)
        if not unique_items:
            unique_items = self._parse_compact_table_text(text)
        if not unique_items:
            unique_items = self._parse_symbol_amount_pairs(text)

        return unique_items

    def _parse_symbol_amount_pairs(self, text):
        """
        Parse OCR text where item amounts are prefixed by symbols like '<', '₹', '$'
        in a mostly single-line sentence.
        """
        items = []
        if not text:
            return items

        compact = re.sub(r"\s+", " ", text).strip()
        pair_pattern = re.compile(
            r"([A-Za-z][A-Za-z0-9\s\-\(\)/,&]{2,}?)\s*[<₹$]\s*(\d+(?:\.\d{2})?)"
        )

        for match in pair_pattern.finditer(compact):
            raw_name = match.group(1)
            try:
                amount = float(match.group(2))
            except ValueError:
                continue

            if amount <= 0 or amount > 1000000:
                continue

            # Keep the nearest phrase before amount, not the full preceding sentence.
            name = re.split(r"[:|]", raw_name)[-1].strip()
            name = re.sub(r"\b(?:invoice|items|purchased|total|amount|date)\b", "", name, flags=re.IGNORECASE)
            name = re.sub(r"\s+", " ", name).strip(" -,:")

            if len(name) > 80:
                words = name.split()
                name = " ".join(words[-6:])

            if name and len(name) >= 3:
                items.append((name, amount))

        # Deduplicate by (normalized name, amount)
        deduped = []
        seen = set()
        for name, amount in items:
            key = (name.lower(), round(amount, 2))
            if key in seen:
                continue
            seen.add(key)
            deduped.append((name, amount))

        return deduped

    def _parse_table_style_items(self, lines):
        """Parse table-like invoice text where each field is on separate lines."""
        items = []
        if not lines:
            return items

        def is_serial_number(token):
            return bool(re.fullmatch(r"\d{1,3}", token)) and int(token) > 0

        def parse_numeric(token):
            token = token.strip().replace(",", "")
            if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", token):
                try:
                    return float(token)
                except ValueError:
                    return None
            return None

        header_start = 0
        for i, line in enumerate(lines):
            if line.strip().lower() == "sr":
                header_start = i
                break

        i = header_start
        while i < len(lines):
            token = lines[i].strip()
            if not is_serial_number(token):
                i += 1
                continue

            serial = int(token)
            j = i + 1
            block = []
            while j < len(lines):
                nxt = lines[j].strip()
                if is_serial_number(nxt) and int(nxt) == serial + 1 and len(block) >= 5:
                    break
                lower_nxt = nxt.lower()
                if lower_nxt.startswith("item total") or lower_nxt.startswith("invoice value"):
                    break
                block.append(nxt)
                j += 1

            name_parts = []
            for part in block:
                if parse_numeric(part) is not None:
                    break
                if len(part) > 1 and not re.fullmatch(r"[A-Za-z/&\-\s]{1,5}", part):
                    name_parts.append(part)

            if not name_parts:
                for part in block:
                    if parse_numeric(part) is not None:
                        break
                    if len(part) > 1:
                        name_parts.append(part)

            item_name = re.sub(r"\s+", " ", " ".join(name_parts).strip())

            amount = None
            numeric_values = []
            for part in block:
                value = parse_numeric(part)
                if value is not None and 0 < value <= 1000000:
                    numeric_values.append(value)

            if numeric_values:
                base_price = numeric_values[0]
                upper_bound = max(base_price * 1.5, base_price + 20)
                candidates = [v for v in numeric_values if 1 <= v <= upper_bound]
                if candidates:
                    for value in reversed(candidates):
                        if candidates.count(value) >= 2:
                            amount = value
                            break
                    if amount is None:
                        amount = candidates[-1]
                if amount is None:
                    amount = numeric_values[-1]

            if item_name and amount is not None:
                items.append((item_name, amount))

            i = j if j > i else i + 1
            if serial > 500 or len(items) > 200:
                break

        return items

    def _parse_compact_table_text(self, text):
        """Parse flattened invoice text where row breaks are lost."""
        items = []
        if not text:
            return items

        compact = re.sub(r"\s+", " ", text).strip()

        row_patterns = [
            re.compile(
                r"(?:^|\s)(?:\d+\s+)?(?P<name>[A-Za-z][A-Za-z0-9\s\-\(\)&,/]{2,}?)\s+"
                r"\d+\.\d{2}\s+\d{6,8}\s+.*?\s(?P<amount>\d+\.\d{2})\s+\+\s*0\.00",
                re.IGNORECASE,
            ),
            re.compile(
                r"(?:^|\s)(?:\d+\s+)?(?P<name>[A-Za-z][A-Za-z0-9\s\-\(\)&,/]{2,}?)\s+0\.00%\s+"
                r"(?:[A-Za-z]+\s+)?\d+(?:\.\d{2})?\s+\d{6,8}\s+.*?\s(?P<amount>\d+\.\d{2})\s+\+\s*0\.00",
                re.IGNORECASE,
            ),
        ]

        for row_pattern in row_patterns:
            for match in row_pattern.finditer(compact):
                name = re.sub(r"\s+", " ", match.group("name")).strip(" -,:")
                name = re.sub(r".*(?:description|amt_?|sr item & unit product)\s+", "", name, flags=re.IGNORECASE)
                try:
                    amount = float(match.group("amount"))
                except (TypeError, ValueError):
                    continue

                if not name or amount <= 0:
                    continue

                lower_name = name.lower()
                if any(x in lower_name for x in ["invoice", "gst", "item total", "invoice value"]):
                    continue

                items.append((name, amount))

        deduped = []
        seen = set()
        for name, amount in items:
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append((name, amount))

        return deduped

    def extract_total_amount(self, text):
        """Extract total amount from invoice text."""
        total_patterns = [
            r"(?:grand\s+)?total[:\s]+(?:\u20B9|Rs\.?|INR|\$)?[\s]*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"amount\s+(?:due|payable|to\s+pay)[:\s]+(?:\u20B9|Rs\.?|INR|\$)?[\s]*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"net\s+(?:amount|total)[:\s]+(?:\u20B9|Rs\.?|INR|\$)?[\s]*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"(?:final\s+)?amount[:\s]+(?:\u20B9|Rs\.?|INR|\$)?[\s]*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"total\s+(?:amount|to\s+pay)[:\s]+(?:\u20B9|Rs\.?|INR|\$)?[\s]*(\d+(?:,\d+)*(?:\.\d{2})?)",
            r"(?:\u20B9|Rs\.?|INR|\$)\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:only|/-|total)",
        ]

        text_lower = text.lower()
        for pattern in total_patterns:
            for match in re.finditer(pattern, text_lower):
                try:
                    amount = float(match.group(1).replace(",", ""))
                    if 0 < amount <= 10000000:
                        return amount
                except (ValueError, IndexError):
                    continue

        return None

    def process_invoice(self, image, prefer_easyocr=False):
        """Complete invoice OCR processing pipeline."""
        text, method = self.extract_text_auto(image, prefer_easyocr)
        parsed_items = self.parse_invoice_items_ai(text)
        items = [(row["item_name"], row["amount"]) for row in parsed_items]
        total = self.extract_total_amount(text)

        if total is None and items:
            total = sum(amount for _, amount in items)

        return {
            "text": text,
            "items": items,
            "parsed_items": parsed_items,
            "total": total,
            "ocr_method": method,
            "item_count": len(parsed_items),
        }

    def parse_invoice_items_ai(self, text):
        """
        Intelligent parser that returns structured rows:
        [{"item_name": ..., "amount": ..., "category": ..., "confidence": ...}, ...]
        """
        if not text:
            return []

        raw_items = self.parse_invoice_items(text)
        enriched = self._enrich_items(raw_items)

        # Fallback for noisy OCR lines that may miss in existing strategies.
        if not enriched:
            fallback_items = self._parse_amount_anchored_lines(text)
            enriched = self._enrich_items(fallback_items)

        return enriched

    def _enrich_items(self, items):
        structured = []
        seen = set()
        for item_name, amount in items:
            clean_name = self._clean_item_name(item_name)
            if not clean_name or self._is_noise_item(clean_name):
                continue
            if amount <= 0:
                continue
            key = (clean_name.lower(), round(float(amount), 2))
            if key in seen:
                continue
            seen.add(key)
            category, confidence = self.categorizer.get_category_confidence(clean_name)
            structured.append(
                {
                    "item_name": clean_name,
                    "amount": float(amount),
                    "category": category if category else "Miscellaneous",
                    "confidence": round(float(confidence), 1),
                }
            )
        return structured

    def _clean_item_name(self, name):
        name = (name or "").strip()
        name = re.sub(r"\b(?:qty|rate|amt|amount|cgst|sgst|igst|cess|hsn|mrp|disc)\b", " ", name, flags=re.IGNORECASE)
        name = re.sub(r"\b\d+(?:\.\d+)?\b", " ", name)
        name = re.sub(r"\s+", " ", name).strip(" -,:;/")
        return name

    def _is_noise_item(self, name):
        lower = name.lower()
        noise_terms = [
            "invoice", "total", "tax", "gst", "cgst", "sgst", "igst",
            "cess", "amount in words", "bill to", "ship to", "seller",
            "hsn", "item total", "invoice value", "round off", "net amount",
        ]
        return any(term in lower for term in noise_terms) or len(lower) < 3

    def _parse_amount_anchored_lines(self, text):
        """
        Fallback parser: in each line, pick a likely amount and infer item name
        from the alpha-heavy prefix.
        """
        items = []
        amount_rx = re.compile(r"(?<!\d)(\d{1,6}(?:\.\d{1,2})?)(?!\d)")

        for line in text.splitlines():
            line = line.strip()
            if len(line) < 5:
                continue
            if self._is_noise_item(line):
                continue

            matches = list(amount_rx.finditer(line))
            if not matches:
                continue

            # choose rightmost realistic amount
            amount = None
            amount_match = None
            for m in reversed(matches):
                try:
                    val = float(m.group(1))
                except ValueError:
                    continue
                if 1 <= val <= 1000000:
                    amount = val
                    amount_match = m
                    break
            if amount is None or amount_match is None:
                continue

            name_part = line[: amount_match.start()].strip()
            # Keep only the rightmost phrase likely to be item name.
            name_part = re.split(r"[:|]", name_part)[-1].strip()
            name_part = re.sub(r"\s+", " ", name_part).strip(" -,:;/")

            if name_part and not self._is_noise_item(name_part):
                items.append((name_part, amount))

        return items


def extract_from_pdf(pdf_file):
    """Extract text/items from PDF invoice."""
    pdf_bytes = pdf_file if isinstance(pdf_file, bytes) else pdf_file.read()
    ocr = InvoiceOCR()

    # 1) Try direct text extraction first (works best for digital PDFs).
    direct_text = ""
    try:
        try:
            from pypdf import PdfReader
        except ImportError:
            import PyPDF2

            PdfReader = PyPDF2.PdfReader

        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        text_parts = []
        for page in pdf_reader.pages:
            extracted = page.extract_text() or ""
            if extracted:
                text_parts.append(extracted)
        direct_text = "\n".join(text_parts).strip()
    except Exception:
        direct_text = ""

    if direct_text:
        parsed_items = ocr.parse_invoice_items_ai(direct_text)
        items = [(row["item_name"], row["amount"]) for row in parsed_items]
        total = ocr.extract_total_amount(direct_text) or (sum(amount for _, amount in items) if items else None)
        return {
            "text": direct_text,
            "items": items,
            "parsed_items": parsed_items,
            "total": total,
            "ocr_method": "pdf_direct_text",
            "item_count": len(parsed_items),
        }

    # 2) Fallback to OCR for scanned/image PDFs.
    try:
        from pdf2image import convert_from_bytes

        poppler_path = _find_poppler_bin()
        kwargs = {}
        if poppler_path:
            kwargs["poppler_path"] = poppler_path

        images = convert_from_bytes(pdf_bytes, **kwargs)
        if images:
            all_text = []
            all_parsed = []
            for image in images:
                page_result = ocr.process_invoice(image)
                if page_result.get("text"):
                    all_text.append(page_result["text"])
                all_parsed.extend(page_result.get("parsed_items", []))

            deduped = []
            seen = set()
            for row in all_parsed:
                key = (row.get("item_name", "").lower(), round(float(row.get("amount", 0)), 2))
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(row)

            items = [(row["item_name"], row["amount"]) for row in deduped]
            text = "\n".join(all_text)
            total = ocr.extract_total_amount(text) or (sum(amount for _, amount in items) if items else None)

            return {
                "text": text,
                "items": items,
                "parsed_items": deduped,
                "total": total,
                "ocr_method": "pdf_multi_page_ocr",
                "item_count": len(deduped),
            }
    except Exception as e:
        return {"error": str(e)}

    return {"error": "No extractable text found in PDF."}

