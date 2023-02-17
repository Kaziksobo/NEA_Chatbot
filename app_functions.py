from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from csv import writer
from os import stat

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

    # Declares model
    model = BlenderbotForConditionalGeneration.from_pretrained(name)
    
    # Generates Reply ids
    reply_ids = model.generate(
        input_ids,
        num_beams=35,
        )
    
    print(f'Reply Ids: {reply_ids}')

    # Decodes reply ids
    return tokenizer.decode(reply_ids[0], skip_special_tokens=True)

def log(user_message: str, bot_response: str, time_taken: float) -> None:
    """Logs the user's message, the bot response and the computation time to a CSV file"""
    file_address = 'log.csv'
    with open(file_address, 'a', encoding='utf-8', newline='') as file_object:
        csv_writer = writer(file_object)
        # Checks if file did not already exist, and adds header if it did not
        if stat(file_address).st_size == 0:
            csv_writer.writerow(['User message', 'Bot response', 'Time taken'])
        csv_writer.writerow([user_message, bot_response, time_taken])

log('this is a second test message', 'This is second a test reply', 25)