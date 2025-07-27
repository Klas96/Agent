"""
Vector database service for PocketFlow RAG system.

This service handles semantic search, conversation embeddings, and vector storage.
"""

import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import sqlite3
from ..utils.logging import get_logger

logger = get_logger("VectorService")

class VectorService:
    """Service for managing vector embeddings and semantic search."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use a writable location in production
            import os
            if os.path.exists("/opt/pocketflow"):
                # Production environment
                self.db_path = "/opt/pocketflow/data/vector_store.db"
                # Ensure directory exists
                os.makedirs("/opt/pocketflow/data", exist_ok=True)
            else:
                # Development environment
                self.db_path = "vector_store.db"
        else:
            self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the vector database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    conversation_hash TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_email ON conversation_embeddings(user_email)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_hash ON conversation_embeddings(conversation_hash)
            """)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Simple embedding function using character frequency.
        In production, replace with proper embedding model.
        """
        # Simple character-based embedding for demo
        # In real implementation, use sentence-transformers or OpenAI embeddings
        embedding = [0.0] * 384  # Standard embedding size
        
        # Simple hash-based embedding
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        for i, byte in enumerate(hash_bytes):
            if i < len(embedding):
                embedding[i] = (byte - 128) / 128.0
        
        return embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors without numpy."""
        if len(vec1) != len(vec2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def store_conversation(self, user_email: str, conversation: List[Dict], metadata: Dict = None):
        """Store a conversation with its embedding."""
        try:
            # Create conversation hash
            conversation_text = json.dumps(conversation, sort_keys=True)
            conversation_hash = hashlib.sha256(conversation_text.encode()).hexdigest()
            
            # Generate embedding
            embedding = self._simple_embedding(conversation_text)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO conversation_embeddings 
                    (user_email, conversation_hash, content, embedding, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_email,
                    conversation_hash,
                    conversation_text,
                    json.dumps(embedding),
                    json.dumps(metadata) if metadata else None
                ))
            
            logger.info(f"Stored conversation embedding for {user_email}")
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
    
    def find_similar_conversations(self, query: str, user_email: str = None, top_k: int = 3) -> List[Dict]:
        """Find similar conversations based on semantic similarity."""
        try:
            query_embedding = self._simple_embedding(query)
            
            with sqlite3.connect(self.db_path) as conn:
                if user_email:
                    # Search within user's conversations
                    cursor = conn.execute("""
                        SELECT content, embedding, metadata, created_at
                        FROM conversation_embeddings 
                        WHERE user_email = ?
                        ORDER BY created_at DESC
                        LIMIT 100
                    """, (user_email,))
                else:
                    # Search all conversations
                    cursor = conn.execute("""
                        SELECT content, embedding, metadata, created_at
                        FROM conversation_embeddings 
                        ORDER BY created_at DESC
                        LIMIT 100
                    """)
                
                results = []
                for row in cursor.fetchall():
                    content, embedding_str, metadata_str, created_at = row
                    stored_embedding = json.loads(embedding_str)
                    
                    similarity = self._cosine_similarity(query_embedding, stored_embedding)
                    
                    results.append({
                        'content': json.loads(content),
                        'similarity': similarity,
                        'metadata': json.loads(metadata_str) if metadata_str else {},
                        'created_at': created_at
                    })
                
                # Sort by similarity and return top_k
                results.sort(key=lambda x: x['similarity'], reverse=True)
                return results[:top_k]
                
        except Exception as e:
            logger.error(f"Error finding similar conversations: {e}")
            return []
    
    def store_user_pattern(self, user_email: str, pattern_type: str, pattern_data: Dict):
        """Store user behavior patterns."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO user_patterns (user_email, pattern_type, pattern_data)
                    VALUES (?, ?, ?)
                """, (
                    user_email,
                    pattern_type,
                    json.dumps(pattern_data)
                ))
            
            logger.info(f"Stored user pattern for {user_email}: {pattern_type}")
            
        except Exception as e:
            logger.error(f"Error storing user pattern: {e}")
    
    def get_user_patterns(self, user_email: str, pattern_type: str = None) -> List[Dict]:
        """Retrieve user behavior patterns."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if pattern_type:
                    cursor = conn.execute("""
                        SELECT pattern_type, pattern_data, confidence, created_at
                        FROM user_patterns 
                        WHERE user_email = ? AND pattern_type = ?
                        ORDER BY created_at DESC
                    """, (user_email, pattern_type))
                else:
                    cursor = conn.execute("""
                        SELECT pattern_type, pattern_data, confidence, created_at
                        FROM user_patterns 
                        WHERE user_email = ?
                        ORDER BY created_at DESC
                    """, (user_email,))
                
                results = []
                for row in cursor.fetchall():
                    pattern_type, pattern_data_str, confidence, created_at = row
                    results.append({
                        'pattern_type': pattern_type,
                        'pattern_data': json.loads(pattern_data_str),
                        'confidence': confidence,
                        'created_at': created_at
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Error retrieving user patterns: {e}")
            return [] 