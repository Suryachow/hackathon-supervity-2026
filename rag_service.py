import os
import re
import json
import time
import pickle
import requests
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration
TOP_K_RETRIEVE = 10
FINAL_K = 5
SIMILARITY_THRESHOLD = 0.1 # Lower threshold for TF-IDF
MAX_CONTEXT_CHARS = 6000
PERPLEXITY_MODEL = "sonar"

class RAGService:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.vectorizer = None
        self.tfidf_matrix = None
        self.metadata = []
        self.perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
        
        self.index_path = os.path.join(self.data_dir, "tfidf_index.pkl")
        
        # Initialize
        if os.path.exists(self.index_path):
            self.load_index()
        else:
            self.build_index()

    def clean_text(self, s):
        if not isinstance(s, str):
            return ""
        s = s.replace("\r", " ").replace("\n", " ").strip()
        s = re.sub(r'\s+', ' ', s)
        return s.strip()

    def build_index(self):
        print(f"Scanning {self.data_dir} for data...")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            return

        documents = []

        for f in os.listdir(self.data_dir):
            path = os.path.join(self.data_dir, f)
            df = None
            
            if f.endswith(".csv"):
                try:
                    df = pd.read_csv(path)
                except Exception as e:
                    print(f"Error reading {f}: {e}")
            elif f.endswith(".json"):
                try:
                    df = pd.read_json(path, lines=True)
                except Exception as e:
                    print(f"Error reading {f}: {e}")
            
            if df is not None and not df.empty:
                df["_source_file"] = f
                
                # Detect text column specifically for this file
                text_column = self._auto_detect_text_column(df)
                if not text_column:
                    print(f"Skipping {f}: No text column detected.")
                    continue
                
                print(f"Processing {f}: using column '{text_column}'")
                
                for idx, row in df.iterrows():
                    text = self.clean_text(str(row.get(text_column, "")))
                    if len(text) < 5: 
                        continue
                    
                    # Combine other potentially useful columns
                    extra = []
                    for col in df.columns:
                        if col == text_column or col == "_source_file":
                            continue
                        if any(k in col.lower() for k in ["title", "summary", "solution", "answer", "reply", "topic", "desc"]):
                            val = self.clean_text(str(row.get(col, "")))
                            if val and len(val) > 3:
                                extra.append(f"{col}: {val}")
                    
                    full_text = text
                    if extra:
                        full_text = f"Issue: {text}\n" + "\n".join(extra)

                    documents.append({
                        "source_id": f"{f}::row_{idx}",
                        "text": full_text,
                        "meta": row.to_dict()
                    })

        if not documents:
            print("No documents found to index.")
            return

        print(f"Indexing {len(documents)} documents using TF-IDF...")
        texts = [d["text"] for d in documents]
        
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.metadata = documents
        
        # Save cache
        print("Saving index to cache...")
        with open(self.index_path, "wb") as f:
            pickle.dump({
                "vectorizer": self.vectorizer,
                "matrix": self.tfidf_matrix,
                "metadata": self.metadata
            }, f)
            
        print(f"Index built and saved with {len(documents)} documents.")

    def load_index(self):
        print("Loading index from cache...")
        try:
            with open(self.index_path, "rb") as f:
                data = pickle.load(f)
                self.vectorizer = data["vectorizer"]
                self.tfidf_matrix = data["matrix"]
                self.metadata = data["metadata"]
            print(f"Index loaded with {len(self.metadata)} documents.")
        except Exception as e:
            print(f"Error loading cache: {e}. Rebuilding...")
            self.build_index()

    def _auto_detect_text_column(self, df):
        candidates = ["conversation", "text", "dialogue", "issue", "description", "ticket_text", "content"]
        for c in candidates:
            if c in df.columns:
                return c
        text_like = [c for c in df.columns if df[c].dtype == object]
        if not text_like:
            return None
        # choose column with largest average length
        avg_len = {c: df[c].astype(str).map(len).mean() for c in text_like}
        if not avg_len:
            return None
        return max(avg_len, key=avg_len.get)

    def retrieve(self, query):
        if self.vectorizer is None or self.tfidf_matrix is None:
            return []
        
        query_vec = self.vectorizer.transform([self.clean_text(query)])
        
        # Calculate Cosine Similarity
        cosine_similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get Top K indices
        related_docs_indices = cosine_similarities.argsort()[::-1][:TOP_K_RETRIEVE]
        
        results = []
        for i in related_docs_indices:
            score = cosine_similarities[i]
            if score <= 0: # If using TF-IDF, 0 means no keyword match
                continue
                
            meta = self.metadata[i]
            results.append({
                "score": float(score),
                "text": meta["text"],
                "source_id": meta["source_id"]
            })
        return results

    def answer_query(self, query, api_key=None):
        if api_key:
            self.perplexity_api_key = api_key
            
        retrieved = self.retrieve(query)
        
        # Build Context with simplified IDs
        context_parts = []
        curr_len = 0
        
        # Create a mapping for the prompt
        doc_map = {} 
        
        for idx, r in enumerate(retrieved[:FINAL_K]):
            doc_id = f"[{idx+1}]"
            doc_map[doc_id] = r['source_id'] # Keep track for logging if needed
            
            block = f"{doc_id}\n{r['text']}\n"
            if curr_len + len(block) > MAX_CONTEXT_CHARS:
                break
            context_parts.append(block)
            curr_len += len(block)
        
        context = "\n".join(context_parts)
        
        if not self.perplexity_api_key:
            return {
                "answer": "Perplexity API Key is missing. I can only retrieve documents.",
                "context": context,
                "sources": retrieved,
                "escalation": True
            }

        # Call Perplexity
        system_prompt = """You are an expert Telecom Customer Support Assistant.

You will be given HISTORICAL LOGS with numbered references like [1], [2], etc.
Use these logs to answer the user's question.

STRICT RULES FOR CITATIONS:
- Use citation numbers like [1], [2] ONLY when stating a specific fact taken from the logs.
- Do NOT use citations for greetings, empathy, suggestions, or general advice.
- Do NOT overuse citations.
- Never mention filenames, row numbers, or internal identifiers.
- Never explain what the citations mean.

ANSWERING STYLE:
- Start with a direct, clear answer.
- Then provide step-by-step guidance if applicable.
- Be professional, calm, and empathetic.
- Keep the response concise and customer-friendly.

ESCALATION:
- If the logs do not contain enough information to answer confidently, say so politely.
- In that case, recommend escalation to a human support agent."""
        
        print(f"DEBUG: Sending to Perplexity (Context Metadata: {[r['source_id'] for r in retrieved[:FINAL_K]]})")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"HISTORICAL LOGS:\n{context}\n\nUSER QUERY:\n{query}"}
        ]
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": PERPLEXITY_MODEL,
            "messages": messages,
            "temperature": 0.1
        }
        
        # Determine Escalation
        max_score = 0
        if retrieved:
            max_score = retrieved[0]['score']
        
        # Heuristic for escalation
        should_escalate = False
        
        # Don't escalate short greetings even if similarity is low
        is_short_greeting = len(query.strip()) < 10
        
        if max_score < SIMILARITY_THRESHOLD and not is_short_greeting:
            should_escalate = True
            print(f"DEBUG: Escalate due to low similarity ({max_score:.3f} < {SIMILARITY_THRESHOLD})")

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                answer = data["choices"][0]["message"]["content"]
                
                # Secondary escalation check: if model is uncertain
                if "not enough information" in answer.lower() or "i cannot answer" in answer.lower():
                    should_escalate = True

                return {
                    "answer": answer,
                    "context": context,
                    "sources": retrieved,
                    "escalation": should_escalate
                }
            else:
                return {
                    "answer": f"Error from Perplexity: {resp.text}",
                    "context": context,
                    "sources": retrieved,
                    "escalation": True
                }
        except Exception as e:
            return {
                "answer": f"Exception calling Perplexity: {str(e)}",
                "context": context,
                "sources": retrieved,
                "escalation": True
            }
