#!/usr/bin/env python
"""Run Streamlit app with explicit output handling for Python 3.14"""
import sys
import os

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

print("Starting Expense Tracker...", flush=True)
print(f"Python: {sys.version}", flush=True)
print(f"Working directory: {os.getcwd()}", flush=True)

try:
    import streamlit.web.cli as cli
    print("[1/3] Streamlit imported successfully", flush=True)
    
    # Set up arguments
    sys.argv = [
        'streamlit',
        'run',
        'main.py',
        '--server.headless=false',
        '--logger.level=info',
        '--client.logger.enabled=false'
    ]
    
    print("[2/3] Running Streamlit...", flush=True)
    cli.main()
    print("[3/3] Streamlit exited", flush=True)
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
