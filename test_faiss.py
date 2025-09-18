from vector_db.faiss_manager import FAISSManager
from vector_db.retriever import DocumentRetriever
import logging

logging.basicConfig(level=logging.INFO)

def test_faiss_setup():
    print("=" * 60)
    print("Testing FAISS Vector Database Setup")
    print("=" * 60)
    
    # Initialize FAISS manager
    print("1. Initializing FAISS Manager...")
    faiss_manager = FAISSManager()
    
    # Build index from database
    print("2. Building FAISS index from embeddings...")
    num_vectors = faiss_manager.build_index_from_database()
    print(f"   Built index with {num_vectors} vectors")
    
    # Get index statistics
    print("3. Index Statistics:")
    stats = faiss_manager.get_index_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test retrieval
    print("\n4. Testing Document Retrieval...")
    retriever = DocumentRetriever(faiss_manager)
    
    # Test queries
    test_queries = [
        "artificial intelligence technology",
        "machine learning news",
        "latest tech developments",
        "business technology trends"
    ]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        results = retriever.retrieve_relevant_documents(
            query=query,
            top_k=3,
            score_threshold=0.2
        )
        
        print(f"   Found {results['total_results']} relevant documents")
        
        if results['retrieved_documents']:
            for doc in results['retrieved_documents']:
                print(f"     - {doc['article_title'][:50]}... (Score: {doc['similarity_score']:.3f})")
        else:
            print("     No documents found above threshold")
    
    # Test context generation
    print("\n5. Testing Context Generation...")
    context_result = retriever.retrieve_relevant_documents(
        query="What are the latest AI developments?",
        top_k=2,
        score_threshold=0.1
    )
    
    print(f"Context length: {len(context_result['context_text'])} characters")
    print(f"Sources: {context_result['sources']}")
    
    print("\n" + "=" * 60)
    print("FAISS Setup Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_faiss_setup()
