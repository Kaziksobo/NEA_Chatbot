from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from csv import writer, reader
from os import stat, path
import torch

def log_reader() -> list:
    """Reads the contents of the log file into a single list, ignoring the time taken column"""
    # Checks if the chat history is empty
    if not path.exists('log.csv'):
        return None
    with open('log.csv', 'r') as log_file:
        csv_reader = reader(log_file)
        chat_history = []
        for row in csv_reader:
            # Ignores header row
            if 'User message' in row:
                continue
            # Appends the first two entries in the row to the chat_history list
            chat_history.extend((row[0], row[1]))
    return chat_history


def reply_generator(message: str) -> str:
    """Uses Blenderbot to generate a reply to the inputted message"""
    name = 'facebook/blenderbot-400M-distill'

    print(f'Input sequence: {message}')

    # Declares tokenizer
    tokenizer = BlenderbotTokenizer.from_pretrained(name)

    # Tokenizes input
    input_ids = tokenizer.encode(
        message,
        add_special_tokens=True,
        is_split_into_words=False,
        return_tensors='pt',
    )

    print(f'Input Ids: {input_ids}')

    if chat_history := log_reader():
        # Tokenizing chat history
        chat_history_ids = tokenizer.encode(
            chat_history,
            add_special_tokens=True,
            is_split_into_words=False,
            return_tensors='pt'
        )

        bot_input_ids = torch.cat([chat_history_ids, input_ids], dim=-1)

        reply_ids = model_generation(name, bot_input_ids)
        # Decodes reply ids
        return tokenizer.decode(reply_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

    else:
        reply_ids = model_generation(name, input_ids)
        return tokenizer.decode(reply_ids[0], skip_special_tokens=True)

def model_generation(name: str, input_ids: torch.Tensor) -> torch.Tensor:
    """Generates response sequence using an already tokenized input"""
    # Declares model
    model = BlenderbotForConditionalGeneration.from_pretrained(name)
    
    # Generates Reply ids
    result = model.generate(
        input_ids, 
        num_beams=35, 
        max_length=60
    )
    print(f'Reply Ids: {result}')
    return result

print(reply_generator("Do you know how to make them"))


def log(user_message: str, bot_response: str, time_taken: float) -> None:
    """Logs the user's message, the bot response and the computation time to a CSV file"""
    file_address = 'log.csv'
    with open(file_address, 'a', encoding='utf-8', newline='') as file_object:
        csv_writer = writer(file_object)
        # Checks if file did not already exist, and adds header if it did not
        if stat(file_address).st_size == 0:
            csv_writer.writerow(['User message', 'Bot response', 'Time taken'])
        csv_writer.writerow([user_message, bot_response, time_taken])