import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def generate_text_local(prompt: str, model_id: str = "gpt2", max_length: int = 100) -> str:
    """
    Generates text using a local LLM via Hugging Face Transformers.

    Args:
        prompt (str): The input text to generate from.
        model_id (str): The Hugging Face model ID (e.g., "gpt2", "meta-llama/Llama-2-7b-chat-hf").
                        Defaults to "gpt2" for a small, quick download.
        max_length (int): Maximum length of the generated sequence.

    Returns:
        str: The generated text.

    Usage Example:
        >>> from mindquest.llm_local import generate_text_local
        >>> text = generate_text_local("Once upon a time", model_id="gpt2")
        >>> print(text)
    """
    
    # Determine the best available device
    if torch.backends.mps.is_available():
        device = "mps" 
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print(f"Loading model '{model_id}' on {device}...")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # Ensure pad_token is set (common issue with GPT-style models)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(model_id)
        model.to(device)

        # Create the pipeline
        # Note: We pass the model and tokenizer directly. 
        # Device handling in pipeline varies, but passing the model on the correct device works well.
        generator = pipeline(
            "text-generation", 
            model=model, 
            tokenizer=tokenizer,
            # device=0 if device == "cuda" else -1 # We manage device via model.to()
        )
        
        output = generator(
            prompt, 
            max_length=max_length, 
            num_return_sequences=1, 
            truncation=True,
            pad_token_id=tokenizer.pad_token_id
        )
        
        return output[0]['generated_text']

    except Exception as e:
        return f"Error generating text locally: {e}"

if __name__ == "__main__":
    # Simple test when running the module directly
    print(generate_text_local("The future of AI is"))
