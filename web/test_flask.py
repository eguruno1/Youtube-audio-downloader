from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Flask is working!</h1>'

if __name__ == '__main__':
    print("Testing Flask on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
