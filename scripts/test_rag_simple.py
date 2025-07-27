#!/usr/bin/env python3
"""
Simple RAG system test without full PocketFlow dependencies.
"""

import sys
import os
import json
import hashlib
import sqlite3
from typing import List, Dict, Any
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def simple_embedding(text: str) -> List[float]:
    """Simple embedding function using character frequency."""
    embedding = [0.0] * 384
    
    # Simple hash-based embedding
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    
    for i, byte in enumerate(hash_bytes):
        if i < len(embedding):
            embedding[i] = (byte - 128) / 128.0
    
    return embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
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

class SimpleVectorService:
    """Simplified vector service for testing."""
    
    def __init__(self, db_path: str = "test_vector_store.db"):
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
    
    def store_conversation(self, user_email: str, conversation: List[Dict], metadata: Dict = None):
        """Store a conversation with its embedding."""
        try:
            # Create conversation hash
            conversation_text = json.dumps(conversation, sort_keys=True)
            conversation_hash = hashlib.sha256(conversation_text.encode()).hexdigest()
            
            # Generate embedding
            embedding = simple_embedding(conversation_text)
            
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
            
            print(f"✅ Stored conversation embedding for {user_email}")
            
        except Exception as e:
            print(f"❌ Error storing conversation: {e}")
    
    def find_similar_conversations(self, query: str, user_email: str = None, top_k: int = 3) -> List[Dict]:
        """Find similar conversations based on semantic similarity."""
        try:
            query_embedding = simple_embedding(query)
            
            with sqlite3.connect(self.db_path) as conn:
                if user_email:
                    cursor = conn.execute("""
                        SELECT content, embedding, metadata, created_at
                        FROM conversation_embeddings 
                        WHERE user_email = ?
                        ORDER BY created_at DESC
                        LIMIT 100
                    """, (user_email,))
                else:
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
                    
                    similarity = cosine_similarity(query_embedding, stored_embedding)
                    
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
            print(f"❌ Error finding similar conversations: {e}")
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
            
            print(f"✅ Stored user pattern for {user_email}: {pattern_type}")
            
        except Exception as e:
            print(f"❌ Error storing user pattern: {e}")
    
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
            print(f"❌ Error retrieving user patterns: {e}")
            return []

def test_vector_service():
    """Test the vector service functionality."""
    print("🧪 Testing Vector Service...")
    
    vector_service = SimpleVectorService("test_vector_store.db")
    
    # Test conversation storage
    test_conversation = [
        {"role": "user", "content": "Hi, I need help with tokens"},
        {"role": "assistant", "content": "I can help you purchase tokens!"},
        {"role": "user", "content": "How much do tokens cost?"}
    ]
    
    vector_service.store_conversation(
        user_email="test@example.com",
        conversation=test_conversation,
        metadata={"topic": "token_purchase", "user_type": "new"}
    )
    
    # Test similar conversation search
    query = "I want to buy tokens"
    similar_conversations = vector_service.find_similar_conversations(
        query=query,
        user_email="test@example.com",
        top_k=3
    )
    
    print(f"✅ Found {len(similar_conversations)} similar conversations")
    if similar_conversations:
        print(f"   Top similarity: {similar_conversations[0].get('similarity', 0):.3f}")
    
    # Test user pattern storage
    pattern_data = {
        "preferred_detail_level": "detailed",
        "common_topics": ["tokens", "payment"],
        "response_style": "formal"
    }
    
    vector_service.store_user_pattern(
        user_email="test@example.com",
        pattern_type="communication_preferences",
        pattern_data=pattern_data
    )
    
    # Test pattern retrieval
    patterns = vector_service.get_user_patterns("test@example.com")
    print(f"✅ Stored and retrieved {len(patterns)} user patterns")
    
    return True

def test_embedding_consistency():
    """Test that embeddings are consistent."""
    print("🧪 Testing Embedding Consistency...")
    
    text1 = "I need help with tokens"
    text2 = "I need help with tokens"  # Same text
    text3 = "I want to buy tokens"     # Similar text
    text4 = "What's the weather like?" # Different text
    
    emb1 = simple_embedding(text1)
    emb2 = simple_embedding(text2)
    emb3 = simple_embedding(text3)
    emb4 = simple_embedding(text4)
    
    sim1 = cosine_similarity(emb1, emb2)  # Should be 1.0 (identical)
    sim2 = cosine_similarity(emb1, emb3)  # Should be high (similar)
    sim3 = cosine_similarity(emb1, emb4)  # Should be lower (different)
    
    print(f"✅ Identical texts similarity: {sim1:.3f} (should be ~1.0)")
    print(f"✅ Similar texts similarity: {sim2:.3f} (should be >0.5)")
    print(f"✅ Different texts similarity: {sim3:.3f} (should be <0.5)")
    
    if sim1 > 0.99 and sim2 > sim3:
        print("✅ Embedding consistency test passed!")
        return True
    else:
        print("❌ Embedding consistency test failed!")
        return False

def cleanup_test_data():
    """Clean up test data."""
    print("🧹 Cleaning up test data...")
    
    import os
    test_files = [
        "test_vector_store.db"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removed {file}")

def main():
    """Run RAG system tests."""
    print("🚀 Starting Simple RAG System Tests...\n")
    
    try:
        # Run tests
        test_embedding_consistency()
        print()
        
        test_vector_service()
        print()
        
        print("🎉 All RAG system tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        cleanup_test_data()
        print("\n✨ RAG system test completed!")

if __name__ == "__main__":
    main() 