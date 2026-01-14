from mindquest import llm_local

def test_generate_text_local_integration():
    """
    Integration test for generate_text_local using a tiny model.
    This performs a real download and inference.
    """
    prompt = "Hi"
    # use a tiny model for speed
    model_id = "sshleifer/tiny-gpt2" 
    
    result = llm_local.generate_text_local(prompt, model_id=model_id, max_length=10)
    
    assert isinstance(result, str)
    assert len(result) > 0
    # Since it's a tiny random model, we just check that it produces output
    # without crashing.