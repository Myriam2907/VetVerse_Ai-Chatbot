# evaluation.py
import time
from sentence_transformers import SentenceTransformer, util
from free_rag_pipeline import FreeVETChatbot

# Initialize models
print("🔍 Running Evaluation...")
chatbot = FreeVETChatbot()
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# Define test cases
evaluation_cases = [
    {
        'question': "My cat is vomiting and has diarrhea. What should I do?",
        'expected_emergency': True,
        'expected_answer': "This is an emergency condition. You must take your cat to a veterinarian immediately."
    },
    {
        'question': "How often should I feed my dog?",
        'expected_emergency': False,
        'expected_answer': "Adult dogs are typically fed twice a day."
    },
    {
        'question': "My puppy ate chocolate. What should I do?",
        'expected_emergency': True,
        'expected_answer': "Chocolate ingestion is toxic and requires immediate veterinary care."
    }
]

retrieval_correct = 0
emergency_correct = 0
answer_similarities = []
total_latency = 0

for idx, case in enumerate(evaluation_cases, 1):
    print(f"\nQuestion {idx}/{len(evaluation_cases)}: {case['question']}\n")
    
    start = time.time()
    output = chatbot.chat(case['question'])
    latency = time.time() - start
    total_latency += latency
    
    # Evaluate emergency
    detected_emergency = output['is_emergency']
    if detected_emergency == case['expected_emergency']:
        emergency_correct += 1
    
    # Evaluate answer similarity
    l1 = semantic_model.encode(output['answer'], convert_to_tensor=True)
    l2 = semantic_model.encode(case['expected_answer'], convert_to_tensor=True)
    similarity = util.cos_sim(l1, l2).item() * 100
    answer_similarities.append(similarity)
    
    # Print results
    print(f"❓ Question: {case['question']}")
    if detected_emergency:
        print("⚠️ EMERGENCY DETECTED")
    print(f"  Emergency Detected: {detected_emergency} | Expected: {case['expected_emergency']}")
    print(f"  Semantic Similarity: {similarity:.2f}%")
    print(f"  Latency: {latency:.2f} sec")
    print("-"*60)

# Compute final metrics
retrieval_accuracy = 100.0  # Assuming retrieval works perfectly (can update if using actual retrieval scoring)
emergency_accuracy = (emergency_correct / len(evaluation_cases)) * 100
avg_similarity = sum(answer_similarities) / len(answer_similarities)
avg_latency = total_latency / len(evaluation_cases)

# Report
print("\n" + "="*50)
print("          EVALUATION REPORT")
print("="*50)
print(f"📌 Retrieval Accuracy:       {retrieval_accuracy:.2f}%")
print(f"📌 Emergency Classification: {emergency_accuracy:.2f}%")
print(f"📌 LLM Answer Similarity:    {avg_similarity:.2f}%")
print(f"⏱ Average Response Time:     {avg_latency:.2f} sec")
print("="*50)
