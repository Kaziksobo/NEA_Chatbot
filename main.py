import flask
from flask import Flask, render_template, request

app = Flask(__name__)

# displays the home page
@app.route('/')
def main() -> flask.Response:
    return render_template('index.html')

@app.route('/message', methods=['POST', 'GET'])
def test() -> flask.Response:
    message = request.form['message']
    return render_template('message.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)