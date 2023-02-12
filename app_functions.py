from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

def reply_generator(message: str) -> str:
    """Uses Blenderbot to generate a reply to the inputted message"""
    name = 'facebook/blenderbot-400M-distill'

    tokenizer = BlenderbotTokenizer.from_pretrained(name)
    input_ids = tokenizer.encode(
        [message],
        add_special_tokens=True,
        is_split_into_words=False,
        return_tensors='pt',
    )

    model = BlenderbotForConditionalGeneration.from_pretrained(name)
    reply_ids = model.generate(input_ids)

    return tokenizer.decode(reply_ids)



messages = [
    "How far is it to the moon?", 
    "I don't have any pets, should I get one?", 
    "What kind of books do you like reading?", 
    "I have a small Pitbull called Max", 
    "What is the weather like outside?"
]

for message in messages:
    print(reply_generator(message))