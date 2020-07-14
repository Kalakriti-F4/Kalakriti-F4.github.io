import os
import re

from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

allSections = {
    'artworks': ['painting', 'photography', 'print'],
    'merchandise': ['mugs', 'bags', 'gifts', 'coasters', 'accessories'],
    'clothing': ['sarees', 'leather', 'fabrics', 'jewellery'],
    'decor': ['home decor', 'office decor', 'furnishing'],
    'others': ['sheets', 'mats', 'handmade paper']
}

@app.route('/<section>')
def products(section):
    allFilters = allSections.get(section)
    items = []
    for f in allFilters or []:
        for rel in Itembox.query.filter_by(filterName=f).all():
            item = Item.query.get(rel.itemId)
            item.filter = f
            items.append(item)
    content = {
        'section': section,
        'allFilters': allFilters,
        'filter': request.args.get('filter'),
        'items': items
    }
    return render_template('products.html', **content)

@app.route('/item/<id>')
def item_details(id):
    pattern = re.compile("^{}-([0-9]+).jpg$".format(id))
    images = [f for f in os.listdir('./static/img/items') if pattern.match(f)]
    print(images)
    content = {
        'section': request.args.get('section'),
        'item': Item.query.get(id),
        'images': images
    }
    return render_template('item-details.html', **content)

@app.route('/addcart')
def add_cart():
    if session.get('cart'):
        session['cart'] += 1
    else:
        session['cart'] = 1
    return str(session['cart'])

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    seller = db.Column(db.String(100), nullable=False)
    sellerEmail = db.Column(db.String(100), nullable=True)
    sellerPhone = db.Column(db.String(15), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    details = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return str(self.id) + " - " + self.title

class Itembox(db.Model):
    itemId = db.Column(db.Integer, primary_key=True)
    filterName = db.Column(db.String(20), primary_key=True)

    def __repr__(self):
        return str(self.itemId) + " - " + self.filterName
