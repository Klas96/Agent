# MCP Extraction Recommendations

This document outlines code that should be extracted to external MCP (Model Context Protocol) servers to improve modularity, maintainability, and separation of concerns.

## Current State

The codebase already has:
- ✅ **MCP Client** (`src/pocketflow/services/mcp_client.py`) - Base MCP client implementation
- ✅ **Libriscribe MCP Client** - For document generation (already partially integrated)
- ✅ **Podcastfy MCP Client** - For podcast generation

## Recommended Extractions

### 1. **Email Service** → Email MCP Server
**Priority: High**

**Current Location:** `src/pocketflow/services/email_service.py`

**Rationale:**
- Email operations (IMAP/SMTP) are external integrations
- Email credentials and connection management should be isolated
- Email operations are I/O-bound and benefit from separate service
- Can be reused across multiple applications

**What to Extract:**
- `fetch_unread_emails()` - IMAP email fetching
- `send_email()` - SMTP email sending
- `mark_as_read()` - Email status updates
- `_parse_email_message()` - Email parsing logic
- Connection management (IMAP/SMTP)

**MCP Server Interface:**
```python
# Tools to expose:
- fetch_unread_emails(folder: str = "INBOX") -> List[EmailData]
- send_email(to: str, subject: str, body: str, attachments: List[str] = None) -> bool
- mark_as_read(email_id: str) -> bool
- search_emails(query: str, folder: str = "INBOX") -> List[EmailData]
```

**Benefits:**
- Centralized email credential management
- Better security isolation
- Easier to support multiple email providers
- Can add email caching/queuing at MCP level

---

### 2. **LLM Service** → LLM MCP Server
**Priority: Medium**

**Current Location:** `src/pocketflow/services/llm_service.py`

**Rationale:**
- Multiple LLM provider integrations (OpenAI, Google, Ollama)
- Provider-specific logic and fallback mechanisms
- Rate limiting and quota management
- Token counting and cost tracking

**What to Extract:**
- `call_llm()` - Main LLM calling interface
- `_call_openai()` - OpenAI API integration
- `_call_ollama()` - Ollama API integration
- `_call_google()` - Google AI integration
- Provider fallback logic
- Token counting and cost estimation

**MCP Server Interface:**
```python
# Tools to expose:
- call_llm(messages: List[Dict], model: str = None, temperature: float = None, max_tokens: int = None) -> str
- list_available_models() -> List[str]
- estimate_cost(messages: List[Dict], model: str) -> Dict[str, Any]
- get_usage_stats() -> Dict[str, Any]
```

**Benefits:**
- Centralized LLM provider management
- Better rate limiting and quota management
- Cost tracking across all applications
- Easier to add new providers
- Can implement caching at MCP level

**Note:** According to PocketFlow principles, LLM calls are "core functions" not utilities. However, the provider integration logic (API calls, fallbacks) can be externalized while keeping the LLM orchestration in nodes.

---

### 3. **Web Search Service** → Web Search MCP Server
**Priority: High**

**Current Location:** `src/pocketflow/services/websearch_service.py`

**Rationale:**
- Currently uses simulated search results
- Real web search requires API keys (Google Search API, Bing, etc.)
- Search result caching and filtering logic
- Should support multiple search providers

**What to Extract:**
- `search()` - Main search interface
- `_perform_search()` - Actual search execution
- `search_with_filters()` - Filtered search
- `_apply_filters()` - Result filtering logic
- Search result caching

**MCP Server Interface:**
```python
# Tools to expose:
- search(query: str, max_results: int = 10) -> List[SearchResult]
- search_with_filters(query: str, filters: Dict) -> List[SearchResult]
- get_search_suggestions(query: str) -> List[str]
```

**Benefits:**
- Centralized search API key management
- Better search result caching
- Support for multiple search providers
- Can add search result ranking/quality filtering

---

### 4. **Vector Service** → Vector Database MCP Server
**Priority: Medium**

**Current Location:** `src/pocketflow/services/vector_service.py`

**Rationale:**
- Vector database operations (embedding storage, similarity search)
- Database-specific logic (FAISS, Pinecone, Weaviate, etc.)
- Embedding model management

**What to Extract:**
- `store_embeddings()` - Store vectors in database
- `search_similar()` - Similarity search
- `delete_embeddings()` - Remove vectors
- Index management operations

**MCP Server Interface:**
```python
# Tools to expose:
- store_embeddings(vectors: List[float], metadata: Dict) -> str
- search_similar(query_vector: List[float], top_k: int = 10) -> List[Dict]
- delete_embeddings(ids: List[str]) -> bool
- create_index(index_name: str, dimension: int) -> bool
```

**Benefits:**
- Centralized vector database management
- Support for multiple vector DB backends
- Better performance optimization
- Can add embedding caching

---

### 5. **Document Service** → Already Using Libriscribe MCP
**Priority: Low** (Already partially extracted)

**Current Location:** `src/pocketflow/services/document_service.py`

**Status:** Already using Libriscribe MCP Server for document generation. Internal fallback exists.

**Recommendation:**
- Keep internal fallback for reliability
- Consider extracting LaTeX template management to MCP
- Move template rendering logic to MCP server

---

## Services to Keep Internal

### **Database Service**
**Location:** `src/pocketflow/services/database_service.py`

**Rationale:**
- SQLite database is application-specific
- User data and application state
- Should remain tightly coupled with application logic
- Not a good candidate for external service

### **Content Service**
**Location:** `src/pocketflow/services/content_service.py`

**Rationale:**
- Orchestrates multiple services (LLM, Document, etc.)
- Contains business logic specific to PocketFlow
- Coordinates between services - should stay internal

### **Conversation Service**
**Location:** `src/pocketflow/services/conversation_service.py`

**Rationale:**
- Manages conversation state and threading
- Application-specific business logic
- Tightly coupled with email processing flows

---

## Implementation Strategy

### Phase 1: High Priority (Immediate)
1. **Email MCP Server** - Extract email operations
2. **Web Search MCP Server** - Replace simulated search with real implementation

### Phase 2: Medium Priority (Next)
3. **LLM MCP Server** - Extract LLM provider integrations
4. **Vector Database MCP Server** - Extract vector operations

### Phase 3: Optimization
5. Enhance existing MCP clients (Libriscribe, Podcastfy)
6. Add monitoring and observability to MCP servers

---

## Migration Pattern

For each service extraction:

1. **Create MCP Server** (separate repository/service)
   - Implement MCP protocol
   - Expose tools via MCP interface
   - Handle authentication and configuration

2. **Update Service Class**
   ```python
   class EmailService:
       def __init__(self):
           self.mcp_client = EmailMCPClient()
       
       def fetch_unread_emails(self):
           return self.mcp_client.call_tool("fetch_unread_emails")
   ```

3. **Add Fallback Logic**
   - Keep internal implementation as fallback
   - Gracefully degrade if MCP server unavailable

4. **Update Configuration**
   - Add MCP server URLs to settings
   - Add health check endpoints

5. **Update Tests**
   - Mock MCP client in tests
   - Test fallback behavior

---

## Benefits Summary

1. **Separation of Concerns**: External integrations isolated from core logic
2. **Reusability**: MCP servers can be used by multiple applications
3. **Security**: Credentials and API keys isolated in MCP servers
4. **Maintainability**: Easier to update external integrations independently
5. **Scalability**: MCP servers can be scaled independently
6. **Testing**: Easier to mock and test with MCP abstraction
7. **Flexibility**: Can swap implementations without changing core code

---

## References

- [PocketFlow Utility Functions Documentation](.cursor/rules/utility_function/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- Current MCP Client Implementation: `src/pocketflow/services/mcp_client.py`
