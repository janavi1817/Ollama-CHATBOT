# AI Coding Agent Instructions for Text Generation Project

## Project Overview
This is a Jupyter notebook-based text generation project that uses Hugging Face Transformers to generate text using the Google OLLaMA model. The project demonstrates loading pre-trained models, preprocessing input text, and generating responses via beam search.

## Core Architecture & Components

### Text Generation Pipeline
- **Model Loading** (`google/ollama`): Uses `transformers.AutoModelForCausalLM` for loading the model and `AutoTokenizer` for tokenization
- **Preprocessing**: Input prompts are tokenized with `max_length=1024`, truncation, and padding to `"max_length"`
- **Generation**: Uses beam search (`num_beams=4`) with `no_repeat_ngram_size=2` to prevent repetitive outputs
- **Decoding**: Outputs are decoded with `skip_special_tokens=True` to remove tokenizer artifacts

### Key Dependencies
- `transformers`: Model and tokenizer loading/inference
- `huggingface_ollama`: Custom wrapper for OLLaMA model (imported as external module)
- `PIL`: Image handling (imported but currently unused)

## Development Workflow

### Running Experiments
The notebook structure follows this pattern:
1. Load model and tokenizer at initialization
2. Define `generate_text()` function with fixed preprocessing parameters
3. Test with example prompts using both direct function calls and the `huggingface_ollama` wrapper
4. Print outputs for manual inspection

### When Modifying Generation Logic
- **Beam search tuning**: Adjust `num_beams` (higher = more thorough but slower)
- **Repetition control**: Modify `no_repeat_ngram_size` parameter
- **Token limit**: Change `max_length` in tokenizer call (max 1024 for this model)
- **Output cleaning**: Toggle `skip_special_tokens` based on needs

## Project Patterns & Conventions

### Notebook Structure
- Single code cell with full pipeline (model loading → function definition → testing)
- Direct imports at cell start; no modularization
- Test cases embedded with print statements for immediate feedback

### Common Issues
- **Model loading**: Ensure transformers library matches model API (currently uses CausalLM for text generation)
- **VRAM requirements**: OLLaMA models may require significant GPU memory; plan accordingly for inference
- **Custom wrapper**: `huggingface_ollama.OllamaTextGenerator()` is external; verify installation before running

## Integration Points
- **huggingface_ollama module**: External dependency providing abstracted OLLaMA interface; used alongside direct transformers API
- **Prompt-response cycle**: Both direct function calls and wrapper class are tested to compare outputs

## When Adding Features
- Keep preprocessing parameters consistent across functions
- Document changes to `num_beams` or beam search settings in comments
- Validate against both pipelines (direct + wrapper) for consistency
- Consider memory implications when increasing `max_length` or batch operations
