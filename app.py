from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# databae
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init sqlalchemy
db = SQLAlchemy(app)

# init marshmellow
ma = Marshmallow(app)

#product Class/Model
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
        fields = ('id', 'name', 'description', 'price' , 'qty')  

# Init Schema 
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

#Fpp 
@app.route('/', methods=['GET'])
def index():
     
    return jsonify({'dataset': 'smart-house analysis'})


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

#get all products

@app.route('/product', methods=['GET'])
def get_products():
    
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
   
    return jsonify(result)

# run server 
if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)