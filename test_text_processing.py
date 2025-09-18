from text_processing.processor import TextProcessor
import logging

logging.basicConfig(level=logging.INFO)

def test_text_processing():
    processor = TextProcessor()
    
    print("Starting text processing...")
    processed_count = processor.process_unprocessed_articles()
    
    print(f"Successfully processed {processed_count} articles")
    
    # Check results
    import sqlite3
    from config.settings import settings
    
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM text_chunks")
    total_chunks = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT language_code, COUNT(*) 
        FROM text_chunks 
        GROUP BY language_code
    """)
    language_distribution = cursor.fetchall()
    
    cursor.execute("""
        SELECT AVG(word_count), AVG(char_count) 
        FROM text_chunks
    """)
    avg_stats = cursor.fetchone()
    
    print(f"\nProcessing Results:")
    print(f"Total chunks created: {total_chunks}")
    print(f"Average words per chunk: {avg_stats[0]:.1f}")
    print(f"Average characters per chunk: {avg_stats[1]:.1f}")
    print(f"Language distribution: {language_distribution}")
    
    conn.close()

if __name__ == "__main__":
    test_text_processing()
