from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for Expense
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)

# Create the database (run once to create the tables)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Total Expenses Calculation
    expenses = Expense.query.all()
    total_expenses = sum(exp.amount for exp in expenses)
    
    return render_template('index.html', total_expenses=total_expenses)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        category = request.form['category']
        expense = Expense(name=name, amount=amount, category=category)
        
        db.session.add(expense)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('add_expense.html')

@app.route('/view_expenses', methods=['GET'])
def view_expenses():
    filter_option = request.args.get('filter', 'all')
    
    if filter_option == 'monthly':
        start_date = datetime.utcnow().replace(day=1)  # First day of the current month
        expenses = Expense.query.filter(Expense.date >= start_date).all()
    elif filter_option == 'weekly':
        start_date = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())  # Start of the week (Monday)
        expenses = Expense.query.filter(Expense.date >= start_date).all()
    else:  # All expenses
        expenses = Expense.query.all()
    
    total_expenses = sum(exp.amount for exp in expenses)
    return render_template('view_expenses.html', expenses=expenses, total_expenses=total_expenses, filter=filter_option)

@app.route('/delete_expense/<int:id>', methods=['GET'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/manage_expenses', methods=['GET'])
def manage_expenses():
    expenses = Expense.query.all()
    
    # Example logic for spending categories visualization (Bar chart logic or similar can be added here)
    categories = ['Food', 'Rent', 'Utilities', 'Entertainment']
    amounts = {category: sum(exp.amount for exp in expenses if exp.category == category) for category in categories}

    return render_template('manage_expenses.html', expenses=expenses, amounts=amounts)

@app.route('/daily_record', methods=['GET', 'POST'])
def daily_record():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        expense = Expense(name=name, amount=amount, category="Daily")
        
        db.session.add(expense)
        db.session.commit()
    
    # Get today's expenses
    today = datetime.utcnow().date()
    daily_expenses = Expense.query.filter(Expense.date == today).all()
    total_daily_expenses = sum(exp.amount for exp in daily_expenses)
    
    return render_template('daily_record.html', daily_expenses=daily_expenses, total_daily_expenses=total_daily_expenses)

@app.route('/spending_suggestions')
def spending_suggestions():
    expenses = Expense.query.all()
    # Example logic: Suggest reducing categories where spending is high
    categories = ['Food', 'Rent', 'Utilities', 'Entertainment']
    spending_by_category = {category: sum(exp.amount for exp in expenses if exp.category == category) for category in categories}
    
    suggestions = []
    for category, amount in spending_by_category.items():
        if amount > 200:  # Example threshold for suggestion
            suggestions.append(f"Consider reducing your spending on {category} by 20%. Current spending: ${amount}.")

    return render_template('spending_suggestions.html', suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True)

