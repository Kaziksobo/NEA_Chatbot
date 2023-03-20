import flask
from flask import Flask, render_template, request
from os import remove
from app_functions import (
    reply_generator, 
    log, log_reader, 
    message_id_generator, 
    format_message, 
    message_selector, 
    create_log_file, 
    log_report, 
    get_messages_list,
    record_message,
    asr_transcribe
)

current_theme = 'light'
current_page = 'index.html'
stylesheet = 'static/light-styles.css'
chat_history = []
messages_to_display = []
query_message = ''
reported_message = ''

app = Flask(__name__)

@app.route('/')
def main() -> flask.Response:
    """Displays the home page 'index.html' and clears temp logs"""
    
    global stylesheet, current_page
    
    remove('log.csv')
    create_log_file('log.csv')
    
    current_page = 'index.html'
    return render_template('index.html', stylesheet=stylesheet, messages_list=get_messages_list())

@app.route('/home', methods=['GET', 'POST'])
def home() -> flask.Response:
    """Displayes the home page 'index.html' and clears temp logs"""
    
    global stylesheet, current_page
    
    remove('log.csv')
    create_log_file('log.csv')
    
    current_page = 'index.html'
    return render_template('index.html', stylesheet=stylesheet, messages_list=get_messages_list())

@app.route('/message', methods=['GET', 'POST'])
def message() -> flask.Response:
    """Requests the user's message, processes it and renders the messages page with the user's message and AI's reply"""
    
    global stylesheet, current_page, chat_history
    
    if request.form.to_dict()['message-input'] == '':
        record_message()
        user_message = asr_transcribe()
    else:
        user_message = request.form['message-input']
        user_message = format_message(user_message)
    
    reply, time = reply_generator(user_message)
    log(
        user_message=user_message,
        bot_response=reply,
        time_taken=time
    )

    chat_history = log_reader('log.csv', format=True, len_limit=True)
    chat_history = message_id_generator(chat_history)

    current_page = 'message.html'
    return render_template('message.html', stylesheet=stylesheet, messages=chat_history, messages_list=get_messages_list())

@app.route('/theme', methods=['GET', 'POST'])
def theme_switcher() -> flask.Response:
    """Switches the theme of the web app"""
    
    global current_page, current_theme, stylesheet, chat_history, query_message, reported_message
    
    if current_theme == 'light':
        current_theme = 'dark'
        stylesheet = 'static/dark-styles.css'
    else:
        current_theme = 'light'
        stylesheet = 'static/light-styles.css'
    
    if current_page == 'message.html': 
        return render_template(current_page, stylesheet=stylesheet, messages=chat_history, messages_list=get_messages_list())
    elif current_page == 'search_result.html':
        return render_template(current_page, stylesheet=stylesheet, messages=messages_to_display, messages_list=get_messages_list())
    elif current_page == 'search_error.html':
        return render_template(current_page, stylesheet=stylesheet, message=query_message, messages_list=get_messages_list())
    elif current_page == 'report.html':
        return render_template(current_page, stylesheet=stylesheet, message=reported_message, messages_list=get_messages_list())
    else:
        return render_template(current_page, stylesheet=stylesheet, messages_list=get_messages_list())

@app.route('/search', methods=['GET', 'POST'])
def search() -> flask.Response:
    """Renders searched message plus number of surrounding messages"""
    
    global messages_to_display, current_page, stylesheet, query_message
    
    query_message = request.form['search-bar']
    
    print(f'Search query - {query_message}')

    location = False

    history = log_reader('ext_log.csv', format=True)
    
    history.reverse()
    
    for message_info in history:
        if message_info['text'] == query_message:
            print(f'Found message - {message_info}')
            location = history.index(message_info)
    
    if not location:
        current_page = 'search_error.html'
        return render_template(current_page, stylesheet=stylesheet, message=query_message)
    
    messages_before, messages_after = message_selector(len(history), location)
    
    messages_to_display = [history[i] for i in range((location + (messages_after)), (location - (messages_before + 1)), -1)]
    messages_to_display = message_id_generator(messages_to_display)
    
    for message in messages_to_display:
        if message['text'] == query_message:
            message['class'] = 'query-message-box'
        else:
            message['class'] = False
    
    current_page = 'search_result.html'
    return render_template(current_page, stylesheet=stylesheet, messages=messages_to_display, messages_list=get_messages_list())

@app.route('/back', methods=['GET', 'POST'])
def back() -> flask.Response:
    """Renders the message page when back button on search results page clicked"""
    
    global chat_history, current_page, stylesheet
    
    current_page = 'message.html'
    return render_template(current_page, stylesheet=stylesheet, messages=chat_history, messages_list=get_messages_list())

@app.route('/report', methods=['GET', 'POST'])
def report() -> flask.Response:
    """Logs the report and renders report page"""
    
    global stylesheet, chat_history, current_page, reported_message
    
    reported_message = list(request.form.to_dict().keys())[0]
    report_reason = request.form[reported_message]
    report_message = reported_message.replace('report-', '')
    
    for message in chat_history:
        if message['id'] == report_message:
            location = chat_history.index(message)
            bot_response = message['text']
    user_message = chat_history[location - 1]['text']
    
    log_report(user_message, bot_response, report_reason)
    
    current_page = 'report.html'
    return render_template(current_page, stylesheet=stylesheet, message=bot_response, messages_list=get_messages_list())

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')