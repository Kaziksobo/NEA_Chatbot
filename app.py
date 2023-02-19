import flask
from flask import Flask, render_template, request
from app_functions import reply_generator, log

current_theme = 'light'
current_page = 'index.html'
stylesheet = 'static/light-styles.css'

app = Flask(__name__)

@app.route('/')
def main() -> flask.Response:
    """Displays the home page 'index.html'"""
    
    global stylesheet
    return render_template('index.html', stylesheet=stylesheet)

@app.route('/message', methods=['GET', 'POST'])
def message() -> flask.Response:
    """Requests the user's message, processes it and renders the messages page with the user's message and AI's reply"""
    
    global stylesheet, current_page
    
    user_message = request.form['message-input']
    reply, time = reply_generator(user_message)
    log(
        user_message=user_message,
        bot_response=reply,
        time_taken=time
    )
    
    current_page = 'message.html'
    return render_template('message.html', stylesheet=stylesheet)

@app.route('/theme', methods=['GET', 'POST'])
def theme_switcher() -> flask.Response:
    """Switches the theme of the web app"""
    
    global current_page, current_theme, stylesheet
    
    if current_theme == 'light':
        current_theme = 'dark'
        stylesheet = 'static/dark-styles.css'
    else:
        current_theme = 'light'
        stylesheet = 'static/light-styles.css'
    return render_template(current_page, stylesheet=stylesheet)

@app.route('/search')
def search() -> flask.Response:
    pass

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
    
    
    