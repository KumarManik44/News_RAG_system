import logging
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import psutil
import threading
from config.settings import settings

@dataclass
class SystemMetrics:
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    api_response_time: float
    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_confidence_score: float

@dataclass
class RAGMetrics:
    timestamp: str
    queries_processed: int
    avg_retrieval_time_ms: float
    avg_generation_time_ms: float
    avg_confidence_score: float
    top_query_topics: List[str]
    data_freshness_hours: float

class NewsRAGMonitor:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.logger = logging.getLogger(__name__)
        self.init_monitoring_tables()
        
        # Metrics storage
        self.query_metrics = []
        self.system_metrics = []
        
    def init_monitoring_tables(self):
        """Initialize monitoring tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                api_response_time REAL,
                total_queries INTEGER,
                successful_queries INTEGER,
                failed_queries INTEGER,
                avg_confidence_score REAL
            )
        ''')
        
        # Query logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                query_text TEXT NOT NULL,
                response_time_ms REAL,
                confidence_score REAL,
                retrieved_documents INTEGER,
                status TEXT,
                error_message TEXT
            )
        ''')
        
        # Data quality metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_quality_metrics (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                total_articles INTEGER,
                processed_articles INTEGER,
                total_embeddings INTEGER,
                avg_embedding_quality REAL,
                data_freshness_hours REAL,
                duplicate_articles INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_query(self, query: str, response_time_ms: float, 
                  confidence_score: float, retrieved_docs: int, 
                  status: str = "success", error_message: str = None):
        """Log individual query metrics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO query_logs 
            (timestamp, query_text, response_time_ms, confidence_score, 
             retrieved_documents, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            query[:200],  # Truncate long queries
            response_time_ms,
            confidence_score,
            retrieved_docs,
            status,
            error_message
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Query logged: {status} - {response_time_ms:.2f}ms")
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        
        # System resource usage
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        # Database query metrics (last hour)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed,
                AVG(response_time_ms) as avg_response_time,
                AVG(confidence_score) as avg_confidence
            FROM query_logs 
            WHERE timestamp > ?
        ''', (one_hour_ago,))
        
        result = cursor.fetchone()
        conn.close()
        
        total_queries = result[0] or 0
        successful_queries = result[1] or 0
        failed_queries = result[2] or 0
        avg_response_time = result[3] or 0
        avg_confidence = result[4] or 0
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            api_response_time=avg_response_time,
            total_queries=total_queries,
            successful_queries=successful_queries,
            failed_queries=failed_queries,
            avg_confidence_score=avg_confidence
        )
    
    def store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics in database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_metrics 
            (timestamp, cpu_usage, memory_usage, disk_usage, 
             api_response_time, total_queries, successful_queries, 
             failed_queries, avg_confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.timestamp,
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.disk_usage,
            metrics.api_response_time,
            metrics.total_queries,
            metrics.successful_queries,
            metrics.failed_queries,
            metrics.avg_confidence_score
        ))
        
        conn.commit()
        conn.close()
    
    def evaluate_data_quality(self) -> Dict:
        """Evaluate current data quality metrics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get article statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_articles,
                SUM(CASE WHEN processed = 1 THEN 1 ELSE 0 END) as processed_articles
            FROM articles
        ''')
        article_stats = cursor.fetchone()
        
        # Get embedding statistics
        cursor.execute('SELECT COUNT(*) FROM embeddings')
        total_embeddings = cursor.fetchone()[0]
        
        # Check data freshness (hours since last article)
        cursor.execute('''
            SELECT 
                ROUND((julianday('now') - julianday(MAX(created_at))) * 24, 2) as hours_since_last
            FROM articles
        ''')
        freshness_result = cursor.fetchone()
        data_freshness = freshness_result[0] if freshness_result[0] else 0
        
        # Check for duplicates (simplified)
        cursor.execute('''
            SELECT COUNT(*) - COUNT(DISTINCT url) as duplicates
            FROM articles
        ''')
        duplicates = cursor.fetchone()[0]
        
        conn.close()
        
        quality_metrics = {
            'total_articles': article_stats[0],
            'processed_articles': article_stats[1],
            'processing_rate': article_stats[1] / max(article_stats[0], 1),
            'total_embeddings': total_embeddings,
            'embedding_coverage': total_embeddings / max(article_stats[1], 1),
            'data_freshness_hours': data_freshness,
            'duplicate_articles': duplicates,
            'quality_score': self._calculate_quality_score(
                article_stats[1] / max(article_stats[0], 1),
                total_embeddings / max(article_stats[1], 1),
                data_freshness
            )
        }
        
        # Store quality metrics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data_quality_metrics 
            (timestamp, total_articles, processed_articles, total_embeddings,
             avg_embedding_quality, data_freshness_hours, duplicate_articles)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            quality_metrics['total_articles'],
            quality_metrics['processed_articles'],
            quality_metrics['total_embeddings'],
            quality_metrics['quality_score'],
            quality_metrics['data_freshness_hours'],
            quality_metrics['duplicate_articles']
        ))
        
        conn.commit()
        conn.close()
        
        return quality_metrics
    
    def _calculate_quality_score(self, processing_rate: float, 
                               embedding_coverage: float, 
                               freshness_hours: float) -> float:
        """Calculate overall data quality score (0-1)"""
        
        # Processing rate score (0-1)
        processing_score = min(processing_rate, 1.0)
        
        # Embedding coverage score (0-1)
        embedding_score = min(embedding_coverage, 1.0)
        
        # Freshness score (1 for < 24 hours, decreasing)
        freshness_score = max(0, 1 - (freshness_hours / 168))  # 1 week = 0
        
        # Weighted average
        quality_score = (
            processing_score * 0.4 + 
            embedding_score * 0.4 + 
            freshness_score * 0.2
        )
        
        return round(quality_score, 3)
    
    def get_monitoring_dashboard_data(self) -> Dict:
        """Get comprehensive monitoring data for dashboard"""
        
        # Get latest system metrics
        system_metrics = self.collect_system_metrics()
        
        # Get data quality metrics
        quality_metrics = self.evaluate_data_quality()
        
        # Get performance trends (last 24 hours)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        cursor.execute('''
            SELECT 
                DATE(timestamp) as date,
                AVG(response_time_ms) as avg_response_time,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) as query_count
            FROM query_logs 
            WHERE timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (yesterday,))
        
        performance_trends = cursor.fetchall()
        conn.close()
        
        return {
            'system_health': {
                'cpu_usage': system_metrics.cpu_usage,
                'memory_usage': system_metrics.memory_usage,
                'disk_usage': system_metrics.disk_usage,
                'status': 'healthy' if system_metrics.cpu_usage < 80 else 'warning'
            },
            'query_performance': {
                'total_queries': system_metrics.total_queries,
                'success_rate': system_metrics.successful_queries / max(system_metrics.total_queries, 1),
                'avg_response_time': system_metrics.api_response_time,
                'avg_confidence': system_metrics.avg_confidence_score
            },
            'data_quality': quality_metrics,
            'performance_trends': [
                {
                    'date': row[0],
                    'avg_response_time': row[1],
                    'avg_confidence': row[2],
                    'query_count': row[3]
                }
                for row in performance_trends
            ],
            'alerts': self._generate_alerts(system_metrics, quality_metrics)
        }
    
    def _generate_alerts(self, system_metrics: SystemMetrics, 
                        quality_metrics: Dict) -> List[Dict]:
        """Generate system alerts based on metrics"""
        
        alerts = []
        
        # System resource alerts
        if system_metrics.cpu_usage > 85:
            alerts.append({
                'type': 'warning',
                'message': f'High CPU usage: {system_metrics.cpu_usage:.1f}%',
                'timestamp': system_metrics.timestamp
            })
        
        if system_metrics.memory_usage > 90:
            alerts.append({
                'type': 'critical',
                'message': f'High memory usage: {system_metrics.memory_usage:.1f}%',
                'timestamp': system_metrics.timestamp
            })
        
        # Performance alerts
        if system_metrics.api_response_time > 5000:  # 5 seconds
            alerts.append({
                'type': 'warning',
                'message': f'Slow API response time: {system_metrics.api_response_time:.0f}ms',
                'timestamp': system_metrics.timestamp
            })
        
        # Data quality alerts
        if quality_metrics['data_freshness_hours'] > 48:
            alerts.append({
                'type': 'warning',
                'message': f'Stale data: {quality_metrics["data_freshness_hours"]:.1f} hours old',
                'timestamp': datetime.now().isoformat()
            })
        
        if quality_metrics['quality_score'] < 0.7:
            alerts.append({
                'type': 'critical',
                'message': f'Poor data quality score: {quality_metrics["quality_score"]:.2f}',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts

# Background monitoring service
class MonitoringService:
    def __init__(self, monitor: NewsRAGMonitor, interval_seconds: int = 300):
        self.monitor = monitor
        self.interval_seconds = interval_seconds
        self.running = False
        self.thread = None
        
    def start(self):
        """Start background monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        self.monitor.logger.info("Monitoring service started")
    
    def stop(self):
        """Stop background monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.monitor.logger.info("Monitoring service stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect and store system metrics
                metrics = self.monitor.collect_system_metrics()
                self.monitor.store_system_metrics(metrics)
                
                # Evaluate data quality
                self.monitor.evaluate_data_quality()
                
                self.monitor.logger.info("Monitoring cycle completed")
                
            except Exception as e:
                self.monitor.logger.error(f"Monitoring error: {str(e)}")
            
            # Wait for next cycle
            time.sleep(self.interval_seconds)
