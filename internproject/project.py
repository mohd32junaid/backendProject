from flask import Flask, request, jsonify
import requests
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

# Function to fetch data from the third-party API
def fetch_data():
    url = 'https://s3.amazonaws.com/roxiler.com/product_transaction.json'
    response = requests.get(url)
    data = response.json()
    return data

# Function to filter transactions by month
def filter_transactions_by_month(data, month):
    filtered_transactions = [transaction for transaction in data if datetime.strptime(transaction['dateOfSale'], '%Y-%m-%d').month == month]
    return filtered_transactions

# Function to calculate total sale amount, number of sold items, and unsold items for a given month
def calculate_statistics(transactions):
    total_sale_amount = sum(transaction['price'] for transaction in transactions)
    total_sold_items = len(transactions)
    total_unsold_items = len([transaction for transaction in transactions if not transaction['sold']])
    return total_sale_amount, total_sold_items, total_unsold_items

# Function to generate bar chart data
def generate_bar_chart_data(transactions):
    price_ranges = defaultdict(int)
    for transaction in transactions:
        price = transaction['price']
        if price <= 100:
            price_ranges['0-100'] += 1
        elif price <= 200:
            price_ranges['101-200'] += 1
        elif price <= 300:
            price_ranges['201-300'] += 1
        elif price <= 400:
            price_ranges['301-400'] += 1
        elif price <= 500:
            price_ranges['401-500'] += 1
        elif price <= 600:
            price_ranges['501-600'] += 1
        elif price <= 700:
            price_ranges['601-700'] += 1
        elif price <= 800:
            price_ranges['701-800'] += 1
        elif price <= 900:
            price_ranges['801-900'] += 1
        else:
            price_ranges['901-above'] += 1
    return price_ranges

# Function to generate pie chart data
def generate_pie_chart_data(transactions):
    categories = defaultdict(int)
    for transaction in transactions:
        categories[transaction['category']] += 1
    return categories

# API endpoint to list all transactions with search and pagination support
@app.route('/transactions', methods=['GET'])
def list_transactions():
    data = fetch_data()
    month = int(request.args.get('month'))
    search_text = request.args.get('search_text', '').lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    filtered_transactions = filter_transactions_by_month(data, month)
    
    if search_text:
        filtered_transactions = [transaction for transaction in filtered_transactions
                                 if search_text in transaction['title'].lower() or
                                 search_text in transaction['description'].lower() or
                                 search_text in str(transaction['price'])]
    
    total_items = len(filtered_transactions)
    paginated_transactions = filtered_transactions[(page-1)*per_page:page*per_page]
    
    return jsonify({
        'transactions': paginated_transactions,
        'total_items': total_items
    })

# API endpoint for statistics
@app.route('/statistics', methods=['GET'])
def get_statistics():
    data = fetch_data()
    month = int(request.args.get('month'))
    transactions = filter_transactions_by_month(data, month)
    total_sale_amount, total_sold_items, total_unsold_items = calculate_statistics(transactions)
    return jsonify({
        'total_sale_amount': total_sale_amount,
        'total_sold_items': total_sold_items,
        'total_unsold_items': total_unsold_items
    })

# API endpoint for bar chart
@app.route('/bar-chart', methods=['GET'])
def get_bar_chart():
    data = fetch_data()
    month = int(request.args.get('month'))
    transactions = filter_transactions_by_month(data, month)
    bar_chart_data = generate_bar_chart_data(transactions)
    return jsonify(bar_chart_data)

# API endpoint for pie chart
@app.route('/pie-chart', methods=['GET'])
def get_pie_chart():
    data = fetch_data()
    month = int(request.args.get('month'))
    transactions = filter_transactions_by_month(data, month)
    pie_chart_data = generate_pie_chart_data(transactions)
    return jsonify(pie_chart_data)

if __name__ == '__main__':
    app.run(debug=True)
