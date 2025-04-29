# Locust Type Hints

Locust includes comprehensive type hints throughout the codebase to help developers with code completion, error checking, and documentation. This document provides an overview of how to leverage these type hints in your own code.

## Benefits of Type Hints

Type hints provide several benefits when working with Locust code:

1. **Improved Code Completion**: IDEs such as PyCharm, VS Code (with Pylance or Pyright), and others can provide more accurate code completion suggestions.
2. **Error Detection**: Type checkers like Mypy can detect potential type-related errors before runtime.
3. **Self-Documentation**: Type hints serve as documentation about what types are expected by functions and methods.
4. **Better Refactoring**: IDEs can perform more reliable refactoring operations with type information.

## Using Type Hints with Locust

### Basic Usage

When writing your test scripts with Locust, you can leverage type hints for better IDE support:

```python
from locust import HttpUser, task, between
from locust.clients import ResponseContextManager
from typing import List, Dict, Any

class MyUser(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data: List[Dict[str, Any]] = []
    
    @task
    def my_task(self) -> None:
        with self.client.get("/api/endpoint", catch_response=True) as response:
            self.process_response(response)
    
    def process_response(self, response: ResponseContextManager) -> None:
        # Using type checking to prevent potential errors
        response_json = response.json()
        if "status" in response_json and response_json["status"] == "success":
            response.success()
            if "data" in response_json:
                self.data.append(response_json["data"])
        else:
            response.failure("Status was not success or was missing")
```

### Key Types in Locust

Here are some important types you might want to use in your Locust scripts:

| Type | Module | Description |
|------|--------|-------------|
| `HttpUser` | `locust` | Base class for HTTP users |
| `FastHttpUser` | `locust` | High-performance alternative to HttpUser |
| `TaskSet` | `locust` | Group of tasks to be executed |
| `HttpSession` | `locust.clients` | Session for making HTTP requests |
| `ResponseContextManager` | `locust.clients` | Context manager for request validation |
| `Environment` | `locust.env` | Environment for test execution |
| `StatsEntry` | `locust.stats` | Statistics for a request type |
| `LoadTestShape` | `locust.shape` | Base class for custom load shapes |

### Type Checking Your Locust Code

You can use tools like Mypy to check your Locust scripts:

```bash
pip install mypy
mypy my_locustfile.py
```

For VS Code users, you can configure the Pylance extension for enhanced type checking:

```json
// settings.json
{
    "python.analysis.typeCheckingMode": "strict"
}
```

## Advanced Type Hints Examples

### Creating Custom Clients

When creating custom clients, you can use type hints to make the API clearer:

```python
from typing import Optional, Dict, Any
from locust import User
from locust.event import EventHook

class MyCustomClient:
    def __init__(self, host: str, request_event: EventHook):
        self.host = host
        self.request_event = request_event
    
    def my_operation(self, path: str, payload: Dict[str, Any], name: Optional[str] = None) -> Any:
        # Implement custom operation
        # ...
        return result

class MyCustomUser(User):
    abstract = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = MyCustomClient(self.host, self.environment.events.request)
```

### Working with Event Hooks

When working with event hooks, type hints help ensure you're handling the right parameters:

```python
from locust import events
from locust.env import Environment
from typing import Optional, Dict, Any

@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs: Any) -> None:
    print(f"Test is starting with {len(environment.user_classes)} user classes")

@events.request.add_listener
def on_request(request_type: str, name: str, response_time: float, 
               response_length: int, exception: Optional[Exception] = None, 
               **kwargs: Any) -> None:
    if exception:
        print(f"Request to {name} failed with: {exception}")
```

## Type Hints for LoadTestShape

When implementing custom load shapes, type hints can help ensure you're returning the correct format:

```python
from locust import LoadTestShape
from typing import Optional, Tuple, List, Union

class StepLoadShape(LoadTestShape):
    """Step load shape with user count steps."""
    
    step_time: int = 30
    step_users: int = 10
    spawn_rate: int = 10
    max_users: int = 100
    
    def tick(self) -> Optional[Tuple[int, float]]:
        run_time = self.get_run_time()
        
        current_step = int(run_time / self.step_time) + 1
        user_count = current_step * self.step_users
        
        if user_count > self.max_users:
            return None  # Test finished
            
        return (user_count, self.spawn_rate)
```

## Conclusion

Using type hints with your Locust code can significantly improve your development experience, especially when working with complex test scenarios, custom user types, or extensions to Locust's functionality.

By taking advantage of the type information already present in Locust, you can catch potential errors earlier in the development process and make your code more maintainable.
