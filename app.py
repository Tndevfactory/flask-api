from flask import Flask, jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import jwt
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# database
app.config['SECRET_KEY'] = 'a1e6471e-5b4f-4b25-b1a0-c3880b33601e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init sqlalchemy
db = SQLAlchemy(app)

# init marshmellow
ma = Marshmallow(app)


# product Class/Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty


# Product Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'qty')


# Init Schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# User Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name


# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'name')


# Init Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)


# Fpp
@app.route('/', methods=['GET'])
def index():
    return jsonify({'dataset': 'smart-house analysis'})


# create product
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name, description, price, qty)
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


# get all products
@app.route('/product', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)


# get single product
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)


# update product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    
    product = Product.query.get(id)
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name = name
    product.description = description
    product.price = price
    product.qty = qty

    db.session.commit()
    return product_schema.jsonify(product)


# delete product
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)


# search product by name
@app.route('/search/<q>', methods=['GET'])
def search_products(q):
    all_products = Product.query.filter(Product.name.like('%' + q + '%')).all()
    result = products_schema.dump(all_products)
    return jsonify(result)


def time_to_int(dateobj):
    total = int(dateobj.strftime('%S'))
    total += int(dateobj.strftime('%M')) * 60
    total += int(dateobj.strftime('%H')) * 60 * 60
    total += (int(dateobj.strftime('%j')) - 1) * 60 * 60 * 24
    total += (int(dateobj.strftime('%Y')) - 1970) * 60 * 60 * 24 * 365
    return total


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        global payload

        auth_header = ( request.headers["Authorization"] if "Authorization" in request.headers else "" )
        if auth_header:
            data = request.headers['Authorization']
            token = str.replace(str(data), 'Bearer ', '')   
        else:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return jsonify({'message': 'access granted , authorized valid token '}), 200
        except:
            return jsonify({'message': 'invalid token'}), 403

    return decorated

    # auth api flask


@app.route('/public', methods=['GET'])
def unprotected():
    return jsonify({'message': 'any one can view this'})


# protected route
@app.route('/auth', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'only for valid token'})



# login
@app.route('/login', methods=['POST'])
def login():

    dt = datetime.now() + timedelta(days=2)

    email = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(email=email).first()

    #return user_schema.jsonify(user)
    if user:
        if check_password_hash(user.password, password): #authentification

            token = jwt.encode({'user': email, 'exp': dt
                                }, app.config['SECRET_KEY'], algorithm='HS256') #authorization
            return jsonify({'user': email, 'token': token.decode('UTF-8')})

    return make_response('could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.json['email']
    name = request.json['name']
    password = request.json['password']

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, 
         return jsonify({'res': 'email already taken', })

    # create a new user  Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'res': ' user subscribed with success ', })

# run server
if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)
