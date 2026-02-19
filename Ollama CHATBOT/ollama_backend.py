import requests
import base64
import pyttsx3

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"  # Default model, will auto-detect available models

class OllamaBackend:
    def __init__(self):
        self.voice_engine = pyttsx3.init()
        self.voice_engine.setProperty('rate', 180)
        self.available_model = self.check_available_models()

    def check_available_models(self):
        """Check which models are available in Ollama"""
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if r.status_code == 200:
                models = r.json().get('models', [])
                if models:
                    # Prefer text models over multimodal for basic chat
                    model_names = [m['name'] for m in models]
                    
                    # Priority order of models to use
                    preferred_models = ['llama3.2', 'llama3.1', 'llama3', 'llama2', 'mistral', 'phi', 'gemma']
                    
                    for preferred in preferred_models:
                        for model_name in model_names:
                            if preferred in model_name.lower():
                                print(f"Using model: {model_name}")
                                return model_name
                    
                    # If no preferred model found, use the first available
                    print(f"Using model: {model_names[0]}")
                    return model_names[0]
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error checking models: {e}")
            return None

    def check_ollama_connection(self):
        """Check if Ollama is running"""
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            return r.status_code == 200
        except:
            return False

    def get_text_response(self, prompt):
        # Check if Ollama is running
        if not self.check_ollama_connection():
            return "⚠️ Ollama is not running. Please start Ollama by running 'ollama serve' in your terminal."
        
        # Check if a model is available
        if not self.available_model:
            return "⚠️ No models found. Please pull a model first:\n\nRun in terminal:\nollama pull llama3.2\n\nOr try:\nollama pull llama2"
        
        try:
            payload = {
                "model": self.available_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 512,  # Limit response length for faster replies
                }
            }
            r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
            
            if r.status_code == 200:
                result = r.json()
                response = result.get('response', '').strip()
                if not response:
                    response = "I received your message but couldn't generate a response. Please try again."
                return response
            elif r.status_code == 404:
                # Model not found, refresh available models
                self.available_model = self.check_available_models()
                if not self.available_model:
                    return f"⚠️ Model not found. Please pull a model:\n\nollama pull llama3.2"
                return f"⚠️ Model '{self.available_model}' not found. Refreshed model list. Please try again."
            else:
                error_msg = r.json().get('error', 'Unknown error')
                return f"⚠️ Ollama error ({r.status_code}): {error_msg}\n\nTry pulling a model:\nollama pull llama3.2"
                
        except requests.exceptions.Timeout:
            return "⚠️ Request timed out. The model might be loading. Please try again in a moment."
        except requests.exceptions.ConnectionError:
            return "⚠️ Cannot connect to Ollama. Make sure it's running:\n\nRun: ollama serve"
        except Exception as e:
            return f"⚠️ Error: {str(e)}\n\nMake sure Ollama is running and a model is installed."

    def get_image_response(self, image_path, question):
        # Check if Ollama is running
        if not self.check_ollama_connection():
            return "⚠️ Ollama is not running. Please start Ollama by running 'ollama serve' in your terminal."
        
        # For image analysis, we need a multimodal model
        multimodal_models = ['llava', 'bakllava', 'llava-phi3', 'llava-llama3']
        image_model = None
        
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if r.status_code == 200:
                models = r.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                for mm in multimodal_models:
                    for model_name in model_names:
                        if mm in model_name.lower():
                            image_model = model_name
                            break
                    if image_model:
                        break
        except:
            pass
        
        if not image_model:
            return "⚠️ No multimodal model found for image analysis.\n\nPlease install one:\nollama pull llava"
        
        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            
            payload = {
                "model": image_model,
                "prompt": question,
                "images": [img_b64],
                "stream": False
            }
            r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=180)
            
            if r.status_code == 200:
                result = r.json()
                response = result.get('response', '').strip()
                if not response:
                    response = "I analyzed the image but couldn't generate a response. Please try again."
                return response
            else:
                error_msg = r.json().get('error', 'Unknown error')
                return f"⚠️ Image analysis error: {error_msg}"
                
        except Exception as e:
            return f"⚠️ Error analyzing image: {str(e)}"

    def speak(self, message):
        try:
            # Don't speak error messages
            if not message.startswith("⚠️"):
                self.voice_engine.say(message)
                self.voice_engine.runAndWait()
        except:
            pass  # Silently fail if voice engine has issues
