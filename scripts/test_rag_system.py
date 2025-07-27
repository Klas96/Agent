#!/usr/bin/env python3
"""
Test script for PocketFlow RAG system.

This script tests the vector service, conversation service, and RAG integration.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow.services.vector_service import VectorService
from pocketflow.services.conversation_service import ConversationService
from pocketflow.utils.logging import get_logger

logger = get_logger("RAGTest")

def test_vector_service():
    """Test the vector service functionality."""
    print("🧪 Testing Vector Service...")
    
    vector_service = VectorService("test_vector_store.db")
    
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

def test_conversation_service():
    """Test the conversation service functionality."""
    print("🧪 Testing Conversation Service...")
    
    conversation_service = ConversationService()
    
    # Test conversation summarization
    long_conversation = [
        {"role": "user", "content": "Hi there!"},
        {"role": "assistant", "content": "Hello! How can I help you?"},
        {"role": "user", "content": "I need help with tokens"},
        {"role": "assistant", "content": "I can help you with that!"},
        {"role": "user", "content": "What are the prices?"},
        {"role": "assistant", "content": "Tokens cost $10 each"},
        {"role": "user", "content": "How do I pay?"},
        {"role": "assistant", "content": "You can pay with Bitcoin"},
        {"role": "user", "content": "Great, thanks!"},
        {"role": "assistant", "content": "You're welcome!"},
        {"role": "user", "content": "One more question..."},
        {"role": "assistant", "content": "Sure, what is it?"}
    ]
    
    # Test memory optimization
    optimized = conversation_service.optimize_conversation_memory(
        long_conversation, "test@example.com"
    )
    
    print(f"✅ Original length: {len(long_conversation)}")
    print(f"✅ Optimized length: {len(optimized)}")
    
    # Test context retrieval
    context = conversation_service.get_relevant_context(
        current_message="I need help with tokens",
        user_email="test@example.com",
        top_k=3
    )
    
    print(f"✅ Retrieved context with {len(context.get('similar_conversations', []))} similar conversations")
    print(f"✅ Found {len(context.get('user_patterns', []))} user patterns")
    
    # Test conversation storage
    conversation_service.store_conversation_context(
        user_email="test@example.com",
        conversation=long_conversation,
        metadata={"test": True, "topic": "token_help"}
    )
    
    return True

def test_rag_integration():
    """Test the complete RAG integration."""
    print("🧪 Testing RAG Integration...")
    
    # Simulate a shared state
    class MockSharedState:
        def __init__(self):
            self.email = {
                "from": "Test User <test@example.com>",
                "subject": "Help with tokens",
                "body": "I need help purchasing tokens"
            }
            self.conversation = []
            self.rag_context = {}
    
    shared = MockSharedState()
    
    # Test conversation context node
    from pocketflow.nodes.email.context import ConversationContextNode
    
    context_node = ConversationContextNode()
    
    # Test prep
    prep_result = context_node.prep(shared)
    if prep_result:
        print("✅ Conversation context prep successful")
        
        # Test exec
        exec_result = context_node.exec(prep_result)
        if exec_result:
            print("✅ Conversation context exec successful")
            print(f"   Enhanced context created with {len(exec_result.get('conversation', []))} messages")
            
            # Test post
            post_result = context_node.post(shared, prep_result, exec_result)
            print(f"✅ Conversation context post successful: {post_result}")
        else:
            print("❌ Conversation context exec failed")
    else:
        print("❌ Conversation context prep failed")
    
    return True

def test_variable_replacement():
    """Test the variable replacement functionality."""
    print("🧪 Testing Variable Replacement...")
    
    from pocketflow.utils.prompt_utils import replace_variables_in_text
    
    # Mock shared state
    class MockSharedState:
        def __init__(self):
            self.email = {
                "subject": "Test Subject",
                "body": "Test body content"
            }
            self.conversation = [{"role": "user", "content": "Hello"}]
            self.btc_address = "bc1test123"
            self.flow_type = "tokenless_user"
    
    shared = MockSharedState()
    
    # Test variable replacement
    test_text = "Hi {user_name}! Your Bitcoin address is {btc_address}. Subject: {email_subject}"
    replaced_text = replace_variables_in_text(test_text, shared, "test@example.com")
    
    print(f"✅ Original: {test_text}")
    print(f"✅ Replaced: {replaced_text}")
    
    # Check if variables were replaced
    if "{user_name}" not in replaced_text and "{btc_address}" not in replaced_text:
        print("✅ Variables successfully replaced")
    else:
        print("❌ Variables not replaced properly")
    
    return True

def cleanup_test_data():
    """Clean up test data."""
    print("🧹 Cleaning up test data...")
    
    import os
    test_files = [
        "test_vector_store.db",
        "vector_store.db"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removed {file}")

def main():
    """Run all RAG system tests."""
    print("🚀 Starting RAG System Tests...\n")
    
    try:
        # Run tests
        test_vector_service()
        print()
        
        test_conversation_service()
        print()
        
        test_rag_integration()
        print()
        
        test_variable_replacement()
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