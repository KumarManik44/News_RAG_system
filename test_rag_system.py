from llm_integration.news_summarizer import IntelligentNewsSummarizer
from llm_integration.rag_generator import NewsRAGGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_complete_rag_system():
    print("=" * 80)
    print("TESTING COMPLETE RAG NEWS SUMMARIZATION SYSTEM")
    print("=" * 80)
    
    # Initialize the system (works with or without OpenAI API key)
    summarizer = IntelligentNewsSummarizer()  # Add your OpenAI key here if available
    
    print("\n1. Testing Individual Topic Summarization...")
    print("-" * 50)
    
    topics_to_test = [
        "artificial intelligence",
        "technology trends", 
        "business developments",
        "latest tech news"
    ]
    
    for topic in topics_to_test:
        print(f"\nTopic: {topic}")
        response = summarizer.summarize_topic(topic)
        
        print(f"Confidence Score: {response.confidence_score:.3f}")
        print(f"Sources Found: {len(response.sources)}")
        print(f"Retrieved Documents: {len(response.retrieved_documents)}")
        
        # Show preview of answer
        answer_preview = response.answer[:200] + "..." if len(response.answer) > 200 else response.answer
        print(f"Answer Preview: {answer_preview}")
        
        if response.sources:
            print(f"Top Source: {response.sources[0]}")
        
        print("-" * 30)
    
    print("\n2. Testing Question Answering...")
    print("-" * 50)
    
    test_questions = [
        "What are the latest developments in AI technology?",
        "How is technology changing business?", 
        "What recent innovations have been announced?",
        "What are companies doing with artificial intelligence?"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        response = summarizer.answer_news_question(question)
        
        print(f"Confidence: {response.confidence_score:.3f}")
        print(f"Documents Retrieved: {len(response.retrieved_documents)}")
        
        # Show first 150 characters of answer
        answer_snippet = response.answer[:150] + "..." if len(response.answer) > 150 else response.answer
        print(f"Answer: {answer_snippet}")
        
    print("\n3. Testing Trending Topics Summary...")
    print("-" * 50)
    
    trending = summarizer.trending_topics_summary()
    
    for i, topic_summary in enumerate(trending, 1):
        print(f"\nTrending Topic #{i}: {topic_summary['topic']}")
        print(f"Articles: {topic_summary['article_count']}")
        print(f"Confidence: {topic_summary['confidence']:.3f}")
        print(f"Sources: {', '.join(topic_summary['sources'][:2])}")
        
        # Show snippet of summary
        summary_snippet = topic_summary['summary'][:120] + "..." if len(topic_summary['summary']) > 120 else topic_summary['summary']
        print(f"Summary: {summary_snippet}")
    
    print("\n4. Testing Daily News Briefing...")
    print("-" * 50)
    
    briefing = summarizer.daily_news_briefing(['artificial intelligence', 'technology companies'])
    
    for topic, response in briefing.items():
        print(f"\nBriefing - {topic.title()}:")
        print(f"Confidence: {response.confidence_score:.3f}")
        print(f"Sources: {len(response.sources)}")
        
        # Show key points extraction
        if "**Key Points:**" in response.answer:
            key_points_section = response.answer.split("**Key Points:**")[1].split("**Sources:**")[0].strip()
            print(f"Key Points Preview: {key_points_section[:100]}...")
    
    print("\n" + "=" * 80)
    print("RAG SYSTEM TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    test_complete_rag_system()
