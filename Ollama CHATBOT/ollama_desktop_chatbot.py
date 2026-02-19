import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import speech_recognition as sr
from PIL import Image, ImageTk
from datetime import datetime
from ollama_backend import OllamaBackend

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OllamaDesktopChatbot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ollama Chatbot")
        self.geometry("1200x750")
        self.resizable(False, False)
        
        # Dark theme colors
        self.bg_dark = "#1a1d2e"
        self.sidebar_bg = "#16213e"
        self.chat_bg = "#0f1419"
        self.user_bubble = "#7c3aed"
        self.bot_bubble = "#2d3748"
        self.accent_purple = "#8b5cf6"
        self.text_light = "#e2e8f0"
        
        self.configure(fg_color=self.bg_dark)
        self.uploaded_image = None
        self.backend = OllamaBackend()
        self.chat_history = []
        self.chat_sessions = []
        self.current_session = None
        self.knowledge_base = []  # Store RAG documents
        self.theme_mode = "dark"
        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_container = ctk.CTkFrame(self, fg_color=self.bg_dark)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left sidebar - Chat History
        self.sidebar = ctk.CTkFrame(main_container, width=280, fg_color=self.sidebar_bg, corner_radius=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Sidebar header
        sidebar_header = ctk.CTkFrame(self.sidebar, fg_color=self.sidebar_bg, height=60)
        sidebar_header.pack(fill=tk.X, padx=15, pady=(20, 10))
        
        history_label = ctk.CTkLabel(
            sidebar_header, 
            text="📋 Chat History",
            font=("Segoe UI", 18, "bold"),
            text_color=self.text_light
        )
        history_label.pack(anchor="w")

        # New Chat button
        new_chat_btn = ctk.CTkButton(
            self.sidebar,
            text="New Chat",
            font=("Segoe UI", 14, "bold"),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            height=40,
            corner_radius=10,
            command=self.new_chat_session
        )
        new_chat_btn.pack(fill=tk.X, padx=15, pady=(0, 15))

        # Chat sessions scrollable frame
        self.sessions_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color=self.sidebar_bg,
            scrollbar_button_color=self.accent_purple
        )
        self.sessions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Right side - Chat area
        right_panel = ctk.CTkFrame(main_container, fg_color=self.chat_bg, corner_radius=0)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Top header bar
        header_frame = ctk.CTkFrame(right_panel, fg_color=self.bg_dark, height=70, corner_radius=0)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color=self.bg_dark)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Title with icon
        title_frame = ctk.CTkFrame(header_content, fg_color=self.bg_dark)
        title_frame.pack(side=tk.LEFT)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🤖 Ollama Chatbot",
            font=("Segoe UI", 20, "bold"),
            text_color=self.text_light
        )
        title_label.pack(side=tk.LEFT)

        # Action buttons in header
        actions_frame = ctk.CTkFrame(header_content, fg_color=self.bg_dark)
        actions_frame.pack(side=tk.RIGHT)

        # Upload Document button (RAG)
        upload_doc_btn = ctk.CTkButton(
            actions_frame,
            text="📄",
            width=45,
            height=45,
            font=("Segoe UI", 20),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            corner_radius=10,
            command=self.open_upload_document_dialog
        )
        upload_doc_btn.pack(side=tk.LEFT, padx=5)

        # View Knowledge Base button
        view_kb_btn = ctk.CTkButton(
            actions_frame,
            text="📚",
            width=45,
            height=45,
            font=("Segoe UI", 20),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            corner_radius=10,
            command=self.open_knowledge_base_dialog
        )
        view_kb_btn.pack(side=tk.LEFT, padx=5)

        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            actions_frame,
            text="🌙",
            width=45,
            height=45,
            font=("Segoe UI", 20),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            corner_radius=10,
            command=self.toggle_theme
        )
        self.theme_btn.pack(side=tk.LEFT, padx=5)

        # Clear chat button
        clear_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=45,
            height=45,
            font=("Segoe UI", 20),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            corner_radius=10,
            command=self.clear_chat
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Chat display area
        self.chat_display_frame = ctk.CTkScrollableFrame(
            right_panel,
            fg_color=self.chat_bg,
            scrollbar_button_color=self.accent_purple
        )
        self.chat_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Image preview area
        self.img_preview_frame = ctk.CTkFrame(right_panel, fg_color=self.chat_bg, height=0)
        self.img_preview_frame.pack(fill=tk.X, padx=20)
        self.img_label = ctk.CTkLabel(self.img_preview_frame, text="")
        self.img_label.pack()

        # Input area at bottom
        input_container = ctk.CTkFrame(right_panel, fg_color=self.bg_dark, height=110)
        input_container.pack(fill=tk.X, side=tk.BOTTOM)
        input_container.pack_propagate(False)

        # RAG status indicator
        self.rag_status_frame = ctk.CTkFrame(input_container, fg_color=self.bg_dark, height=20)
        self.rag_status_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        self.rag_status_label = ctk.CTkLabel(
            self.rag_status_frame,
            text="",
            font=("Segoe UI", 10),
            text_color="#10b981"
        )
        self.rag_status_label.pack(anchor="w")

        input_frame = ctk.CTkFrame(input_container, fg_color=self.bg_dark)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 15))

        # Message input
        self.prompt_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message...",
            font=("Segoe UI", 14),
            height=50,
            fg_color=self.sidebar_bg,
            border_color=self.accent_purple,
            border_width=2,
            text_color=self.text_light,
            corner_radius=25
        )
        self.prompt_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.prompt_entry.bind('<Return>', lambda e: self.send_message())

        # Voice assistant button (in text area)
        voice_btn = ctk.CTkButton(
            input_frame,
            text="🎤",
            width=50,
            height=50,
            font=("Segoe UI", 20),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            corner_radius=25,
            command=self.voice_input
        )
        voice_btn.pack(side=tk.LEFT, padx=5)

        # Send button
        send_btn = ctk.CTkButton(
            input_frame,
            text="▶",
            width=50,
            height=50,
            font=("Segoe UI", 20, "bold"),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            corner_radius=25,
            command=self.send_message
        )
        send_btn.pack(side=tk.LEFT)

        # Initialize first chat session
        self.new_chat_session()

    def new_chat_session(self):
        """Create a new chat session"""
        timestamp = datetime.now().strftime("%m/%d/%Y")
        session_name = f"New Chat"
        
        session = {
            'name': session_name,
            'date': timestamp,
            'messages': []
        }
        self.chat_sessions.append(session)
        self.current_session = session
        
        # Clear current chat display
        for widget in self.chat_display_frame.winfo_children():
            widget.destroy()
        
        self.update_sessions_sidebar()

    def update_sessions_sidebar(self):
        """Update the chat sessions in sidebar"""
        for widget in self.sessions_frame.winfo_children():
            widget.destroy()
        
        for idx, session in enumerate(reversed(self.chat_sessions)):
            is_current = session == self.current_session
            
            # Container for session button and action buttons
            session_container = ctk.CTkFrame(
                self.sessions_frame,
                fg_color=self.sidebar_bg
            )
            session_container.pack(fill=tk.X, pady=5)
            
            # Session button
            session_btn = ctk.CTkButton(
                session_container,
                text=session['name'],
                font=("Segoe UI", 13, "bold" if is_current else "normal"),
                fg_color=self.accent_purple if is_current else self.bot_bubble,
                hover_color="#6d28d9" if is_current else ("#cbd5e1" if self.theme_mode == "light" else "#374151"),
                text_color=self.text_light if not is_current else "#ffffff",
                height=60,
                corner_radius=10,
                anchor="w",
                command=lambda s=session: self.on_session_click(s)
            )
            session_btn.pack(fill=tk.X, side=tk.TOP)
            
            # Date label on session button
            date_label = ctk.CTkLabel(
                session_btn,
                text=session['date'],
                font=("Segoe UI", 10),
                text_color="#ffffff" if is_current else ("#64748b" if self.theme_mode == "light" else "#94a3b8")
            )
            date_label.place(relx=0.05, rely=0.65)
            
            # Store session reference
            session_container.session = session

    def on_session_click(self, session):
        """Handle session click - switch and show actions"""
        # Switch to the session
        self.switch_session(session)
        
        # Show action buttons for this session
        self.show_session_actions(session)

    def show_session_actions(self, session):
        """Show edit/delete actions for a session"""
        # Find the container for this session
        for container in self.sessions_frame.winfo_children():
            if hasattr(container, 'session') and container.session == session:
                # Check if actions already exist
                has_actions = False
                for widget in container.winfo_children():
                    if isinstance(widget, ctk.CTkFrame) and widget != container.winfo_children()[0]:
                        # Toggle visibility
                        if widget.winfo_viewable():
                            widget.pack_forget()
                        else:
                            widget.pack(fill=tk.X, pady=(5, 0))
                        has_actions = True
                        break
                
                if not has_actions:
                    # Create actions frame
                    actions_frame = ctk.CTkFrame(
                        container,
                        fg_color=self.sidebar_bg
                    )
                    actions_frame.pack(fill=tk.X, pady=(5, 0))
                    
                    actions_inner = ctk.CTkFrame(
                        actions_frame,
                        fg_color=self.sidebar_bg
                    )
                    actions_inner.pack(fill=tk.X, padx=5)
                    
                    # Edit button
                    edit_btn = ctk.CTkButton(
                        actions_inner,
                        text="✏️ Edit",
                        font=("Segoe UI", 12),
                        fg_color="#3b82f6",
                        hover_color="#2563eb",
                        height=35,
                        corner_radius=8,
                        command=lambda s=session: self.edit_session_name(s)
                    )
                    edit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
                    
                    # Delete button
                    delete_btn = ctk.CTkButton(
                        actions_inner,
                        text="🗑️ Delete",
                        font=("Segoe UI", 12),
                        fg_color="#dc2626",
                        hover_color="#b91c1c",
                        height=35,
                        corner_radius=8,
                        command=lambda s=session: self.delete_session(s)
                    )
                    delete_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                # Hide actions for other sessions
                for widget in container.winfo_children():
                    if isinstance(widget, ctk.CTkFrame) and widget != container.winfo_children()[0]:
                        widget.pack_forget()

    def edit_session_name(self, session):
        """Open dialog to edit session name"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Chat Name")
        dialog.geometry("450x200")
        dialog.configure(fg_color=self.bg_dark)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"450x200+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="✏️ Edit Chat Name",
            font=("Segoe UI", 20, "bold"),
            text_color=self.text_light
        )
        header.pack(pady=20)
        
        # Input field
        name_entry = ctk.CTkEntry(
            dialog,
            font=("Segoe UI", 14),
            height=45,
            fg_color=self.sidebar_bg,
            border_color=self.accent_purple,
            border_width=2,
            text_color=self.text_light,
            corner_radius=10
        )
        name_entry.pack(fill=tk.X, padx=30, pady=10)
        name_entry.insert(0, session['name'])
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color=self.bg_dark)
        button_frame.pack(fill=tk.X, padx=30, pady=10)
        
        def save_name():
            new_name = name_entry.get().strip()
            if new_name:
                session['name'] = new_name
                self.update_sessions_sidebar()
                dialog.destroy()
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            font=("Segoe UI", 13, "bold"),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            height=40,
            corner_radius=10,
            command=save_name
        )
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 13, "bold"),
            fg_color=self.bot_bubble,
            hover_color="#374151",
            height=40,
            corner_radius=10,
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind Enter key to save
        name_entry.bind('<Return>', lambda e: save_name())

    def delete_session(self, session):
        """Delete a chat session with confirmation"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Delete Chat")
        dialog.geometry("450x220")
        dialog.configure(fg_color=self.bg_dark)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (220 // 2)
        dialog.geometry(f"450x220+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="🗑️ Delete Chat",
            font=("Segoe UI", 20, "bold"),
            text_color=self.text_light
        )
        header.pack(pady=20)
        
        # Confirmation message
        msg = ctk.CTkLabel(
            dialog,
            text=f"Are you sure you want to delete\n\"{session['name']}\"?\n\nThis action cannot be undone.",
            font=("Segoe UI", 13),
            text_color="#94a3b8",
            justify="center"
        )
        msg.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color=self.bg_dark)
        button_frame.pack(fill=tk.X, padx=30, pady=20)
        
        def confirm_delete():
            if session in self.chat_sessions:
                self.chat_sessions.remove(session)
                
                # If deleting current session, switch to another or create new
                if session == self.current_session:
                    if self.chat_sessions:
                        self.switch_session(self.chat_sessions[-1])
                    else:
                        self.new_chat_session()
                else:
                    self.update_sessions_sidebar()
                
                dialog.destroy()
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="Delete",
            font=("Segoe UI", 13, "bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            height=40,
            corner_radius=10,
            command=confirm_delete
        )
        delete_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 13, "bold"),
            fg_color=self.bot_bubble,
            hover_color="#374151",
            height=40,
            corner_radius=10,
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def switch_session(self, session):
        """Switch to a different chat session"""
        self.current_session = session
        
        # Clear and reload messages
        for widget in self.chat_display_frame.winfo_children():
            widget.destroy()
        
        for msg in session['messages']:
            self.display_message(msg['sender'], msg['text'], msg['time'])
        
        self.update_sessions_sidebar()

    def display_message(self, sender, message, timestamp):
        """Display a chat message bubble"""
        # Message container
        msg_container = ctk.CTkFrame(self.chat_display_frame, fg_color=self.chat_bg)
        msg_container.pack(fill=tk.X, pady=8)
        
        # Store message data for interactions
        msg_container.message_data = {
            'sender': sender,
            'text': message,
            'time': timestamp
        }
        msg_container.actions_visible = False
        
        if sender == "You":
            # User message - right aligned
            bubble_frame = ctk.CTkFrame(msg_container, fg_color=self.chat_bg)
            bubble_frame.pack(anchor="e", padx=10)
            
            # User icon
            user_icon = ctk.CTkLabel(
                bubble_frame,
                text="👤",
                font=("Segoe UI", 20)
            )
            user_icon.pack(side=tk.RIGHT, padx=(5, 0))
            
            # Message content frame
            content_frame = ctk.CTkFrame(bubble_frame, fg_color=self.chat_bg)
            content_frame.pack(side=tk.RIGHT)
            
            bubble = ctk.CTkFrame(content_frame, fg_color=self.user_bubble, corner_radius=15)
            bubble.pack()
            
            # Inner frame for message and actions
            inner_frame = ctk.CTkFrame(bubble, fg_color=self.user_bubble)
            inner_frame.pack(fill=tk.BOTH, expand=True)
            
            msg_label = ctk.CTkLabel(
                inner_frame,
                text=message,
                font=("Segoe UI", 13),
                text_color=self.text_light,
                wraplength=500,
                justify="left"
            )
            msg_label.pack(padx=15, pady=10, anchor="w")
            
            # Actions frame (hidden by default) - inside bubble
            actions_frame = ctk.CTkFrame(inner_frame, fg_color=self.user_bubble)
            msg_container.actions_frame = actions_frame
            
            # Time label under bubble
            time_label = ctk.CTkLabel(
                content_frame,
                text=timestamp,
                font=("Segoe UI", 9),
                text_color="#94a3b8" if self.theme_mode == "dark" else "#64748b"
            )
            time_label.pack(anchor="e", pady=(2, 0))
            
            # Make bubble clickable
            bubble.bind("<Button-1>", lambda e, c=msg_container: self.toggle_user_message_actions(c))
            msg_label.bind("<Button-1>", lambda e, c=msg_container: self.toggle_user_message_actions(c))
            inner_frame.bind("<Button-1>", lambda e, c=msg_container: self.toggle_user_message_actions(c))
            
        else:
            # Bot message - left aligned
            bubble_frame = ctk.CTkFrame(msg_container, fg_color=self.chat_bg)
            bubble_frame.pack(anchor="w", padx=10)
            
            # Bot icon
            bot_icon = ctk.CTkLabel(
                bubble_frame,
                text="🤖",
                font=("Segoe UI", 20)
            )
            bot_icon.pack(side=tk.LEFT, padx=(0, 5))
            
            # Message content frame
            content_frame = ctk.CTkFrame(bubble_frame, fg_color=self.chat_bg)
            content_frame.pack(side=tk.LEFT)
            
            bubble = ctk.CTkFrame(content_frame, fg_color=self.bot_bubble, corner_radius=15)
            bubble.pack()
            
            # Inner frame for message and actions
            inner_frame = ctk.CTkFrame(bubble, fg_color=self.bot_bubble)
            inner_frame.pack(fill=tk.BOTH, expand=True)
            
            msg_label = ctk.CTkLabel(
                inner_frame,
                text=message,
                font=("Segoe UI", 13),
                text_color=self.text_light,
                wraplength=500,
                justify="left"
            )
            msg_label.pack(padx=15, pady=10, anchor="w")
            
            # Actions frame (hidden by default) - inside bubble
            actions_frame = ctk.CTkFrame(inner_frame, fg_color=self.bot_bubble)
            msg_container.actions_frame = actions_frame
            
            # Time label under bubble
            time_label = ctk.CTkLabel(
                content_frame,
                text=timestamp,
                font=("Segoe UI", 9),
                text_color="#94a3b8" if self.theme_mode == "dark" else "#64748b"
            )
            time_label.pack(anchor="w", pady=(2, 0))
            
            # Make bubble clickable
            bubble.bind("<Button-1>", lambda e, c=msg_container: self.toggle_bot_message_actions(c))
            msg_label.bind("<Button-1>", lambda e, c=msg_container: self.toggle_bot_message_actions(c))
            inner_frame.bind("<Button-1>", lambda e, c=msg_container: self.toggle_bot_message_actions(c))

    def append_chat(self, sender, message):
        """Add message to chat"""
        timestamp = datetime.now().strftime("%I:%M %p")
        
        # Add to current session
        if self.current_session:
            msg_data = {
                'sender': sender,
                'text': message,
                'time': timestamp
            }
            self.current_session['messages'].append(msg_data)
            
            # Update session name with first user message
            if sender == "You" and self.current_session['name'] == "New Chat":
                self.current_session['name'] = message[:30] + "..." if len(message) > 30 else message
                self.update_sessions_sidebar()
        
        # Display message
        self.display_message(sender, message, timestamp)
        
        # Speak bot messages
        if sender == "Bot" and message != "Thinking..." and message != "Analyzing image...":
            threading.Thread(target=self.backend.speak, args=(message,), daemon=True).start()

    def send_message(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            return
        
        # Update RAG status
        if self.knowledge_base:
            kb_count = len(self.knowledge_base)
            self.rag_status_label.configure(text=f"📚 {kb_count} document{'s' if kb_count > 1 else ''} in knowledge base")
        else:
            self.rag_status_label.configure(text="")
        
        self.append_chat("You", prompt)
        self.prompt_entry.delete(0, tk.END)
        threading.Thread(target=self.get_bot_response, args=(prompt,), daemon=True).start()

    def get_bot_response(self, prompt):
        # Always check knowledge base first (silently)
        context = self.get_relevant_context(prompt)
        
        if context:
            # Found relevant information in knowledge base
            self.append_chat("Bot", "📚 Found relevant information in knowledge base...")
            
            # Provide context and let model decide how to use it
            enhanced_prompt = f"""You have access to the following information from the knowledge base:

{context}

User's question: {prompt}

Instructions: 
- If the knowledge base information is relevant to the question, use it in your answer and mention that you found it in the knowledge base.
- If the knowledge base information is not relevant, ignore it and answer based on your general knowledge.
- Be natural and helpful in your response."""
            
            response = self.backend.get_text_response(enhanced_prompt)
        else:
            # No relevant context found, use general knowledge
            self.append_chat("Bot", "Thinking...")
            response = self.backend.get_text_response(prompt)
        
        self.update_last_bot_message(response)

    def get_relevant_context(self, query):
        """Always check knowledge base and return relevant context only if strongly relevant"""
        if not self.knowledge_base:
            print("DEBUG: No knowledge base documents")
            return None
        
        print(f"DEBUG: Checking {len(self.knowledge_base)} documents for query: '{query}'")
        
        query_lower = query.lower()
        relevant_docs = []
        
        # Extract meaningful words from query (3+ characters, excluding common words)
        stop_words = {'what', 'when', 'where', 'which', 'who', 'how', 'why', 'does', 'did', 'will', 'can', 'could', 'would', 'should', 'the', 'this', 'that', 'these', 'those', 'with', 'from', 'into', 'through', 'during', 'before', 'after', 'have', 'has', 'had', 'been', 'being', 'are', 'was', 'were', 'your', 'their', 'there', 'here', 'then', 'than', 'them', 'they', 'some', 'such', 'only', 'also', 'just', 'very', 'more', 'most', 'much', 'many', 'make', 'made', 'like'}
        query_words = [word for word in query_lower.split() if len(word) >= 3 and word not in stop_words]
        
        print(f"DEBUG: Extracted query words: {query_words}")
        
        # If query has no meaningful words, don't use KB
        if len(query_words) < 1:
            print("DEBUG: Not enough meaningful words in query")
            return None
        
        # Search all documents for relevance
        for doc in self.knowledge_base:
            doc_lower = doc['content'].lower()
            doc_name_lower = doc['name'].lower()
            
            # Count keyword matches in content
            content_matches = sum(1 for word in query_words if word in doc_lower)
            
            # Check for phrase matches (2+ consecutive words)
            phrase_matches = 0
            for i in range(len(query_words) - 1):
                phrase = f"{query_words[i]} {query_words[i+1]}"
                if phrase in doc_lower:
                    phrase_matches += 2
            
            # Check for exact query substring match (very strong signal)
            exact_match = 0
            if len(query_lower) > 8 and query_lower in doc_lower:
                exact_match = 5
            
            # Calculate relevance score
            total_score = content_matches + phrase_matches + exact_match
            
            print(f"DEBUG: Doc '{doc['name']}' - Matches: {content_matches}, Phrases: {phrase_matches}, Exact: {exact_match}, Score: {total_score}")
            
            # Include document if it has ANY relevance (lowered threshold)
            # Require at least 1 keyword match OR 1 phrase match OR exact match
            if total_score >= 1:
                relevant_docs.append({
                    'doc': doc,
                    'score': total_score
                })
        
        print(f"DEBUG: Found {len(relevant_docs)} relevant documents")
        
        # Return relevant documents if we have any matches
        if relevant_docs:
            # Sort by relevance score (highest first)
            relevant_docs.sort(key=lambda x: x['score'], reverse=True)
            
            # Use top 2 most relevant documents
            top_docs = relevant_docs[:2]
            
            print(f"DEBUG: Using top {len(top_docs)} documents")
            
            # Format context with source attribution
            context_parts = []
            for item in top_docs:
                doc = item['doc']
                context_parts.append(f"[Source: {doc['name']}]\n{doc['content']}")
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Limit context size to avoid token limits
            if len(context) > 3000:
                context = context[:3000] + "\n\n[Content truncated...]"
            
            print(f"DEBUG: Returning context of length {len(context)}")
            return context
        
        print("DEBUG: No relevant documents found")
        return None

    def update_last_bot_message(self, new_message):
        """Update the last bot message"""
        if self.current_session and self.current_session['messages']:
            last_msg = self.current_session['messages'][-1]
            if last_msg['sender'] == "Bot":
                last_msg['text'] = new_message
                
                # Refresh display
                for widget in self.chat_display_frame.winfo_children():
                    widget.destroy()
                
                for msg in self.current_session['messages']:
                    self.display_message(msg['sender'], msg['text'], msg['time'])
                
                # Speak the response
                threading.Thread(target=self.backend.speak, args=(new_message,), daemon=True).start()

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if not file_path:
            return
        
        self.uploaded_image = file_path
        img = Image.open(file_path)
        img.thumbnail((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        
        self.img_label.configure(image=img_tk)
        self.img_label.image = img_tk
        self.img_preview_frame.configure(height=170)
        
        self.append_chat("You", "📷 [Image uploaded]")

    def ask_about_image(self):
        if not self.uploaded_image:
            self.append_chat("Bot", "Please upload an image first.")
            return
        
        question = self.prompt_entry.get().strip()
        if not question:
            self.append_chat("Bot", "Please enter your question about the image.")
            return
        
        self.append_chat("You", f"🖼️ {question}")
        self.prompt_entry.delete(0, tk.END)
        threading.Thread(
            target=self.get_image_answer, 
            args=(self.uploaded_image, question),
            daemon=True
        ).start()

    def get_image_answer(self, image_path, question):
        self.append_chat("Bot", "Analyzing image...")
        response = self.backend.get_image_response(image_path, question)
        self.update_last_bot_message(response)

    def clear_chat(self):
        """Clear current chat session"""
        if self.current_session:
            self.current_session['messages'].clear()
            
            for widget in self.chat_display_frame.winfo_children():
                widget.destroy()
            
            self.img_label.configure(image=None)
            self.img_label.image = None
            self.img_preview_frame.configure(height=0)
            self.uploaded_image = None

    def voice_input(self):
        recognizer = sr.Recognizer()
        
        def recognize():
            try:
                with sr.Microphone() as source:
                    # Show listening indicator
                    self.append_chat("Bot", "🎤 Listening...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5)
                
                # Remove listening message
                self.update_last_bot_message("")
                if self.current_session and self.current_session['messages']:
                    self.current_session['messages'].pop()
                
                # Recognize speech
                text = recognizer.recognize_google(audio)
                
                # Display as user message
                self.append_chat("You", text)
                
                # Get bot response
                threading.Thread(target=self.get_bot_response, args=(text,), daemon=True).start()
                
            except sr.WaitTimeoutError:
                self.update_last_bot_message("⚠️ No speech detected. Please try again.")
            except sr.UnknownValueError:
                self.update_last_bot_message("⚠️ Could not understand audio. Please try again.")
            except Exception as e:
                self.update_last_bot_message(f"⚠️ Voice input error: {str(e)}")
        
        threading.Thread(target=recognize, daemon=True).start()

    def toggle_user_message_actions(self, msg_container):
        """Toggle edit, copy icons for user messages inside bubble"""
        # Hide all other message actions first
        for container in self.chat_display_frame.winfo_children():
            if container != msg_container and hasattr(container, 'actions_visible') and container.actions_visible:
                container.actions_frame.pack_forget()
                container.actions_visible = False
        
        # Toggle current message actions
        if msg_container.actions_visible:
            # Hide actions
            msg_container.actions_frame.pack_forget()
            msg_container.actions_visible = False
        else:
            # Show actions inside bubble
            msg_container.actions_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
            msg_container.actions_visible = True
            
            # Clear and recreate action buttons
            for widget in msg_container.actions_frame.winfo_children():
                widget.destroy()
            
            actions_inner = ctk.CTkFrame(msg_container.actions_frame, fg_color="transparent")
            actions_inner.pack(anchor="e")
            
            msg_data = msg_container.message_data
            
            # Edit button (smaller)
            edit_btn = ctk.CTkButton(
                actions_inner,
                text="✏️",
                width=28,
                height=28,
                font=("Segoe UI", 11),
                fg_color="#6d28d9",
                hover_color="#5b21b6",
                corner_radius=6,
                command=lambda: self.edit_message(msg_container)
            )
            edit_btn.pack(side=tk.LEFT, padx=2)
            
            # Copy button (smaller)
            copy_btn = ctk.CTkButton(
                actions_inner,
                text="📋",
                width=28,
                height=28,
                font=("Segoe UI", 11),
                fg_color="#6d28d9",
                hover_color="#5b21b6",
                corner_radius=6,
                command=lambda: self.copy_message(msg_data['text'])
            )
            copy_btn.pack(side=tk.LEFT, padx=2)

    def toggle_bot_message_actions(self, msg_container):
        """Toggle copy icon for bot messages inside bubble"""
        # Hide all other message actions first
        for container in self.chat_display_frame.winfo_children():
            if container != msg_container and hasattr(container, 'actions_visible') and container.actions_visible:
                container.actions_frame.pack_forget()
                container.actions_visible = False
        
        # Toggle current message actions
        if msg_container.actions_visible:
            # Hide actions
            msg_container.actions_frame.pack_forget()
            msg_container.actions_visible = False
        else:
            # Show actions inside bubble
            msg_container.actions_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
            msg_container.actions_visible = True
            
            # Clear and recreate action buttons
            for widget in msg_container.actions_frame.winfo_children():
                widget.destroy()
            
            actions_inner = ctk.CTkFrame(msg_container.actions_frame, fg_color="transparent")
            actions_inner.pack(anchor="w")
            
            msg_data = msg_container.message_data
            
            # Copy button (smaller)
            copy_btn = ctk.CTkButton(
                actions_inner,
                text="📋",
                width=28,
                height=28,
                font=("Segoe UI", 11),
                fg_color="#374151",
                hover_color="#1f2937",
                corner_radius=6,
                command=lambda: self.copy_message(msg_data['text'])
            )
            copy_btn.pack(padx=2)

    def clear_all_message_actions(self):
        """Clear all message action frames"""
        for container in self.chat_display_frame.winfo_children():
            if hasattr(container, 'actions_visible') and container.actions_visible:
                container.actions_frame.pack_forget()
                container.actions_visible = False

    def edit_message(self, msg_container):
        """Edit a user message"""
        msg_data = msg_container.message_data
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Message")
        dialog.geometry("500x250")
        dialog.configure(fg_color=self.bg_dark)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"500x250+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="✏️ Edit Message",
            font=("Segoe UI", 20, "bold"),
            text_color=self.text_light
        )
        header.pack(pady=20)
        
        # Text area
        text_area = ctk.CTkTextbox(
            dialog,
            font=("Segoe UI", 13),
            fg_color=self.sidebar_bg,
            text_color=self.text_light,
            border_color=self.accent_purple,
            border_width=2,
            corner_radius=10,
            height=100
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        text_area.insert("1.0", msg_data['text'])
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color=self.bg_dark)
        button_frame.pack(fill=tk.X, padx=30, pady=10)
        
        def save_edit():
            new_text = text_area.get("1.0", tk.END).strip()
            if new_text:
                msg_data['text'] = new_text
                # Update in session
                for msg in self.current_session['messages']:
                    if msg['sender'] == msg_data['sender'] and msg['time'] == msg_data['time']:
                        msg['text'] = new_text
                        break
                # Refresh display
                self.refresh_chat_display()
                dialog.destroy()
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            font=("Segoe UI", 13, "bold"),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            height=40,
            corner_radius=10,
            command=save_edit
        )
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 13, "bold"),
            fg_color=self.bot_bubble,
            hover_color="#374151",
            height=40,
            corner_radius=10,
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def copy_message(self, text):
        """Copy message to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        
        # Show confirmation
        self.show_toast("📋 Copied to clipboard!")

    def show_message_time(self, timestamp):
        """Show message timestamp"""
        self.show_toast(f"🕐 {timestamp}")

    def show_toast(self, message):
        """Show a temporary toast notification"""
        toast = ctk.CTkFrame(self, fg_color=self.sidebar_bg, corner_radius=10)
        toast.place(relx=0.5, rely=0.9, anchor="center")
        
        label = ctk.CTkLabel(
            toast,
            text=message,
            font=("Segoe UI", 12),
            text_color=self.text_light
        )
        label.pack(padx=20, pady=10)
        
        # Auto-hide after 2 seconds
        self.after(2000, toast.destroy)

    def refresh_chat_display(self):
        """Refresh the chat display"""
        for widget in self.chat_display_frame.winfo_children():
            widget.destroy()
        
        if self.current_session:
            for msg in self.current_session['messages']:
                self.display_message(msg['sender'], msg['text'], msg['time'])

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        if self.theme_mode == "dark":
            # Switch to light theme
            self.theme_mode = "light"
            self.theme_btn.configure(text="☀️")
            
            # Light theme colors
            self.bg_dark = "#f8fafc"
            self.sidebar_bg = "#e2e8f0"
            self.chat_bg = "#ffffff"
            self.user_bubble = "#8b5cf6"
            self.bot_bubble = "#f1f5f9"
            self.text_light = "#1e293b"
            
        else:
            # Switch to dark theme
            self.theme_mode = "dark"
            self.theme_btn.configure(text="🌙")
            
            # Dark theme colors
            self.bg_dark = "#1a1d2e"
            self.sidebar_bg = "#16213e"
            self.chat_bg = "#0f1419"
            self.user_bubble = "#7c3aed"
            self.bot_bubble = "#2d3748"
            self.text_light = "#e2e8f0"
        
        # Recreate widgets with new theme
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()

    def open_upload_document_dialog(self):
        """Open dialog to upload document to knowledge base"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Upload Document")
        dialog.geometry("600x500")
        dialog.configure(fg_color=self.bg_dark)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="📄 Upload Document",
            font=("Segoe UI", 24, "bold"),
            text_color=self.text_light
        )
        header.pack(pady=20)
        
        # Text area for document
        text_frame = ctk.CTkFrame(dialog, fg_color=self.bg_dark)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        text_label = ctk.CTkLabel(
            text_frame,
            text="Paste your document text here...",
            font=("Segoe UI", 12),
            text_color="#94a3b8"
        )
        text_label.pack(anchor="w", pady=(0, 5))
        
        text_area = ctk.CTkTextbox(
            text_frame,
            font=("Segoe UI", 13),
            fg_color=self.sidebar_bg,
            text_color=self.text_light,
            border_color=self.accent_purple,
            border_width=2,
            corner_radius=10
        )
        text_area.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color=self.bg_dark)
        button_frame.pack(fill=tk.X, padx=30, pady=20)
        
        def add_to_kb():
            content = text_area.get("1.0", tk.END).strip()
            if content:
                doc_name = f"Document {len(self.knowledge_base) + 1}"
                self.knowledge_base.append({
                    'name': doc_name,
                    'content': content,
                    'date': datetime.now().strftime("%m/%d/%Y %I:%M %p")
                })
                dialog.destroy()
                # Show toast notification instead of chat message
                self.show_toast(f"✅ Document added: {doc_name}")
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Add to Knowledge Base",
            font=("Segoe UI", 14, "bold"),
            fg_color=self.accent_purple,
            hover_color="#6d28d9",
            height=45,
            corner_radius=10,
            command=add_to_kb
        )
        add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 14, "bold"),
            fg_color=self.bot_bubble,
            hover_color="#374151",
            height=45,
            corner_radius=10,
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def open_knowledge_base_dialog(self):
        """Open dialog to view knowledge base"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Knowledge Base")
        dialog.geometry("800x700")
        dialog.configure(fg_color=self.bg_dark)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"800x700+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="📚 Knowledge Base",
            font=("Segoe UI", 24, "bold"),
            text_color=self.text_light
        )
        header.pack(pady=20)
        
        # Content area
        content_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color=self.chat_bg,
            scrollbar_button_color=self.accent_purple
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        if not self.knowledge_base:
            no_docs_label = ctk.CTkLabel(
                content_frame,
                text="No documents in knowledge base",
                font=("Segoe UI", 14),
                text_color="#94a3b8"
            )
            no_docs_label.pack(pady=50)
        else:
            for idx, doc in enumerate(self.knowledge_base):
                doc_frame = ctk.CTkFrame(
                    content_frame,
                    fg_color=self.sidebar_bg,
                    corner_radius=10
                )
                doc_frame.pack(fill=tk.X, pady=10, padx=10)
                
                # Document header
                doc_header = ctk.CTkFrame(doc_frame, fg_color=self.sidebar_bg)
                doc_header.pack(fill=tk.X, padx=15, pady=10)
                
                doc_title = ctk.CTkLabel(
                    doc_header,
                    text=doc['name'],
                    font=("Segoe UI", 16, "bold"),
                    text_color=self.text_light
                )
                doc_title.pack(side=tk.LEFT)
                
                doc_date = ctk.CTkLabel(
                    doc_header,
                    text=doc['date'],
                    font=("Segoe UI", 11),
                    text_color="#94a3b8"
                )
                doc_date.pack(side=tk.RIGHT)
                
                # Full document content in a text box
                doc_textbox = ctk.CTkTextbox(
                    doc_frame,
                    font=("Segoe UI", 12),
                    fg_color=self.chat_bg,
                    text_color="#94a3b8",
                    wrap="word",
                    height=150
                )
                doc_textbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
                doc_textbox.insert("1.0", doc['content'])
                doc_textbox.configure(state="disabled")  # Make read-only
                
                # Action buttons
                btn_frame = ctk.CTkFrame(doc_frame, fg_color=self.sidebar_bg)
                btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
                
                # View full button
                view_btn = ctk.CTkButton(
                    btn_frame,
                    text="📖 View Full",
                    font=("Segoe UI", 11),
                    fg_color=self.accent_purple,
                    hover_color="#6d28d9",
                    height=30,
                    corner_radius=8,
                    command=lambda d=doc: self.view_full_document(d)
                )
                view_btn.pack(side=tk.LEFT, padx=(0, 5))
                
                # Delete button
                delete_btn = ctk.CTkButton(
                    btn_frame,
                    text="🗑️ Delete",
                    font=("Segoe UI", 11),
                    fg_color="#dc2626",
                    hover_color="#b91c1c",
                    height=30,
                    corner_radius=8,
                    command=lambda i=idx: self.delete_document(i, dialog)
                )
                delete_btn.pack(side=tk.LEFT)
        
        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="Close",
            font=("Segoe UI", 14, "bold"),
            fg_color=self.bot_bubble,
            hover_color="#374151",
            height=45,
            corner_radius=10,
            command=dialog.destroy
        )
        close_btn.pack(fill=tk.X, padx=30, pady=(10, 20))

    def view_full_document(self, doc):
        """View full document content in a separate window"""
        view_dialog = ctk.CTkToplevel(self)
        view_dialog.title(doc['name'])
        view_dialog.geometry("700x600")
        view_dialog.configure(fg_color=self.bg_dark)
        view_dialog.transient(self)
        view_dialog.grab_set()
        
        # Center the dialog
        view_dialog.update_idletasks()
        x = (view_dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (view_dialog.winfo_screenheight() // 2) - (600 // 2)
        view_dialog.geometry(f"700x600+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            view_dialog,
            text=f"📄 {doc['name']}",
            font=("Segoe UI", 20, "bold"),
            text_color=self.text_light
        )
        header.pack(pady=20)
        
        # Date
        date_label = ctk.CTkLabel(
            view_dialog,
            text=f"Added: {doc['date']}",
            font=("Segoe UI", 11),
            text_color="#94a3b8"
        )
        date_label.pack()
        
        # Full content
        content_textbox = ctk.CTkTextbox(
            view_dialog,
            font=("Segoe UI", 13),
            fg_color=self.sidebar_bg,
            text_color=self.text_light,
            wrap="word"
        )
        content_textbox.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        content_textbox.insert("1.0", doc['content'])
        content_textbox.configure(state="disabled")  # Make read-only
        
        # Close button
        close_btn = ctk.CTkButton(
            view_dialog,
            text="Close",
            font=("Segoe UI", 13, "bold"),
            fg_color=self.bot_bubble,
            hover_color="#374151",
            height=40,
            corner_radius=10,
            command=view_dialog.destroy
        )
        close_btn.pack(fill=tk.X, padx=30, pady=(0, 20))

    def delete_document(self, index, dialog):
        """Delete a document from knowledge base"""
        if 0 <= index < len(self.knowledge_base):
            doc_name = self.knowledge_base[index]['name']
            self.knowledge_base.pop(index)
            dialog.destroy()
            self.open_knowledge_base_dialog()
            # Show toast notification instead of chat message
            self.show_toast(f"🗑️ Deleted: {doc_name}")

if __name__ == "__main__":
    # Start directly with chatbot (no login page)
    app = OllamaDesktopChatbot()
    app.mainloop()
