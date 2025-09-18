from embeddings.embedding_generator import EmbeddingGenerator
import logging

logging.basicConfig(level=logging.INFO)

def test_embeddings():
    print("Initializing embedding generator...")
    
    # Initialize with optimized model for news content
    generator = EmbeddingGenerator(
        model_name="all-MiniLM-L6-v2",  # Fast, good quality model
        batch_size=16  # Conservative batch size for stability
    )
    
    print(f"Model loaded. Embedding dimension: {generator.embedding_dim}")
    
    # Generate embeddings for unprocessed chunks
    print("Generating embeddings...")
    processed_count = generator.generate_embeddings_for_unprocessed_chunks()
    
    print(f"Successfully processed {processed_count} chunks")
    
    # Get statistics
    stats = generator.get_embedding_stats()
    print(f"\nEmbedding Statistics:")
    print(f"Total embeddings: {stats['total_embeddings']}")
    print(f"Model distribution: {stats['model_distribution']}")
    print(f"Embedding dimensions: {stats['embedding_dimensions']}")
    
    # Test retrieval
    print("\nTesting embedding retrieval...")
    embeddings, chunk_ids = generator.get_all_embeddings()
    
    if len(embeddings) > 0:
        print(f"Retrieved {len(embeddings)} embeddings")
        print(f"Embedding shape: {embeddings[0].shape}")
        print(f"Sample chunk ID: {chunk_ids[0]}")
        
        # Test similarity between first two embeddings
        if len(embeddings) > 1:
            similarity = np.dot(embeddings[0], embeddings[1])
            print(f"Similarity between first two embeddings: {similarity:.4f}")
    
if __name__ == "__main__":
    import numpy as np
    test_embeddings()
