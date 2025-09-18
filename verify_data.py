import sqlite3
from config.settings import settings

def check_stored_articles():
    """Verify articles are properly stored in database"""
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM articles")
    total_count = cursor.fetchone()[0]
    print(f"Total articles in database: {total_count}")
    
    # Get articles by source
    cursor.execute("SELECT source, COUNT(*) FROM articles GROUP BY source")
    sources = cursor.fetchall()
    print("\nArticles by source:")
    for source, count in sources:
        print(f"  {source}: {count} articles")
    
    # Show sample article
    cursor.execute("SELECT title, source, published_at FROM articles LIMIT 3")
    samples = cursor.fetchall()
    print("\nSample articles:")
    for title, source, published in samples:
        print(f"  • {title[:60]}... ({source})")
    
    conn.close()

if __name__ == "__main__":
    check_stored_articles()
