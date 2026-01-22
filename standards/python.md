# Python Coding Standards

## Core Philosophy
- Simplicity over cleverness - code should read like prose
- Use battle-tested libraries over custom implementations
- Names reveal intent, not implementation details
- If it needs explanation, rewrite it
- One function does one thing - if you use "and" to describe it, split it

## Essential Libraries to Prefer

**Data manipulation:** pandas (DataFrames), polars (fast DataFrames), numpy (numerical operations)

**HTTP & APIs:** httpx (modern async+sync), requests (simple synchronous)

**Async:** asyncio (built-in runtime), aiohttp (async HTTP)

**CLI tools:** typer (beautiful CLIs with type hints), rich (terminal formatting and progress)

**Data validation:** pydantic (type-safe structures), attrs (lightweight dataclasses alternative)

**Testing:** pytest (standard test framework), hypothesis (property-based testing)

**Date/time:** pendulum (timezone-sane datetime), arrow (human-friendly dates)

**Utilities:** itertools (built-in iteration tools), more-itertools (extended recipes), toolz (functional programming)

## Code Quality Standards

**Always use:**
- Type hints on all function signatures as runnable documentation
- List/dict comprehensions over manual loops
- Early returns over nested conditionals
- pathlib over os.path string manipulation
- Context managers (with statements) for all resources
- f-strings for display formatting only
- Dataclasses or pydantic models for data structures
- Parameterized queries for SQL (never string concatenation)
- PEP 8 compliance via black or ruff auto-formatting
- Import grouping: stdlib first, then third-party, then local

**Never use:**
- Try/except for flow control (use .get() methods instead)
- String concatenation for SQL queries
- Manual dictionary/list building when comprehensions work
- Complex inheritance hierarchies (prefer composition)
- Clever one-liners that obscure meaning
- Nested conditionals more than 2 levels deep

## Pattern Examples

**List comprehensions:**
```python
emails = [u.email for u in users if u.is_active]
user_map = {u.id: u for u in users}
```

**Early returns for clarity:**
```python
def get_discount(user):
    if not user or not user.is_premium:
        return 0
    return 0.2 if user.orders > 10 else 0.1
```

**Modern path handling:**
```python
from pathlib import Path
path = Path(__file__).parent / "data" / filename
```

**Proper type hints:**
```python
def calculate_total(items: list[dict], tax_rate: float) -> float:
    """Calculate total with tax applied."""
    return sum(item['price'] for item in items) * (1 + tax_rate)
```

**Dataclasses for structures:**
```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    is_active: bool = True
```

**Library methods over manual code:**
```python
# Use dict.get() instead of try/except KeyError
value = my_dict.get(key, default_value)

# Use httpx methods instead of manual error checking
data = httpx.get(url).raise_for_status().json()

# Use filter/map with attrgetter for clarity
from operator import attrgetter
emails = [u.email for u in users if u.is_active]
```

**Context managers always:**
```python
with open('file.txt') as f:
    data = f.read()
```

## Documentation Standards

- Docstrings for all public functions using imperative mood
- Type hints are primary documentation
- Comments explain "why" not "what"
- Keep functions small enough that they don't need comments

## Key Principle

Code is read 10x more than it's written. Always optimize for the reader. Choose readability over performance until performance becomes a measured problem.
