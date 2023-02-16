from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

def reply_generator(message: str) -> str:
    """Uses Blenderbot to generate a reply to the inputted message"""
    name = 'facebook/blenderbot-400M-distill'

    print(f'Input sequence: {message}')

    tokenizer = BlenderbotTokenizer.from_pretrained(name)
    
    input_ids = tokenizer.encode(
        message,
        add_special_tokens=True,
        is_split_into_words=False,
        return_tensors='pt',
    )
    
    print(f'Input Ids: {input_ids}')

    model = BlenderbotForConditionalGeneration.from_pretrained(name)
    reply_ids = model.generate(
        input_ids,
        num_beams=35,
        )
    
    print(f'Reply Ids: {reply_ids}')

    return tokenizer.decode(reply_ids[0], skip_special_tokens=True)