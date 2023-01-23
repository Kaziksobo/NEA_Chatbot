import flask
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def main() -> flask.Response:
    """Displays the home page 'index.html'"""
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message() -> flask.Response:
    """requests the user's message, processes it and renders the messages page with the user's message and AI's reply"""
    user_message = request.form['message-input']
    print(user_message)
    return render_template('message.html')

@app.route('/search')
def search() -> flask.Response:
    pass

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
    
    
    