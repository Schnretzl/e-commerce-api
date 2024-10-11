from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError
from my_password import my_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/e_commerce_api'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class CustomerSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    email = fields.String(required=True, validate=validate.Email())
    phone = fields.String(required=True, validate=validate.Regexp(r'^\d{10}$'))
    address = fields.String(required=True, validate=validate.Length(min=1))
    
    class Meta:
        fields = ('name', 'email', 'phone', 'address', 'id')
        
class CustomerAccountSchema(ma.Schema):
    customer_id = fields.Integer(required=True)
    username = fields.String(required=True, validate=validate.Length(min=3))
    password = fields.String(required=True, validate=validate.Length(min=6))
    
    class Meta:
        fields = ('customer_id', 'username', 'password', 'id')
        
class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock = fields.Integer(validate=validate.Range(min=0))
    
    class Meta:
        fields = ('name', 'price', 'id')
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique = True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    
class CustomerAccount(db.Model):
    __tablename__ = 'customer_accounts'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    username = db.Column(db.String(100), unique = True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    customer = db.relationship('Customer', backref='customer_accounts', uselist=False)
    
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    
with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)
    
# ====================================================================================================
# Routes for customers
# ====================================================================================================
    
@app.route('/customers', methods=['POST'])
def add_customer():
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    address = request.json['address']
    username = request.json['username']
    password = request.json['password']
    
    new_customer = Customer(name=name, email=email, phone=phone, address=address)
    new_customer_account = CustomerAccount(customer_id=new_customer.id, username=username, password=password)
    db.session.add(new_customer)
    db.session.add(new_customer_account)
    db.session.commit()
    
    return jsonify({'message': 'Customer and account created successfully!'}), 201

@app.route('/customers/<int:id>', methods=['GET'])
def read_customer(id):
    customer = Customer.query.get(id)
    if customer:
        return customer_schema.jsonify(customer)
    return jsonify({'message': 'Customer not found!'}), 404

@app.route('/customers', methods=['GET'])
def get_all_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'message': 'Customer not found!'}), 404
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    address = request.json['address']
    customer.name = name
    customer.email = email
    customer.phone = phone
    customer.address = address
    db.session.commit()
    return jsonify({'message': 'Customer updated successfully!'}), 200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'message': 'Customer not found!'}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully!'}), 200

# ====================================================================================================
# Routes for customer accounts
# ====================================================================================================

@app.route('/customer_accounts', methods=['POST'])
def add_customer_account():
    customer_id = request.json['customer_id']
    username = request.json['username']
    password = request.json['password']
    
    new_customer_account = CustomerAccount(customer_id=customer_id, username=username, password=password)
    db.session.add(new_customer_account)
    db.session.commit()
    
    return jsonify({'message': 'Customer account created successfully!'}), 201

# ====================================================================================================
# Routes for products
# ====================================================================================================

@app.route('/products', methods=['POST'])
def add_product():
    name = request.json['name']
    price = request.json['price']
    stock = request.json['stock']
    
    new_product = Product(name=name, price=price, stock=stock)
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({'message': 'Product created successfully!'}), 201