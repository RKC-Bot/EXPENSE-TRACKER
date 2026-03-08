import streamlit as st

st.set_page_config(page_title="Test", page_icon="test.ico")
st.title("Expense Tracker - Loading...")
st.info("If you see this, Streamlit is working!")

try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
    
    st.write("Importing modules...")
    from modules.database import ExpenseDatabase
    st.success("Database module imported")
    
    from modules.categorizer import AIExpenseCategorizer
    st.success("Categorizer module imported")
    
    st.write("Initializing database...")
    db = ExpenseDatabase()
    st.success("Database initialized!")
    
    st.write("All systems operational. The full app is loading...")
    
except Exception as e:
    st.error(f"[ERROR] {type(e).__name__}: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
