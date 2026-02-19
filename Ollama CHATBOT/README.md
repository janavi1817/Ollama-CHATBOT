# Ollama Web Chatbot (Purple Theme)

## How to Run

1. **Start Ollama backend**
   - Make sure Ollama is running on your machine: http://localhost:11434
   - If not, download and install from https://ollama.ai/
   - Start your model with e.g. `ollama serve` and `ollama pull llama3.2:latest`

2. **Start the Web Chatbot**
   - In your terminal, run:
     ```
     python ollama_web_chatbot.py
     ```
   - You should see output like:
     ```
     * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
     ```

3. **Open the Chatbot in your browser**
   - Go to: [http://localhost:5000](http://localhost:5000)

## Troubleshooting
- If you can't access the link, check your terminal for errors.
- Try both http://localhost:5000 and http://127.0.0.1:5000
- Make sure no firewall or antivirus is blocking Python or port 5000.
- The backend API (not for direct chat) is at: http://localhost:11434

## Files
- `ollama_web_chatbot.py`: Flask app (frontend + backend, purple theme)

---

**Chatbot Link:**

👉 [http://localhost:5000](http://localhost:5000)
