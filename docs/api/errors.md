# 错误

本页面记录了 SQLAlchemy CRUD Plus 可能抛出的错误类型和异常。

## Exception Hierarchy

```
Exception
├── SQLAlchemyError (from SQLAlchemy)
│   ├── IntegrityError
│   ├── DataError
│   └── OperationalError
├── ValidationError (from Pydantic)
└── CRUDPlusError (custom)
    ├── ModelNotFoundError
    ├── MultipleResultsFoundError
    └── InvalidFilterError
```

## Common Exceptions

### ValidationError

Raised when Pydantic schema validation fails.

```python
from pydantic import ValidationError

try:
    user_data = UserCreate(name="", email="invalid-email")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### IntegrityError

Raised when database constraints are violated.

```python
from sqlalchemy.exc import IntegrityError

try:
    user = await user_crud.create_model(session, user_data)
except IntegrityError as e:
    if "UNIQUE constraint failed" in str(e):
        print("Email already exists")
```

### ModelNotFoundError

Custom exception for when a model is not found.

```python
user = await user_crud.select_model(session, 999)
if not user:
    # Handle not found case
    pass
```

## Error Handling Patterns

### Basic Error Handling

```python
async def safe_create_user(user_data: dict):
    try:
        validated_data = UserCreate(**user_data)
        async with _async_db_session() as session:
            async with session.begin():
                user = await user_crud.create_model(session, validated_data)
        return {"success": True, "user": user}
    
    except ValidationError as e:
        return {"success": False, "error": "Invalid data", "details": str(e)}
    
    except IntegrityError as e:
        return {"success": False, "error": "Database constraint violation", "details": str(e)}
    
    except Exception as e:
        return {"success": False, "error": "Unexpected error", "details": str(e)}
```

### Transaction Error Handling

```python
async def transaction_with_error_handling():
    async with _async_db_session() as session:
        try:
            async with session.begin():
                # Multiple operations
                user = await user_crud.create_model(session, user_data)
                profile = await profile_crud.create_model(session, profile_data)
                
        except Exception as e:
            # Transaction automatically rolled back
            print(f"Transaction failed: {e}")
            raise
```

## Best Practices

1. **Catch Specific Exceptions**
   - Always catch the most specific exception type first
   - Provide meaningful error messages
   - Log detailed error information for debugging

2. **Use Transaction Context**
   - Let `session.begin()` handle rollbacks automatically
   - Don't manually manage transaction state unless necessary
   - Keep transactions as short as possible

3. **Validate Early**
   - Use Pydantic schemas to validate input data
   - Check for required conditions before database operations
   - Provide clear validation error messages

4. **Error Logging**
   - Log errors with sufficient context
   - Include request IDs or user information
   - Use appropriate log levels (ERROR, WARNING, INFO)
