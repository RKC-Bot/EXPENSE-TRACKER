import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class ExpenseReports:
    """
    Generate various reports and visualizations for expense tracking.
    """
    
    def __init__(self, database):
        self.db = database
    
    def get_summary_stats(self):
        """Get overall summary statistics"""
        total_expenses = self.db.get_total_expenses()
        petty_cash_balance = self.db.get_petty_cash_balance()
        total_received = self.db.get_total_petty_cash_received()
        
        expenses_df = self.db.get_all_expenses()
        
        stats = {
            'total_expenses': total_expenses,
            'petty_cash_balance': petty_cash_balance,
            'total_cash_received': total_received,
            'total_transactions': len(expenses_df) if not expenses_df.empty else 0,
            'avg_expense': expenses_df['amount'].mean() if not expenses_df.empty else 0,
        }
        
        return stats
    
    def create_category_pie_chart(self):
        """Create pie chart for expenses by category"""
        df = self.db.get_expenses_by_category()
        
        if df.empty:
            return None
        
        fig = px.pie(
            df,
            values='total',
            names='category',
            title='Expenses by Category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        return fig
    
    def create_employee_bar_chart(self):
        """Create bar chart for expenses by employee"""
        df = self.db.get_expenses_by_employee()
        
        if df.empty:
            return None
        
        fig = px.bar(
            df,
            x='employee_name',
            y='total',
            title='Expenses by Employee',
            color='total',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title='Employee',
            yaxis_title='Total Amount (₹)',
            height=400
        )
        
        return fig
    
    def create_daily_trend_chart(self, days=30):
        """Create line chart showing daily expense trends"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        df = self.db.get_expenses_by_date_range(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if df.empty:
            return None
        
        # Group by date
        daily_expenses = df.groupby('date')['amount'].sum().reset_index()
        daily_expenses['date'] = pd.to_datetime(daily_expenses['date'])
        daily_expenses = daily_expenses.sort_values('date')
        
        fig = px.line(
            daily_expenses,
            x='date',
            y='amount',
            title=f'Daily Expenses Trend (Last {days} Days)',
            markers=True
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Amount (₹)',
            height=400
        )
        
        return fig
    
    def create_category_trend_chart(self, days=30):
        """Create stacked area chart for category trends"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        df = self.db.get_expenses_by_date_range(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if df.empty:
            return None
        
        # Group by date and category
        df['date'] = pd.to_datetime(df['date'])
        category_trend = df.groupby(['date', 'category'])['amount'].sum().reset_index()
        
        fig = px.area(
            category_trend,
            x='date',
            y='amount',
            color='category',
            title=f'Category-wise Expense Trends (Last {days} Days)'
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Amount (₹)',
            height=400
        )
        
        return fig
    
    def create_monthly_comparison_chart(self, months=6):
        """Create bar chart comparing monthly expenses"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months*30)
        
        df = self.db.get_expenses_by_date_range(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if df.empty:
            return None
        
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)
        
        monthly_expenses = df.groupby('month')['amount'].sum().reset_index()
        
        fig = px.bar(
            monthly_expenses,
            x='month',
            y='amount',
            title=f'Monthly Expense Comparison (Last {months} Months)',
            color='amount',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Amount (₹)',
            height=400
        )
        
        return fig
    
    def create_top_expenses_chart(self, top_n=10):
        """Create bar chart for top expenses"""
        df = self.db.get_all_expenses()
        
        if df.empty:
            return None
        
        top_expenses = df.nlargest(top_n, 'amount')
        
        fig = px.bar(
            top_expenses,
            x='item_name',
            y='amount',
            color='category',
            title=f'Top {top_n} Expenses',
            hover_data=['date', 'employee_name']
        )
        
        fig.update_layout(
            xaxis_title='Item',
            yaxis_title='Amount (₹)',
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def generate_date_wise_report(self, start_date, end_date):
        """Generate detailed date-wise report"""
        df = self.db.get_expenses_by_date_range(start_date, end_date)
        
        if df.empty:
            return None
        
        # Add summary
        summary = {
            'total_amount': df['amount'].sum(),
            'total_transactions': len(df),
            'average_amount': df['amount'].mean(),
            'date_range': f"{start_date} to {end_date}"
        }
        
        return df, summary
    
    def generate_category_wise_report(self):
        """Generate category-wise summary report"""
        df = self.db.get_expenses_by_category()
        
        if df.empty:
            return None
        
        # Calculate percentages
        total = df['total'].sum()
        df['percentage'] = (df['total'] / total * 100).round(2)
        
        return df
    
    def generate_employee_wise_report(self):
        """Generate employee-wise summary report"""
        df = self.db.get_expenses_by_employee()
        
        if df.empty:
            return None
        
        # Calculate percentages
        total = df['total'].sum()
        df['percentage'] = (df['total'] / total * 100).round(2)
        
        # Get transaction counts
        all_expenses = self.db.get_all_expenses()
        transaction_counts = all_expenses.groupby('employee_name').size().reset_index(name='transactions')
        
        df = df.merge(transaction_counts, left_on='employee_name', right_on='employee_name')
        df['avg_per_transaction'] = (df['total'] / df['transactions']).round(2)
        
        return df
    
    def export_report_to_excel(self, report_type, start_date=None, end_date=None):
        """Export report to Excel file"""
        import io
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if report_type == 'date_wise' and start_date and end_date:
                df, summary = self.generate_date_wise_report(start_date, end_date)
                if df is not None:
                    df.to_excel(writer, sheet_name='Expenses', index=False)
                    
                    # Add summary sheet
                    summary_df = pd.DataFrame([summary])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            elif report_type == 'category_wise':
                df = self.generate_category_wise_report()
                if df is not None:
                    df.to_excel(writer, sheet_name='Category Report', index=False)
            
            elif report_type == 'employee_wise':
                df = self.generate_employee_wise_report()
                if df is not None:
                    df.to_excel(writer, sheet_name='Employee Report', index=False)
            
            elif report_type == 'all':
                # Export all data
                all_expenses = self.db.get_all_expenses()
                all_expenses.to_excel(writer, sheet_name='All Expenses', index=False)
                
                category_report = self.generate_category_wise_report()
                if category_report is not None:
                    category_report.to_excel(writer, sheet_name='By Category', index=False)
                
                employee_report = self.generate_employee_wise_report()
                if employee_report is not None:
                    employee_report.to_excel(writer, sheet_name='By Employee', index=False)
                
                petty_cash = self.db.get_all_petty_cash()
                if not petty_cash.empty:
                    petty_cash.to_excel(writer, sheet_name='Petty Cash', index=False)
        
        output.seek(0)
        return output.getvalue()
