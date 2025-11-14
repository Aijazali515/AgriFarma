"""Ultra simple Flask test - no extensions, just Flask.
"""
from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
    return "<h1>Hello from Flask!</h1>"

if __name__ == '__main__':
    print("Starting ultra-simple Flask app...")
    app.run(debug=True, port=5001)
