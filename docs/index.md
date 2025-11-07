# SQLAlchemy CRUD Plus

基于 SQLAlchemy 2.0 构建的高级异步 CRUD SDK

## 特性

- **简化的 CRUD 操作** - 统一的 API 接口，支持批量操作
- **关系查询支持** - 预加载策略和 JOIN 查询，避免 N+1 问题
- **丰富的过滤条件** - 支持 30+ 种过滤操作符
- **类型安全** - 完整的类型提示支持
- **异步支持** - 基于 SQLAlchemy 2.0 异步引擎
- **复合主键支持** - 支持多字段主键操作

## 快速开始

### 安装

```bash
pip install sqlalchemy-crud-plus
```

### 基本用法

```python
from sqlalchemy_crud_plus import CRUDPlus

# 创建 CRUD 实例
user_crud = CRUDPlus(User)

# 创建记录
user = await user_crud.create_model(session, user_data)

# 查询记录
user = await user_crud.select_model(session, pk=1)
users = await user_crud.select_models(session, is_active=True)

# 更新记录
await user_crud.update_model(session, pk=1, obj=update_data)

# 删除记录
await user_crud.delete_model(session, pk=1)

# 过滤查询
users = await user_crud.select_models(
    session,
    name__like='%admin%',
    age__ge=18,
    email__endswith='@example.com'
)

# 关系查询
users = await user_crud.select_models(
    session,
    load_strategies=['posts', 'profile']
)
```

## 文档导航

- [安装指南](installing.md) - 环境准备和依赖安装
- [快速开始](getting-started/quick-start.md) - 基础用法示例
- [基础 CRUD](usage/crud.md) - 增删改查操作详解
- [过滤条件](advanced/filter.md) - 查询过滤操作符
- [关系查询](advanced/relationship.md) - 预加载和 JOIN 查询
- [事务控制](advanced/transaction.md) - 事务管理
- [API 参考](api/crud-plus.md) - 完整 API 文档
