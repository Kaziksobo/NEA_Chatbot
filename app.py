import flask
from flask import Flask, render_template, request
from app_functions import reply_generator, log, log_reader, message_id_generator

current_theme = 'light'
current_page = 'index.html'
stylesheet = 'static/light-styles.css'
formatted_chat_history = []
messages_to_display = []

app = Flask(__name__)

@app.route('/')
def main() -> flask.Response:
    """Displays the home page 'index.html'"""
    
    global stylesheet
    return render_template('index.html', stylesheet=stylesheet)

@app.route('/message', methods=['GET', 'POST'])
def message() -> flask.Response:
    """Requests the user's message, processes it and renders the messages page with the user's message and AI's reply"""
    
    global stylesheet, current_page, formatted_chat_history
    
    user_message = request.form['message-input']
    reply, time = reply_generator(user_message)
    log(
        user_message=user_message,
        bot_response=reply,
        time_taken=time
    )
    
    chat_history = log_reader('log.csv', format=True, len_limit=True)
    chat_history = message_id_generator(chat_history)
    
    current_page = 'message.html'
    return render_template('message.html', stylesheet=stylesheet, messages=chat_history)

@app.route('/theme', methods=['GET', 'POST'])
def theme_switcher() -> flask.Response:
    """Switches the theme of the web app"""
    
    global current_page, current_theme, stylesheet, formatted_chat_history
    
    if current_theme == 'light':
        current_theme = 'dark'
        stylesheet = 'static/dark-styles.css'
    else:
        current_theme = 'light'
        stylesheet = 'static/light-styles.css'
    if current_page == 'message.html': 
        return render_template(current_page, stylesheet=stylesheet, messages=formatted_chat_history)
    elif current_page == 'search_result.html':
        return render_template(current_page, stylesheet=stylesheet, messages_to_display=messages_to_display)
    else:
        return render_template(current_page, stylesheet=stylesheet)

@app.route('/search', methods=['GET', 'POST'])
def search() -> flask.Response:
    """Renders searched message plus number of surrounding messages"""
    
    global messages_to_display
    
    query = request.form['search-bar']

    history = log_reader('ext_log.csv', format=True)
    for message_info in history:
        if message_info['text'] == query:
            location = history.index(message_info)
    
    messages_to_display = [history[i] for i in range((location - 4), (location + 5))]
    messages_to_display = message_id_generator(messages_to_display)
    
    current_page = 'search_result.html'
    return render_template('search_result.html', stylesheet=stylesheet, messages=messages_to_display)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')