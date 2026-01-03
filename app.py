from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from rag_service import RAGService
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Global RAG service instance
rag_service = None

def get_rag_service():
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("message")
    api_key = data.get("apiKey")  # Optional: User can provide it from UI
    
    if not query:
        return jsonify({"error": "No message provided"}), 400

    service = get_rag_service()
    
    # Process query
    result = service.answer_query(query, api_key=api_key)
    
    return jsonify(result)

@app.route("/status", methods=["GET"])
def status():
    service = get_rag_service()
    return jsonify({
        "status": "ready" if service.tfidf_matrix is not None else "empty (no data)",
        "doc_count":  service.tfidf_matrix.shape[0] if service.tfidf_matrix is not None else 0
    })

if __name__ == "__main__":
    # Pre-load model on startup
    print("Initializing RAG Service...")
    get_rag_service()
    print("Server starting at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
