from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/products')
def get_products():
    """A simple endpoint to return a list of products."""
    products = [
        {'id': 1, 'name': 'Laptop', 'stock': 150},
        {'id': 2, 'name': 'Mouse', 'stock': 800},
        {'id': 3, 'name': 'Keyboard', 'stock': 450}
    ]
    return jsonify(products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
