# chatbot.py
import json
import chromadb
from sentence_transformers import SentenceTransformer, util
from chromadb.config import Settings
import ollama

class FreeVETChatbot:
    def __init__(self, dataset_path="vet_chatbot_dataset.json", emergency_similarity=0.7):
        """Initialize the FREE VET chatbot with local models"""
        print("🚀 Initializing FREE VET Chatbot...")
        
        # Load dataset
        print("📚 Loading dataset...")
        with open(dataset_path, 'r') as f:
            self.dataset = json.load(f)
        print(f"✅ Loaded {len(self.dataset)} Q&A pairs")
        
        # Initialize embedding model
        print("🔧 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model ready")
        
        # Initialize ChromaDB
        print("💾 Setting up ChromaDB...")
        self.chroma_client = chromadb.Client(Settings(
            persist_directory="./chroma_db",
            anonymized_telemetry=False
        ))
        
        # Load or create collection
        try:
            self.collection = self.chroma_client.get_collection("vet_qa")
            print("✅ Loaded existing vector database")
        except:
            print("📝 Creating new vector database...")
            self.collection = self.chroma_client.create_collection("vet_qa")
            self._populate_database()
        
        # Emergency detection settings
        self.emergency_similarity = emergency_similarity
        self.emergency_examples = [
            "My dog ate chocolate",
            "My cat is vomiting and has diarrhea",
            "My pet is having a seizure",
            "My dog is choking",
            "My cat collapsed and is not breathing"
        ]
        self.emergency_embeddings = self.embedding_model.encode(self.emergency_examples, convert_to_tensor=True)
        
        print("✅ Chatbot ready! Using FREE local LLM (Ollama)\n")
    
    def _populate_database(self):
        """Populate ChromaDB with embeddings"""
        print("⚙️ Generating embeddings for all Q&As...")
        documents, metadatas, ids = [], [], []
        
        for item in self.dataset:
            doc_text = f"Q: {item['question']}\nA: {item['answer']}"
            documents.append(doc_text)
            metadatas.append({
                'question': item['question'],
                'answer': item['answer'],
                'urgency': item['urgency'],
                'species': item['species'],
                'category': item.get('category', 'general')
            })
            ids.append(str(item['id']))
        
        # Add to ChromaDB
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            embeddings = self.embedding_model.encode(batch_docs).tolist()
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids,
                embeddings=embeddings
            )
            print(f"  Processed {min(i+batch_size, len(documents))}/{len(documents)}...")
        print("✅ Vector database populated!")
    
    def is_emergency(self, question):
        """Hybrid emergency detection: keyword + embedding similarity"""
        question_lower = question.lower()
        # Quick keyword check
        keywords = ['bleeding', 'seizure', 'chocolate', 'collapsed', 'not breathing', 'choking', 'vomiting', 'diarrhea']
        if any(k in question_lower for k in keywords):
            return True
        
        # Embedding similarity check
        q_emb = self.embedding_model.encode(question, convert_to_tensor=True)
        similarities = util.cos_sim(q_emb, self.emergency_embeddings)
        if similarities.max().item() >= self.emergency_similarity:
            return True
        
        return False
    
    def retrieve_relevant_context(self, question, n_results=3):
        """Retrieve relevant Q&As from vector DB"""
        query_embedding = self.embedding_model.encode([question]).tolist()
        results = self.collection.query(query_embeddings=query_embedding, n_results=n_results)
        return results
    
    def generate_response(self, question, context_docs):
        """Generate response using Ollama LLM"""
        context = "\n\n".join([f"Relevant Information {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
        prompt = f"""You are a veterinary assistant. Answer based ONLY on the context below. If info is missing, say so.

Context:
{context}

Question: {question}

Instructions:
- If emergency, start with "⚠️ EMERGENCY:"
- Concise but thorough
- Include disclaimer to consult a vet if unsure
Answer:"""
        try:
            response = ollama.chat(
                model='llama3.2:3b',
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"Error generating response: {e}"
    
    def chat(self, question):
        """Main chat function"""
        print(f"\n❓ Question: {question}")
        is_emergency = self.is_emergency(question)
        if is_emergency:
            print("⚠️ EMERGENCY DETECTED")
        
        results = self.retrieve_relevant_context(question, n_results=3)
        context_docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        response = self.generate_response(question, context_docs)
        output = {
            'question': question,
            'answer': response,
            'is_emergency': is_emergency,
            'sources': [{'question': m['question'], 'urgency': m['urgency'], 'species': m['species']} for m in metadatas]
        }
        return output
    
    def format_output(self, output):
        print("\n" + "="*60)
        if output['is_emergency']:
            print("⚠️ EMERGENCY SITUATION DETECTED ⚠️")
            print("Please contact your veterinarian immediately!")
            print("="*60)
        print(f"\n💬 Answer:\n{output['answer']}")
        print(f"\n📚 Sources used:")
        for i, source in enumerate(output['sources'], 1):
            print(f"  {i}. {source['question']} [{source['urgency']}]")
        print("="*60 + "\n")
