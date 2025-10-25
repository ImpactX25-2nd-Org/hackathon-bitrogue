# test_indictrans.py

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor  # <-- FIXED THIS LINE
from huggingface_hub import login
login(token="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")  # Replace with your actual token



def translate(sentences, src_lang, tgt_lang, model, tokenizer, processor, device):
    """Translate sentences using IndicTrans2"""
    
    # Preprocess
    batch = processor.preprocess_batch(sentences, src_lang=src_lang, tgt_lang=tgt_lang)
    
    # Tokenize
    inputs = tokenizer(
        batch,
        truncation=True,
        padding="longest",
        max_length=256,
        return_tensors="pt",
        return_attention_mask=True
    ).to(device)
    
    # Generate translation - FIXED PARAMETERS
    with torch.inference_mode():
        generated_tokens = model.generate(
            **inputs,
            use_cache=False,  # <-- CHANGED: False instead of True
            min_length=0,
            max_length=256,
            num_beams=1,  # <-- CHANGED: Use greedy search instead of beam
            num_return_sequences=1
        )
    
    # Decode
    outputs = tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )
    
    # Postprocess
    translations = processor.postprocess_batch(outputs, lang=tgt_lang)
    return translations


if __name__ == "__main__":
    print("Loading model...")
    
    # Setup
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {DEVICE}\n")
    
    # Load English to Indic model (smaller 200M version for faster testing)
    model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
    ).to(DEVICE)
    
    processor = IndicProcessor(inference=True)
    
    print("Model loaded successfully!\n")
    print("="*60)
    
    # Test 1: English to Kannada
    print("\n[Test 1: English → Kannada]")
    en_sentences = [
        "Hello, how are you?",
        "What is your name?",
        "Good morning, have a nice day!"
    ]
    
    kan_translations = translate(
        en_sentences, 
        "eng_Latn", 
        "kan_Knda", 
        model, 
        tokenizer, 
        processor, 
        DEVICE
    )
    
    for eng, kan in zip(en_sentences, kan_translations):
        print(f"English: {eng}")
        print(f"Kannada: {kan}\n")
    
    print("="*60)
    
    # Test 2: English to Tamil
    print("\n[Test 2: English → Tamil]")
    tam_translations = translate(
        en_sentences, 
        "eng_Latn", 
        "tam_Taml", 
        model, 
        tokenizer, 
        processor, 
        DEVICE
    )
    
    for eng, tam in zip(en_sentences, tam_translations):
        print(f"English: {eng}")
        print(f"Tamil  : {tam}\n")
    
    print("="*60)
    print("\n✓ All tests completed successfully!")
    print("\nNote: For reverse translation (Kannada/Tamil → English),")
    print("use model: 'ai4bharat/indictrans2-indic-en-dist-200M'")
