from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from csv import writer, reader
from os import path, remove
from time import time
from datetime import datetime
from typing import Union
import torch, re, nltk.data
import sounddevice as sd
import soundfile as sf
import numpy as np

def log_reader(file_address: str, format: bool=False, len_limit: bool=False) -> list:
    """Reads the contents of the log file into a single list, ignoring the time taken and log time columns.\n
    Also has the option of formatting the chat history, turning each message into a dictionary,
    specifying if the message came from the model or the user"""
    
    # Checks if the chat history is empty
    if not path.exists(file_address):
        print('No log file found')
        return None

    print('Log file found')
    with open(file_address, 'r') as log_file:
        csv_reader = reader(log_file)
        chat_history = []
        for row in csv_reader:
            # Ignores header row
            if 'User message' in row:
                continue
            # Appends the first two entries in the row to the chat_history list
            chat_history.extend((row[0], row[1]))
    
    chat_history.reverse()
    
    if format:
        formatted_chat_history = []
        if len_limit:
            for i in range(min(9, len(chat_history))):
                if i % 2 == 0:
                    formatted_chat_history.append({'type': 'ai', 'text': chat_history[i]})
                else:
                    formatted_chat_history.append({'type': 'user', 'text': chat_history[i]})
        else:
            for i in range(len(chat_history)):
                if i % 2 == 0:
                    formatted_chat_history.append({'type': 'ai', 'text': chat_history[i]})
                else:
                    formatted_chat_history.append({'type': 'user', 'text': chat_history[i]})

        return formatted_chat_history
    
    return chat_history

def message_id_generator(chat_history: list) -> list:
    """Adds IDs to each message based on their location in the list"""
    
    for i in range(len(chat_history)):
        chat_history[i]['id'] = f'message-{i + 1}'
    
    return chat_history

def reply_generator(message: str) -> Union[str, float]:
    # sourcery skip: extract-duplicate-method
    """Uses Blenderbot to generate a reply to the inputted message"""
    
    start = time()
    name = 'facebook/blenderbot-400M-distill'

    print(f'Input sequence: {message}')

    # Declares tokenizer
    tokenizer = BlenderbotTokenizer.from_pretrained(name, cache_dir='data/tokenizers')

    print('Tokenizing input')

    # Tokenizes input
    input_ids = tokenizer.encode(
        message,
        add_special_tokens=True,
        is_split_into_words=False,
        return_tensors='pt',
    )

    print(f'Input Ids: {input_ids}')
    
    reply_ids = model_generation(name, input_ids)
    reply = tokenizer.decode(reply_ids[0], skip_special_tokens=True)

    print(f'Response: {reply}')
    end = time()
    
    return format_message(reply), round((end - start), 2)

def model_generation(name: str, input_ids: torch.Tensor) -> torch.Tensor:
    """Generates response sequence using an already tokenized input"""
    
    # Declares model
    model = BlenderbotForConditionalGeneration.from_pretrained(name, cache_dir='data/models')
    
    print('Generating reply ids')
    # Generates Reply ids
    result = model.generate(
        input_ids, 
        # num_beams=35, 
        # max_length=60
    )
    print(f'Reply Ids: {result}')
    
    return result

def format_message(message: str) -> str:
    """Formats message to capitalise and remove whitespace and fix some grammar errors"""
    
    message = re.sub(r'\s(?=[\.,:;])', "", message)
    message = message.strip()
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_tokenizer.tokenize(message)
    sentences = [sent.capitalize() for sent in sentences]
    message = ' '.join(sentences)
    return message

def log(user_message: str, bot_response: str, time_taken: float) -> None:
    # sourcery skip: extract-method
    """Logs the user's message, the bot response and the computation time to a CSV file"""
    
    # Checking if either log files do not exist
    file_address = 'log.csv'
    extended_file_address = 'ext_log.csv'
    for file in [file_address, extended_file_address]:
        if not path.exists(file):
            create_log_file(file)

    # Checking if the main log file is full
    with open(file_address, 'r', encoding='utf-8', newline='') as file_object:
        limit_reached = sum(1 for _ in file_object) == 11
    if limit_reached:
        print('Log file limit reached')

        # Reading in all rows from original file
        rows = []
        with open(file_address, 'r', encoding='utf-8', newline='') as log_file:
            csv_reader = reader(log_file)
            rows.extend(iter(csv_reader))
            
        # Removing oldest message row and header row
        rows.pop(0)
        rows.pop(0)
        remove(file_address)
        create_log_file(file_address)

        # Writing older rows to new log file
        with open(file_address, 'a', encoding='utf-8', newline='') as file_object:
            csv_writer = writer(file_object)
            for row in rows:
                csv_writer.writerow(row)

    # Logging new data to both log files
    print('Logging data')
    log_time = str(datetime.now())
    log_file_writer(user_message, bot_response, time_taken, file_address, log_time)
    log_file_writer(user_message, bot_response, time_taken, extended_file_address, log_time)
        
def log_file_writer(user_message: str, bot_response: str, time_taken: str, file_address: str, log_time:str) -> None:
    """Logs data to any log file"""
    
    with open(file_address, 'a', encoding='utf-8', newline='') as file_object:
        csv_writer = writer(file_object)
        csv_writer.writerow([user_message, bot_response, time_taken, log_time])

def create_log_file(file_address: str) -> None:
    """Creates the log file, adding in the header row"""
    
    print('Creating new log file')
    with open(file_address, 'w', encoding='utf-8', newline='') as file_object:
        csv_writer = writer(file_object)
        csv_writer.writerow(['User message', 'Bot response', 'Time taken', 'Log time'])

def log_report(user_message: str, bot_response: str, report_reason: str):
    """Saves reported response, user's message and report reason to a CSV file"""
    
    if not path.exists('report.csv'):
        create_report_file()
    
    with open('report.csv', 'a', encoding='utf-8', newline='') as file_object:
        csv_writer = writer(file_object)
        csv_writer.writerow([user_message, bot_response, report_reason])

def create_report_file() -> None:
    """Creates report file, adding in the header row"""
    
    print('Creating report file')
    with open('report.csv', 'w', encoding='utf-8', newline='') as file_object:
        csv_writer = writer(file_object)
        csv_writer.writerow(['User message', 'Bot response', 'Report reason'])

def message_selector(length: int, location: int) -> int:
    """selects the messages to be displayed when a message is searched for, 
    based off the length of the chat history"""
    
    messages_before = 0
    messages_after = 0
    messages_after_query = length - (location + 1)
    messages_before_query = length - (messages_after_query + 1)
    if messages_after_query > 3 and messages_before_query > 3:
        messages_after = 4
        messages_before = 4
    elif messages_after_query < 4 and messages_before_query > 3:
        messages_after = messages_after_query
        messages_before = 8 - messages_after
    elif messages_after_query > 3 and messages_before_query < 4:
        messages_before = messages_before_query
        messages_after = 8 - messages_before
    
    return messages_before, messages_after

def get_messages_list() -> list:
    """Returns a list of individual messages"""
    
    history = log_reader('ext_log.csv', format=True)
    history.reverse()

    return [message['text'] for message in history]
