# Locust Data Flow

This document describes how data flows through the Locust system during test execution, focusing on request data, statistics, and events.

## Request and Response Flow

```mermaid
flowchart TD
    User[User Task] -->|Makes Request| HttpClient[HTTP Client]
    HttpClient -->|Sends Request| Target[Target System]
    Target -->|Returns Response| HttpClient
    HttpClient -->|Captures Metrics| Events[Event System]
    Events -->|Fires Events| Stats[Statistics]
    Events -->|Notifies| Listeners[Event Listeners]
    
    Stats -->|Updates| Metrics[Metrics Collection]
    Stats -->|Reports to| WebUI[Web UI]
    Stats -->|Writes to| CSV[CSV Export]
    
    Listeners -->|Custom Processing| UserCode[User Code]
    Listeners -->|Custom Reporting| ExternalSystems[External Systems]
```

## Statistics Data Structure

```mermaid
classDiagram
    class RequestStats {
        +entries: dict
        +errors: dict
        +total: StatsEntry
        +start_time: int
        +reset_all()
        +log_request()
        +log_error()
        +get_statistics()
    }
    
    class StatsEntry {
        +name: str
        +method: str
        +num_requests: int
        +num_failures: int
        +total_response_time: int
        +min_response_time: int
        +max_response_time: int
        +response_times: dict
        +reset()
        +log()
        +get_response_time_percentile()
        +serialize()
    }
    
    class StatsError {
        +name: str
        +method: str
        +error: str
        +occurrences: int
    }
    
    RequestStats --> "many" StatsEntry: contains
    RequestStats --> "many" StatsError: tracks
```

## Event System Data Flow

The event system is a core part of Locust, enabling communication between components and allowing for extensions.

```mermaid
flowchart TD
    Event[Event Fired] -->|Triggers| Listeners[Event Listeners]
    Listeners -->|Execute| Callbacks[Callback Functions]
    
    subgraph "Core Events"
        TestStart[test_start]
        TestStop[test_stop]
        Request[request]
        RequestSuccess[request_success]
        RequestFailure[request_failure]
        UserStart[user_start]
        UserStop[user_stop]
        Spawning[spawning_complete]
        Quitting[quitting]
    end
    
    subgraph "Example Use Cases"
        TestStart -->|Initialize| Resources[Resource Initialization]
        RequestSuccess -->|Log| Metrics[Metrics Collection]
        RequestFailure -->|Alert| Monitoring[Monitoring System]
        UserStart -->|Setup| UserData[User Data]
        Quitting -->|Cleanup| Resources
    end
```

## Distributed Mode Data Flow

In distributed mode, Locust uses ZeroMQ for communication between master and worker nodes.

```mermaid
flowchart TD
    Master[Master Node] -->|Sends Commands| Workers[Worker Nodes]
    Workers -->|Report Stats| Master
    
    subgraph "Command Types"
        Spawn[Spawn Users]
        Stop[Stop Users]
        Quit[Quit]
        ClientReady[Client Ready]
        ClientStopped[Client Stopped]
        Stats[Stats]
        Exception[Exception]
    end
    
    Master -->|Spawn| Workers
    Master -->|Stop| Workers
    Master -->|Quit| Workers
    
    Workers -->|ClientReady| Master
    Workers -->|ClientStopped| Master
    Workers -->|Stats| Master
    Workers -->|Exception| Master
    
    subgraph "Stats Data"
        UserCount[User Count]
        RequestCount[Request Count]
        Failures[Failures]
        ResponseTimes[Response Times]
    end
    
    Workers -->|Reports| UserCount
    Workers -->|Reports| RequestCount
    Workers -->|Reports| Failures
    Workers -->|Reports| ResponseTimes
```

## Data Flow During Test Execution

```mermaid
sequenceDiagram
    participant User as User Task
    participant Client as HTTP Client
    participant Target as Target System
    participant Events as Event System
    participant Stats as Statistics
    participant WebUI as Web UI
    
    User->>Client: Make request
    activate Client
    Client->>Target: Send HTTP request
    activate Target
    Target-->>Client: Return response
    deactivate Target
    
    Client->>Events: Fire request event
    activate Events
    Events->>Stats: Log request result
    activate Stats
    Stats->>Stats: Update metrics
    Stats-->>Events: Acknowledge
    deactivate Stats
    
    Events->>Events: Notify listeners
    Events-->>Client: Continue
    deactivate Events
    
    Client-->>User: Return response
    deactivate Client
    
    Stats->>WebUI: Update statistics display
    activate WebUI
    WebUI->>WebUI: Refresh UI
    deactivate WebUI
    
    opt CSV Export Enabled
        Stats->>Stats: Write to CSV
    end
```

## Custom Metrics Data Flow

In addition to standard HTTP metrics, Locust supports custom metrics:

```mermaid
flowchart TD
    UserCode[User Code] -->|Reports| CustomMetrics[Custom Metrics]
    CustomMetrics -->|Updates| Stats[Stats System]
    
    subgraph "Custom Metric Types"
        Counter[Counter]
        Timer[Timer]
        RateCounter[Rate Counter]
    end
    
    UserCode -->|Increment| Counter
    UserCode -->|Time Event| Timer
    UserCode -->|Count Over Time| RateCounter
    
    Counter -->|Updates| Stats
    Timer -->|Updates| Stats
    RateCounter -->|Updates| Stats
    
    Stats -->|Displays| WebUI[Web UI]
    Stats -->|Exports to| CSV[CSV Report]
```

## Web UI Data Flow

```mermaid
flowchart TD
    WebUI[Web UI Frontend] <-->|HTTP/WebSocket| Backend[Web UI Backend]
    Backend <-->|Queries| Stats[Statistics]
    Backend <-->|Controls| Runner[Test Runner]
    
    subgraph "Frontend Components"
        Dashboard[Dashboard]
        Chart[Chart]
        Control[Control Panel]
        Report[Report Page]
    end
    
    subgraph "Data Types"
        RealTimeStats[Real-time Stats]
        TestConfig[Test Configuration]
        TestStatus[Test Status]
        History[History]
    end
    
    Stats -->|Provides| RealTimeStats
    Runner -->|Reports| TestStatus
    
    RealTimeStats -->|Updates| Dashboard
    RealTimeStats -->|Visualizes| Chart
    TestStatus -->|Updates| Control
    RealTimeStats -->|Generates| Report
    
    Control -->|Modifies| TestConfig
    TestConfig -->|Configures| Runner
```
