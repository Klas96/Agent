# PocketFlow Architecture Diagram

## Complete System Architecture

```mermaid
graph TB
    %% User Interface Layer
    subgraph "User Interface"
        UI[Email Client]
        API[API Endpoints]
    end

    %% Main Application Layer
    subgraph "PocketFlow Core"
        FM[Flow Manager]
        AR[Auto Router]
        PM[Performance Monitor]
    end

    %% Flow Layer
    subgraph "Flow Engine"
        EPF[Email Processor Flow]
        TUF[Tokenless User Flow]
        CGF[Content Generation Flow]
        IF[Investigation Flow]
        PPF[Payment Processing Flow]
    end

    %% Node Layer
    subgraph "Node System"
        subgraph "Email Nodes"
            FEN[Fetch Email Node]
            SEN[Send Email Node]
            CCN[Conversation Context Node]
        end
        
        subgraph "Agent Nodes"
            AN[Agent Node]
            PAN[Pop Agent Action Node]
        end
        
        subgraph "Content Nodes"
            CCN[Content Creator Node]
            CPN[Content Param Node]
            GCN[Generate Content Node]
        end
        
        subgraph "Investigation Nodes"
            ITN[Investigate Topic Node]
        end
        
        subgraph "Bitcoin Nodes"
            PTBN[Purchase Tokens Bitcoin Node]
        end
    end

    %% Service Layer
    subgraph "Service Layer"
        ES[Email Service]
        LS[LLM Service]
        CS[Content Service]
        BS[Bitcoin Service]
        WS[Web Search Service]
    end

    %% External Services
    subgraph "External Services"
        GMAIL[Gmail IMAP/SMTP]
        OPENAI[OpenAI API]
        GOOGLE[Google AI]
        BTC[Bitcoin Network]
        WEB[Web Search APIs]
    end

    %% Configuration & Utils
    subgraph "Configuration & Utils"
        CONFIG[Configuration Manager]
        LOG[Logging System]
        ERR[Error Handler]
        VAL[Validation]
        PERF[Performance Monitor]
    end

    %% Data Flow
    UI --> FM
    API --> FM
    
    FM --> AR
    AR --> EPF
    AR --> TUF
    AR --> CGF
    AR --> IF
    AR --> PPF
    
    EPF --> FEN
    EPF --> SEN
    EPF --> CCN
    EPF --> AN
    EPF --> PAN
    EPF --> CCN
    EPF --> CPN
    EPF --> GCN
    EPF --> ITN
    
    TUF --> PTBN
    TUF --> SEN
    
    CGF --> CCN
    CGF --> CPN
    CGF --> GCN
    CGF --> SEN
    
    IF --> ITN
    IF --> SEN
    
    PPF --> PTBN
    PPF --> SEN
    
    %% Node to Service connections
    FEN --> ES
    SEN --> ES
    CCN --> ES
    AN --> LS
    PAN --> LS
    CCN --> CS
    CPN --> CS
    GCN --> CS
    ITN --> WS
    PTBN --> BS
    
    %% Service to External connections
    ES --> GMAIL
    LS --> OPENAI
    LS --> GOOGLE
    CS --> OPENAI
    CS --> GOOGLE
    BS --> BTC
    WS --> WEB
    
    %% Configuration connections
    FM --> CONFIG
    ES --> CONFIG
    LS --> CONFIG
    CS --> CONFIG
    BS --> CONFIG
    WS --> CONFIG
    
    %% Monitoring connections
    FM --> PM
    EPF --> PERF
    TUF --> PERF
    CGF --> PERF
    IF --> PERF
    PPF --> PERF
    
    %% Error handling
    FM --> ERR
    EPF --> ERR
    TUF --> ERR
    CGF --> ERR
    IF --> ERR
    PPF --> ERR
    
    %% Logging
    FM --> LOG
    EPF --> LOG
    TUF --> LOG
    CGF --> LOG
    IF --> LOG
    PPF --> LOG

    %% Styling
    classDef flowClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef nodeClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef externalClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef utilClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class EPF,TUF,CGF,IF,PPF flowClass
    class FEN,SEN,CCN,AN,PAN,CCN,CPN,GCN,ITN,PTBN nodeClass
    class ES,LS,CS,BS,WS serviceClass
    class GMAIL,OPENAI,GOOGLE,BTC,WEB externalClass
    class CONFIG,LOG,ERR,VAL,PERF utilClass
```

## Flow Selection Logic

```mermaid
flowchart TD
    START([Email Received]) --> CHECK_USER{Check User Type}
    
    CHECK_USER -->|Tokenless User| TOKENLESS[Tokenless User Flow]
    CHECK_USER -->|Tokened User| ANALYZE{Analyze Email Content}
    
    ANALYZE -->|Contains 'generate'| CONTENT[Content Generation Flow]
    ANALYZE -->|Contains 'create'| CONTENT
    ANALYZE -->|Contains 'research'| INVESTIGATE[Investigation Flow]
    ANALYZE -->|Contains 'investigate'| INVESTIGATE
    ANALYZE -->|Contains 'payment'| PAYMENT[Payment Processing Flow]
    ANALYZE -->|Contains 'purchase'| PAYMENT
    ANALYZE -->|Default| EMAIL_PROCESS[Email Processor Flow]
    
    TOKENLESS --> PAYMENT_REQUEST[Send Payment Request]
    CONTENT --> CONTENT_GEN[Generate Content]
    INVESTIGATE --> WEB_SEARCH[Web Search & Summarize]
    PAYMENT --> BTC_PAYMENT[Process Bitcoin Payment]
    EMAIL_PROCESS --> FULL_PROCESS[Full Email Processing]
    
    PAYMENT_REQUEST --> END([Complete])
    CONTENT_GEN --> END
    WEB_SEARCH --> END
    BTC_PAYMENT --> END
    FULL_PROCESS --> END
```

## Node Processing Pipeline

```mermaid
sequenceDiagram
    participant FM as Flow Manager
    participant FEN as Fetch Email Node
    participant CCN as Conversation Context Node
    participant AN as Agent Node
    participant PAN as Pop Agent Action Node
    participant CCN as Content Creator Node
    participant CPN as Content Param Node
    participant GCN as Generate Content Node
    participant SEN as Send Email Node
    participant ES as Email Service
    participant LS as LLM Service
    participant CS as Content Service

    FM->>FEN: Process email
    FEN->>ES: Fetch unread emails
    ES-->>FEN: Email data
    FEN-->>FM: Email processed

    FM->>CCN: Get conversation context
    CCN->>ES: Retrieve conversation history
    ES-->>CCN: Context data
    CCN-->>FM: Context ready

    FM->>AN: Process with agent
    AN->>LS: Call LLM with context
    LS-->>AN: Agent response
    AN-->>FM: Actions extracted

    FM->>PAN: Get next action
    PAN-->>FM: Action details

    FM->>CCN: Determine content type
    CCN-->>FM: Content type identified

    FM->>CPN: Prepare parameters
    CPN-->>FM: Parameters ready

    FM->>GCN: Generate content
    GCN->>CS: Generate content
    CS-->>GCN: Generated file
    GCN-->>FM: Content generated

    FM->>SEN: Send response
    SEN->>ES: Send email with attachment
    ES-->>SEN: Email sent
    SEN-->>FM: Response sent

    FM-->>FM: Flow complete
```

## Service Integration Architecture

```mermaid
graph LR
    subgraph "PocketFlow Application"
        NODES[Nodes]
        FLOWS[Flows]
        CORE[Core Engine]
    end

    subgraph "Service Layer"
        ES[Email Service]
        LS[LLM Service]
        CS[Content Service]
        BS[Bitcoin Service]
        WS[Web Search Service]
    end

    subgraph "External APIs"
        GMAIL[Gmail API]
        OPENAI[OpenAI API]
        GOOGLE[Google AI]
        BTC[Bitcoin Network]
        SEARCH[Search APIs]
    end

    NODES --> ES
    NODES --> LS
    NODES --> CS
    NODES --> BS
    NODES --> WS

    FLOWS --> NODES
    CORE --> FLOWS

    ES --> GMAIL
    LS --> OPENAI
    LS --> GOOGLE
    CS --> OPENAI
    CS --> GOOGLE
    BS --> BTC
    WS --> SEARCH

    classDef appClass fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef serviceClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef apiClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class NODES,FLOWS,CORE appClass
    class ES,LS,CS,BS,WS serviceClass
    class GMAIL,OPENAI,GOOGLE,BTC,SEARCH apiClass
```

## Performance Monitoring Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        FLOWS[Flows]
        NODES[Nodes]
        SERVICES[Services]
    end

    subgraph "Performance Monitoring"
        PM[Performance Monitor]
        METRICS[Metrics Collection]
        TIMERS[Timer Management]
        STATS[Statistics Engine]
    end

    subgraph "Monitoring Output"
        LOGS[Log Files]
        DASHBOARD[Performance Dashboard]
        ALERTS[Performance Alerts]
    end

    FLOWS --> PM
    NODES --> PM
    SERVICES --> PM

    PM --> METRICS
    PM --> TIMERS
    PM --> STATS

    METRICS --> LOGS
    STATS --> DASHBOARD
    STATS --> ALERTS

    classDef appClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef monitorClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef outputClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px

    class FLOWS,NODES,SERVICES appClass
    class PM,METRICS,TIMERS,STATS monitorClass
    class LOGS,DASHBOARD,ALERTS outputClass
```

## Error Handling Flow

```mermaid
flowchart TD
    START([Operation Start]) --> TRY{Try Operation}
    
    TRY -->|Success| SUCCESS([Operation Success])
    TRY -->|Failure| CATCH{Catch Error Type}
    
    CATCH -->|Email Error| EMAIL_ERR[Email Error Handler]
    CATCH -->|LLM Error| LLM_ERR[LLM Error Handler]
    CATCH -->|Content Error| CONTENT_ERR[Content Error Handler]
    CATCH -->|Bitcoin Error| BTC_ERR[Bitcoin Error Handler]
    CATCH -->|Web Search Error| WEB_ERR[Web Search Error Handler]
    CATCH -->|General Error| GEN_ERR[General Error Handler]
    
    EMAIL_ERR --> RETRY{Retry Logic}
    LLM_ERR --> RETRY
    CONTENT_ERR --> RETRY
    BTC_ERR --> RETRY
    WEB_ERR --> RETRY
    GEN_ERR --> RETRY
    
    RETRY -->|Retry Success| SUCCESS
    RETRY -->|Retry Failed| FALLBACK{Fallback Available}
    
    FALLBACK -->|Yes| FALLBACK_OP[Execute Fallback]
    FALLBACK -->|No| ERROR_LOG[Log Error]
    
    FALLBACK_OP --> SUCCESS
    ERROR_LOG --> FAILURE([Operation Failed])
    
    SUCCESS --> END([Complete])
    FAILURE --> END
```

## Configuration Management

```mermaid
graph TB
    subgraph "Configuration Sources"
        ENV[Environment Variables]
        YAML[YAML Files]
        DEFAULT[Default Values]
    end

    subgraph "Configuration Manager"
        LOADER[Config Loader]
        VALIDATOR[Config Validator]
        MERGER[Config Merger]
    end

    subgraph "Application Components"
        FLOWS[Flows]
        NODES[Nodes]
        SERVICES[Services]
        UTILS[Utilities]
    end

    ENV --> LOADER
    YAML --> LOADER
    DEFAULT --> LOADER

    LOADER --> VALIDATOR
    VALIDATOR --> MERGER
    MERGER --> CONFIG[Final Config]

    CONFIG --> FLOWS
    CONFIG --> NODES
    CONFIG --> SERVICES
    CONFIG --> UTILS

    classDef sourceClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef managerClass fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef componentClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class ENV,YAML,DEFAULT sourceClass
    class LOADER,VALIDATOR,MERGER,CONFIG managerClass
    class FLOWS,NODES,SERVICES,UTILS componentClass
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Layer"
        EMAIL[Email Input]
        API[API Requests]
        WEBHOOK[Webhooks]
    end

    subgraph "Processing Layer"
        SHARED[Shared State]
        FLOW[Flow Engine]
        NODES[Node System]
    end

    subgraph "Service Layer"
        EMAIL_SVC[Email Service]
        LLM_SVC[LLM Service]
        CONTENT_SVC[Content Service]
        BTC_SVC[Bitcoin Service]
        SEARCH_SVC[Search Service]
    end

    subgraph "Output Layer"
        RESPONSE[Email Response]
        ATTACHMENT[File Attachments]
        PAYMENT[Payment Info]
        LOGS[System Logs]
    end

    EMAIL --> SHARED
    API --> SHARED
    WEBHOOK --> SHARED

    SHARED --> FLOW
    FLOW --> NODES

    NODES --> EMAIL_SVC
    NODES --> LLM_SVC
    NODES --> CONTENT_SVC
    NODES --> BTC_SVC
    NODES --> SEARCH_SVC

    EMAIL_SVC --> RESPONSE
    CONTENT_SVC --> ATTACHMENT
    BTC_SVC --> PAYMENT
    NODES --> LOGS

    classDef inputClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef processClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef serviceClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef outputClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class EMAIL,API,WEBHOOK inputClass
    class SHARED,FLOW,NODES processClass
    class EMAIL_SVC,LLM_SVC,CONTENT_SVC,BTC_SVC,SEARCH_SVC serviceClass
    class RESPONSE,ATTACHMENT,PAYMENT,LOGS outputClass
```

## Component Relationships

```mermaid
graph TD
    subgraph "Core Components"
        CORE[Core Engine]
        TYPES[Type System]
        CONFIG[Configuration]
    end

    subgraph "Flow System"
        FM[Flow Manager]
        AR[Auto Router]
        FLOWS[Production Flows]
    end

    subgraph "Node System"
        NODES[Modular Nodes]
        SERVICES[Service Layer]
    end

    subgraph "External Integrations"
        EMAIL[Email APIs]
        LLM[LLM APIs]
        CONTENT[Content APIs]
        BTC[Bitcoin APIs]
        SEARCH[Search APIs]
    end

    subgraph "Utilities"
        LOG[Logging]
        ERR[Error Handling]
        PERF[Performance]
        VAL[Validation]
    end

    CORE --> FM
    TYPES --> FLOWS
    CONFIG --> SERVICES

    FM --> AR
    AR --> FLOWS
    FLOWS --> NODES

    NODES --> SERVICES
    SERVICES --> EMAIL
    SERVICES --> LLM
    SERVICES --> CONTENT
    SERVICES --> BTC
    SERVICES --> SEARCH

    CORE --> LOG
    FLOWS --> ERR
    NODES --> PERF
    SERVICES --> VAL

    classDef coreClass fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef flowClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef nodeClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef externalClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef utilClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class CORE,TYPES,CONFIG coreClass
    class FM,AR,FLOWS flowClass
    class NODES,SERVICES nodeClass
    class EMAIL,LLM,CONTENT,BTC,SEARCH externalClass
    class LOG,ERR,PERF,VAL utilClass
```

This comprehensive set of Mermaid diagrams shows the complete PocketFlow architecture after the refactor, including:

1. **Complete System Architecture** - Overall system structure
2. **Flow Selection Logic** - How flows are automatically selected
3. **Node Processing Pipeline** - Sequence of node execution
4. **Service Integration Architecture** - How services connect to external APIs
5. **Performance Monitoring Architecture** - How performance is tracked
6. **Error Handling Flow** - Error handling and recovery
7. **Configuration Management** - How configuration is managed
8. **Data Flow Architecture** - How data flows through the system
9. **Component Relationships** - How all components relate to each other

The diagrams illustrate the modular, scalable, and production-ready architecture that has been achieved through the refactor! 