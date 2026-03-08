import re
from datetime import datetime

class VoiceExpenseEntry:
    """
    Process voice input to extract expense information.
    Uses SpeechRecognition library with Google Speech API.
    Note: Requires PyAudio for microphone access on Windows.
    """
    
    def __init__(self):
        self.recognizer = None
        self.sr_available = False
        self.error_message = ""
        
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.sr_available = True
        except ImportError as e:
            self.error_message = f"SpeechRecognition not available: {str(e)}"
    
    def listen_from_microphone(self, duration=5):
        """
        Listen to microphone and convert speech to text.
        duration: maximum recording duration in seconds
        """
        if not self.sr_available:
            return None, "SpeechRecognition not available"
        
        try:
            with self.sr.Microphone() as source:
                print("Listening... Speak now!")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=duration)
                
                print("Processing...")
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                
                return text, None
        except self.sr.WaitTimeoutError:
            return None, "No speech detected. Please try again."
        except self.sr.UnknownValueError:
            return None, "Could not understand audio. Please speak clearly."
        except self.sr.RequestError as e:
            return None, f"Could not request results; {e}"
        except OSError as e:
            if "PyAudio" in str(e):
                return None, "PyAudio not properly installed. Please reinstall with: pip install pyaudio"
            return None, f"Audio error: {str(e)}"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def process_audio_file(self, audio_file):
        """Process audio file and convert to text"""
        if not self.sr_available:
            return None, "SpeechRecognition not available"
        
        try:
            with self.sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                return text, None
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def parse_expense_from_text(self, text):
        """
        Parse expense details from voice text.
        Expected format examples:
        - "Bought tomatoes for 50 rupees"
        - "Spent 100 on milk"
        - "Purchased notebook 25 rupees"
        - "Taxi fare 200"
        """
        
        # Clean up text
        text = text.lower().strip()
        
        # Extract amount
        amount = None
        amount_patterns = [
            r'(\d+)\s*(?:rupees|rs|inr)',
            r'for\s*(\d+)',
            r'spent\s*(\d+)',
            r'(?:cost|price|fare)\s*(\d+)',
            r'(\d+)\s*/-',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                amount = float(match.group(1))
                break
        
        # If no amount found, try to find any number
        if amount is None:
            numbers = re.findall(r'\d+', text)
            if numbers:
                amount = float(numbers[-1])  # Take last number as amount
        
        # Extract item name
        item_name = None
        
        # Remove amount-related words
        cleaned_text = re.sub(r'\d+\s*(?:rupees|rs|inr|/-)', '', text)
        cleaned_text = re.sub(r'(?:for|spent|bought|purchased|cost|price|fare)', '', cleaned_text)
        cleaned_text = re.sub(r'\d+', '', cleaned_text)
        cleaned_text = ' '.join(cleaned_text.split())  # Remove extra spaces
        
        # The remaining text is likely the item name
        if cleaned_text:
            item_name = cleaned_text.strip()
        
        # If still no item, try common patterns
        if not item_name:
            item_patterns = [
                r'(?:bought|purchased)\s+(\w+)',
                r'(\w+)\s+for',
            ]
            for pattern in item_patterns:
                match = re.search(pattern, text)
                if match:
                    item_name = match.group(1)
                    break
        
        return {
            'item_name': item_name if item_name else 'Unknown Item',
            'amount': amount if amount else 0.0,
            'raw_text': text,
            'success': item_name is not None and amount is not None
        }
    
    def interactive_voice_entry(self):
        """
        Interactive voice entry with confirmation.
        Returns parsed expense data.
        """
        # Listen to user
        text, error = self.listen_from_microphone()
        
        if error:
            return None, error
        
        # Parse the text
        parsed_data = self.parse_expense_from_text(text)
        
        return parsed_data, None

# Utility functions for voice commands
def process_voice_command(command_text):
    """
    Process general voice commands for the app.
    Examples:
    - "Show dashboard"
    - "Add expense"
    - "View reports"
    """
    command = command_text.lower().strip()
    
    commands = {
        'dashboard': ['dashboard', 'home', 'main'],
        'add_expense': ['add expense', 'new expense', 'enter expense'],
        'upload_invoice': ['upload invoice', 'scan invoice', 'add invoice'],
        'reports': ['reports', 'view reports', 'show reports'],
        'petty_cash': ['petty cash', 'cash received', 'add cash'],
    }
    
    for action, keywords in commands.items():
        for keyword in keywords:
            if keyword in command:
                return action
    
    return None
