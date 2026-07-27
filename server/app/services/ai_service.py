import json
import re
import google.generativeai as genai
from openai import OpenAI
from app.config import settings

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Configure OpenAI
openai_client = None
if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("your_"):
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

class AIService:
    @staticmethod
    def get_embedding(text: str) -> list:
        """
        Generates vector embeddings for a given text using Gemini or OpenAI.
        """
        # Try Gemini first
        if settings.GEMINI_API_KEY:
            try:
                # Truncate text to avoid limits
                truncated_text = text[:10000]
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=truncated_text,
                    task_type="retrieval_document"
                )
                return result['embedding']
            except Exception as e:
                print(f"[*] Gemini embedding error: {e}. Trying OpenAI...")
        
        # Fallback to OpenAI
        if openai_client:
            try:
                response = openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text[:8000]
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"[*] OpenAI embedding error: {e}")

        # Fallback Mock embedding if offline or keys missing (dimension 768)
        print("[*] WARNING: No AI API keys available or API call failed. Generating pseudo-random embedding.")
        np_state = hash(text) % (2**32)
        import numpy as np
        rng = np.random.default_rng(np_state)
        return rng.standard_normal(768).tolist()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list:
        """
        Splits text into overlapping chunks.
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunks.append(text[start:end])
            start += chunk_size - overlap
            
        return chunks

    @staticmethod
    def generate_content(prompt: str, system_instruction: str = "") -> str:
        """
        Helper method to call LLM for text generation (Gemini primary, OpenAI fallback).
        """
        # Try Gemini
        if settings.GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction if system_instruction else None
                )
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"[*] Gemini generation failed: {e}. Trying OpenAI...")
        
        # Try OpenAI
        if openai_client:
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[*] OpenAI generation failed: {e}")

        # Fallback response
        return "Offline Mode: AI keys are missing or invalid. Please check your config.py/env setup."

    @classmethod
    def summarize_text(cls, text: str) -> str:
        """
        Generates a concise summary of a text document.
        """
        prompt = f"Please read the following text and provide a comprehensive, structured summary highlighting key concepts, formulas, dates, and definitions:\n\n{text[:15000]}"
        system = "You are an expert academic tutor. Summarize the text clearly with bullet points."
        return cls.generate_content(prompt, system)

    @classmethod
    def explain_concept(cls, concept: str, history: list = None) -> str:
        """
        Explains study doubts or concepts. Takes message history into account if provided.
        """
        system = "You are StudyBuddy AI, a helpful and friendly study assistant. Explain concepts clearly and concisely using simple language, formatting math equations in LaTeX style, and utilizing Markdown code blocks for code snippets."
        
        prompt = ""
        if history:
            prompt += "Conversation history:\n"
            for msg in history:
                role = "User" if msg.get("role") == "user" else "Assistant"
                prompt += f"{role}: {msg.get('content')}\n"
        
        prompt += f"\nUser Question: {concept}\nAnswer:"
        return cls.generate_content(prompt, system)

    @classmethod
    def generate_flashcards(cls, text: str) -> list:
        """
        Generates flashcards (Q&As) from text. Returns a list of dicts.
        """
        prompt = (
            "Read the following text and generate exactly 5 high-quality flashcards for learning. "
            "Return the output STRICTLY as a JSON array of objects, where each object has "
            "exactly two fields: 'front' (the question or term) and 'back' (the answer or explanation). "
            "Do not include markdown tags like ```json in your response, just the raw JSON array. "
            f"\n\nText:\n{text[:8000]}"
        )
        system = "You are an AI learning assistant that formats output strictly as raw JSON."
        
        raw_res = cls.generate_content(prompt, system)
        try:
            # Clean response from any markdown block decoration if present
            clean_res = re.sub(r"^```json\s*|\s*```$", "", raw_res, flags=re.MULTILINE).strip()
            return json.loads(clean_res)
        except Exception as e:
            print(f"[*] Error parsing flashcards JSON: {e}. Raw response: {raw_res}")
            # Return basic safety flashcards if parsing fails
            return [
                {"front": "What was the main topic of the uploaded document?", "back": "Refer to your study notes for a complete view."},
                {"front": "Spaced Repetition benefits", "back": "Improves long-term memory retention by reviewing material right before forgetting."}
            ]

    @classmethod
    def generate_quiz(cls, text: str, num_questions: int = 5, difficulty: str = "medium") -> list:
        """
        Generates multiple-choice quiz questions from text. Returns a list of dicts.
        """
        prompt = (
            f"Read the following text and generate exactly {num_questions} multiple-choice questions "
            f"appropriate for a '{difficulty}' difficulty level. "
            "Return the output STRICTLY as a JSON array of objects. Each object must have: "
            "'question_text' (str), 'question_type' (must be 'mcq'), 'options' (a comma-separated string "
            "of exactly 4 choices, e.g. 'A) Python, B) Java, C) C++, D) Rust'), and 'correct_answer' "
            "(str, matching exactly one of the options, e.g. 'A) Python'). "
            "Do not include markdown tags like ```json, return only valid raw JSON. "
            f"\n\nText:\n{text[:8000]}"
        )
        system = "You are a teacher formatting a quiz strictly as a JSON array of questions."
        
        raw_res = cls.generate_content(prompt, system)
        try:
            clean_res = re.sub(r"^```json\s*|\s*```$", "", raw_res, flags=re.MULTILINE).strip()
            return json.loads(clean_res)
        except Exception as e:
            print(f"[*] Error parsing quiz JSON: {e}. Raw response: {raw_res}")
            # Return basic safety quiz if parsing fails
            return [
                {
                    "question_text": "Which memory technique reviews material at increasing intervals?",
                    "question_type": "mcq",
                    "options": "A) Rote learning, B) Spaced Repetition, C) Summarization, D) Brainstorming",
                    "correct_answer": "B) Spaced Repetition"
                }
            ]

    @classmethod
    def answer_with_rag(cls, query: str, context_chunks: list) -> str:
        """
        Answers a user query using retrieved document chunks as reference.
        """
        context_str = "\n---\n".join([c.get("text", "") for c in context_chunks])
        prompt = (
            "You are StudyBuddy AI, an expert academic tutor. Answer the user's question relying "
            "primarily on the provided study context. If the answer cannot be found in the context, "
            "use your general knowledge but state that it wasn't directly found in the document. "
            f"\n\nStudy Context:\n{context_str}\n\nUser Question: {query}\nAnswer:"
        )
        return cls.generate_content(prompt)

ai_service = AIService()
