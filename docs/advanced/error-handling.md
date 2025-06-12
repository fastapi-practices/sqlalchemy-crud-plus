# 错误处理

SQLAlchemy CRUD Plus 提供了完善的错误处理机制，帮助开发者优雅地处理各种异常情况。

## 常见异常类型

### 数据验证错误

```python
from pydantic import ValidationError

async def handle_validation_error():
    async with _async_db_session() as session:
        try:
            # 无效的数据
            invalid_data = {"name": "", "email": "invalid-email"}
            user_data = UserCreate(**invalid_data)
            
        except ValidationError as e:
            print(f"数据验证失败: {e}")
            # 处理验证错误
            return {"error": "数据格式不正确"}
```

### 数据库约束错误

```python
from sqlalchemy.exc import IntegrityError

async def handle_integrity_error():
    async with _async_db_session() as session:
        try:
            async with session.begin():
                user_data = UserCreate(name="张三", email="existing@example.com")
                user = await user_crud.create_model(session, user_data)
                
        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {"error": "邮箱地址已存在"}
            elif "NOT NULL constraint failed" in str(e):
                return {"error": "必填字段不能为空"}
            else:
                return {"error": f"数据完整性错误: {e}"}
```

### 记录不存在错误

```python
async def handle_not_found():
    async with _async_db_session() as session:
        user = await user_crud.select_model(session, 999)
        
        if not user:
            return {"error": "用户不存在"}
        
        return user
```

## 完整错误处理示例

```python
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError

async def create_user_with_error_handling(user_data: dict):
    async with _async_db_session() as session:
        try:
            # 数据验证
            validated_data = UserCreate(**user_data)
            
            async with session.begin():
                # 创建用户
                user = await user_crud.create_model(session, validated_data)
                
            return {"success": True, "user": user}
            
        except ValidationError as e:
            return {
                "success": False,
                "error": "数据验证失败",
                "details": str(e)
            }
            
        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {
                    "success": False,
                    "error": "邮箱地址已存在"
                }
            return {
                "success": False,
                "error": "数据完整性错误",
                "details": str(e)
            }
            
        except SQLAlchemyError as e:
            return {
                "success": False,
                "error": "数据库操作失败",
                "details": str(e)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "未知错误",
                "details": str(e)
            }
```

## 事务回滚处理

```python
async def transaction_with_rollback():
    async with _async_db_session() as session:
        try:
            async with session.begin():
                # 创建用户
                user_data = UserCreate(name="张三", email="zhangsan@example.com")
                user = await user_crud.create_model(session, user_data, flush=True)
                
                # 创建个人资料
                profile_data = ProfileCreate(user_id=user.id, bio="个人简介")
                profile = await profile_crud.create_model(session, profile_data)
                
                # 如果这里出现异常，整个事务会自动回滚
                
        except Exception as e:
            # session.begin() 会自动处理回滚
            print(f"事务失败，已回滚: {e}")
            raise
```

## 自定义异常处理

```python
class UserNotFoundError(Exception):
    """用户不存在异常"""
    pass

class DuplicateEmailError(Exception):
    """邮箱重复异常"""
    pass

async def get_user_safe(user_id: int):
    async with _async_db_session() as session:
        user = await user_crud.select_model(session, user_id)
        
        if not user:
            raise UserNotFoundError(f"用户 ID {user_id} 不存在")
        
        return user

async def create_user_safe(user_data: UserCreate):
    async with _async_db_session() as session:
        try:
            async with session.begin():
                user = await user_crud.create_model(session, user_data)
                
        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateEmailError(f"邮箱 {user_data.email} 已存在")
            raise
        
        return user
```

## 最佳实践

1. **分层错误处理**
   - 在数据访问层处理数据库相关错误
   - 在业务逻辑层处理业务规则错误
   - 在接口层处理用户输入错误

2. **使用事务**
   - 使用 `async with session.begin()` 自动处理事务
   - 避免手动管理事务状态
   - 让异常自然传播以触发回滚

3. **错误日志**
   - 记录详细的错误信息用于调试
   - 向用户返回友好的错误消息
   - 避免泄露敏感信息

4. **异常类型**
   - 捕获具体的异常类型
   - 提供有意义的错误消息
   - 使用自定义异常表达业务逻辑
