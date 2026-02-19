# Ollama Chatbot with RAG

A modern desktop chatbot application built with Python and CustomTkinter, featuring Retrieval-Augmented Generation (RAG) capabilities powered by Ollama.

## Features

### 🤖 AI-Powered Chat
- Powered by Ollama (supports llama3.2, llama2, mistral, and more)
- Natural language conversations
- Voice input support with speech recognition
- Text-to-speech responses

### 📚 RAG (Retrieval-Augmented Generation)
- Upload documents to knowledge base
- Automatic relevance detection
- Smart context retrieval
- Combines knowledge base with general AI knowledge
- View and manage uploaded documents

### 💬 Chat Management
- Multiple chat sessions
- Edit and delete messages
- Copy messages to clipboard
- Chat history with timestamps
- Session management (create, edit, delete)

### 🎨 Modern UI
- Dark and light theme support
- Clean, intuitive interface
- User and bot message bubbles with icons
- Interactive message actions
- Real-time status indicators

## Prerequisites

- Python 3.10 or higher
- Ollama installed and running ([Download Ollama](https://ollama.ai/))
- A pulled Ollama model (e.g., `ollama pull llama3.2`)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd "CHAT VS"
```

2. Install required packages:
```bash
pip install customtkinter pillow speechrecognition pyttsx3 requests pyaudio
```

3. Start Ollama:
```bash
ollama serve
```

4. Pull a model (if not already done):
```bash
ollama pull llama3.2
```

## Usage

Run the chatbot:
```bash
python "Ollama CHATBOT/ollama_desktop_chatbot.py"
```

### Using RAG Features

1. **Upload Documents:**
   - Click the 📄 "Upload Document" button
   - Paste your document text
   - Click "Add to Knowledge Base"

2. **Ask Questions:**
   - Type your question in the input field
   - The bot automatically checks the knowledge base
   - If relevant info is found, it shows "📚 Found relevant information..."
   - Otherwise, it uses general knowledge

3. **View Knowledge Base:**
   - Click the 📚 button to view all documents
   - Read full documents
   - Delete documents you no longer need

### Chat Features

- **Voice Input:** Click 🎤 to speak your message
- **Edit Messages:** Click on your message bubble, then click ✏️
- **Copy Messages:** Click on any message bubble, then click 📋
- **Theme Toggle:** Click 🌙/☀️ to switch between dark and light mode
- **Clear Chat:** Click 🗑️ to clear the current conversation

## Project Structure

```
CHAT VS/
├── Ollama CHATBOT/
│   ├── ollama_desktop_chatbot.py  # Main application
│   ├── ollama_backend.py          # Ollama API integration
│   └── README.md                  # Original README
├── .github/
│   └── copilot-instructions.md
└── README.md                      # This file
```

## Configuration

The chatbot automatically detects available Ollama models. You can modify the model preferences in `ollama_backend.py`:

```python
preferred_models = ['llama3.2', 'llama3.1', 'llama3', 'llama2', 'mistral', 'phi', 'gemma']
```

## RAG System

The RAG system uses intelligent keyword matching and relevance scoring:

- Extracts meaningful keywords from queries (3+ characters)
- Filters out common stop words
- Matches keywords and phrases in documents
- Scores documents by relevance
- Uses top 2 most relevant documents
- Falls back to general knowledge when no relevant docs found

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if a model is installed: `ollama list`
- Pull a model if needed: `ollama pull llama3.2`

### Voice Input Not Working
- Check microphone permissions
- Install PyAudio: `pip install pyaudio`
- On Windows, you may need to install it from a wheel file

### Application Won't Start
- Verify all dependencies are installed
- Check Python version (3.10+)
- Look for error messages in the terminal

## Technologies Used

- **Python 3.10+**
- **CustomTkinter** - Modern UI framework
- **Ollama** - Local LLM inference
- **SpeechRecognition** - Voice input
- **pyttsx3** - Text-to-speech
- **Pillow** - Image handling
- **Requests** - API communication

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Ollama team for the amazing local LLM platform
- CustomTkinter for the modern UI framework
- All contributors and users of this project

## Author

Created with ❤️ by Janavi Patel

---

**Note:** This chatbot runs entirely locally using Ollama. No data is sent to external servers.
