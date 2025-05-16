from flask import Flask, jsonify, request, session
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Sample database (in a real app, use a proper database)
users_db = []
products_db = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 99.99,
        "category": "Electronics",
        "description": "High-quality wireless headphones with noise cancellation",
        "imageUrl": "https://via.placeholder.com/300x200?text=Headphones",
        "stock": 10
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 199.99,
        "category": "Electronics",
        "description": "Feature-rich smartwatch with health monitoring",
        "imageUrl": "https://via.placeholder.com/300x200?text=Smart+Watch",
        "stock": 5
    },
    {
        "id": 3,
        "name": "Running Shoes",
        "price": 79.99,
        "category": "Sports",
        "description": "Comfortable running shoes with cushioning",
        "imageUrl": "https://via.placeholder.com/300x200?text=Running+Shoes",
        "stock": 15
    },
    {
        "id": 4,
        "name": "Backpack",
        "price": 49.99,
        "category": "Accessories",
        "description": "Durable backpack with multiple compartments",
        "imageUrl": "https://via.placeholder.com/300x200?text=Backpack",
        "stock": 20
    },
    {
        "id": 5,
        "name": "Coffee Maker",
        "price": 129.99,
        "category": "Home",
        "description": "Automatic coffee maker with timer",
        "imageUrl": "https://via.placeholder.com/300x200?text=Coffee+Maker",
        "stock": 8
    },
    {
        "id": 6,
        "name": "Yoga Mat",
        "price": 29.99,
        "category": "Sports",
        "description": "Non-slip yoga mat with carrying strap",
        "imageUrl": "https://via.placeholder.com/300x200?text=Yoga+Mat",
        "stock": 12
    }
]

# JWT Configuration
JWT_SECRET = 'your_jwt_secret_key'  # In production, use a more secure key
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600  # 1 hour in seconds

# Helper function to generate JWT token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Routes
@app.route('/')
def home():
    return "ShopEase Backend API"

# User Authentication
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not email or not password or not name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if any(user['email'] == email for user in users_db):
        return jsonify({'error': 'Email already registered'}), 400
    
    new_user = {
        'id': len(users_db) + 1,
        'name': name,
        'email': email,
        'password': password,  # In production, hash the password
        'isAdmin': False,
        'createdAt': datetime.utcnow().isoformat()
    }
    
    users_db.append(new_user)
    token = generate_token(new_user['id'])
    
    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': {
            'id': new_user['id'],
            'name': new_user['name'],
            'email': new_user['email'],
            'isAdmin': new_user['isAdmin']
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = next((user for user in users_db if user['email'] == email and user['password'] == password), None)
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    token = generate_token(user['id'])
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'isAdmin': user['isAdmin']
        }
    })

# Products
@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products_db)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products_db if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

# Cart
@app.route('/api/cart', methods=['GET'])
def get_cart():
    if 'cart' not in session:
        session['cart'] = []
    return jsonify(session['cart'])

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    product = next((p for p in products_db if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart_item = next((item for item in session['cart'] if item['product_id'] == product_id), None)
    if cart_item:
        cart_item['quantity'] += quantity
    else:
        session['cart'].append({
            'product_id': product_id,
            'quantity': quantity,
            'name': product['name'],
            'price': product['price'],
            'imageUrl': product['imageUrl']
        })
    
    session.modified = True
    return jsonify({'message': 'Product added to cart', 'cart': session['cart']})

@app.route('/api/cart/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
        return jsonify({'message': 'Cart is empty'})
    
    session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
    session.modified = True
    return jsonify({'message': 'Product removed from cart', 'cart': session['cart']})

if __name__ == '__main__':
    app.run(debug=True)