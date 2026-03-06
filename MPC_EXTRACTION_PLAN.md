# MPC Extraction Plan - Files to Remove/Move

This document lists all files that should be removed or moved to separate MPC processes as part of the Email + LLM core refactoring.

## ✅ Completed

1. ✅ Created MPCManager in `src/pocketflow/services/mcp_client.py`
2. ✅ Created MPC wrapper nodes in `src/pocketflow/nodes/mpc/`
3. ✅ Updated email processor flow to use MPC nodes
4. ✅ Updated services __init__.py to remove deprecated services

## 📋 Files to Remove (Content Generation)

### Services
- `src/pocketflow/services/content_service.py` → Move to Content-MPC
- `src/pocketflow/services/document_service.py` → Move to Content-MPC

### Nodes
- `src/pocketflow/nodes/content/` (entire directory) → Move to Content-MPC
  - `creator.py`
  - `generator.py`
  - `params.py`
  - `document_generator.py`

### Flows
- `src/pocketflow/flows/content_generation.py` → Remove (use email_processor with MPC)

### Agents
- `src/pocketflow/agents/content_agent.py` → Move to Content-MPC

## 📋 Files to Remove (Research/Investigation)

### Services
- `src/pocketflow/services/websearch_service.py` → Move to Research-MPC
- `src/pocketflow/services/vector_service.py` → Move to Research-MPC (if used)

### Nodes
- `src/pocketflow/nodes/investigation/` (entire directory) → Move to Research-MPC
  - `topic.py`

### Flows
- `src/pocketflow/flows/investigation.py` → Remove (use email_processor with MPC)
- `src/pocketflow/flows/research_and_generate.py` → Remove

### Agents
- `src/pocketflow/agents/research_agent.py` → Move to Research-MPC
- `src/pocketflow/agents/llm_enhanced_research_agent.py` → Move to Research-MPC

## 📋 Files to Remove (Tools)

### Tools (keep only email_tools.py if needed)
- `src/pocketflow/tools/calculator.py` → Move to Tools-MPC
- `src/pocketflow/tools/file_operations.py` → Move to Tools-MPC
- `src/pocketflow/tools/weather.py` → Move to Tools-MPC
- `src/pocketflow/tools/web_search.py` → Move to Tools-MPC (or Research-MPC)
- `src/pocketflow/tools/polymarket.py` → Move to Tools-MPC
- `src/pocketflow/tools/database.py` → Keep (used by core)
- `src/pocketflow/tools/email_tools.py` → Keep (used by core)
- `src/pocketflow/tools/mcp_tools.py` → Keep (MPC integration)

## 📋 Files to Remove (Bitcoin/Payment)

### Services
- `src/pocketflow/services/deprecated-donation/` (entire directory) → Already in Bitcoin-MPC

### Utils
- `src/pocketflow/utils/electrum_utils.py` → Already in Bitcoin-MPC
- `src/pocketflow/utils/simple_bitcoin_utils.py` → Already in Bitcoin-MPC

### Nodes
- `src/pocketflow/nodes/deprecated-donation/` (entire directory) → Already in Bitcoin-MPC

## 📋 Files to Update

### Flow Manager
- `src/pocketflow/flows/manager.py` → Remove content_generation flow reference

### Imports
- Update all files that import removed services/nodes
- Replace direct service calls with MPC calls

## 🎯 Next Steps

1. **Phase 1**: Remove content generation files (Content-MPC)
2. **Phase 2**: Remove research/investigation files (Research-MPC)
3. **Phase 3**: Remove tools files (Tools-MPC)
4. **Phase 4**: Update all imports and dependencies
5. **Phase 5**: Update flow manager to remove deprecated flows
6. **Phase 6**: Test email processor flow with MPC nodes

## 📝 Notes

- Keep `src/pocketflow/tools/registry.py` and `base.py` as they may be needed for MPC tool registration
- Keep `src/pocketflow/nodes/agent/` as it's core to LLM functionality
- All MPC processes should expose HTTP/gRPC APIs
- MPC processes should be started separately and communicate via the MPCManager
