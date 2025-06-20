<h1 style="text-align: center; margin: 3rem auto">SQLAlchemy CRUD Plus</h1>

SQLAlchemy CRUD Plus 是一个强大的 Python 库，为 SQLAlchemy 提供了增强的 CRUD（创建、读取、更新、删除）操作功能

## 核心特性

**简化的 CRUD 操作**

- 统一的 API 接口处理所有 CRUD 操作
- 支持单条和批量操作
- 完整的类型提示支持

**强大的关系查询操作**

- 通过 `load_options`、`load_strategies`、`join_conditions` 参数实现灵活的关系查询
- 支持多种预加载策略：`selectinload`、`joinedload`、`subqueryload` 等
- 支持多种 JOIN 类型：`inner`、`left`、`right`、`full`

**丰富的过滤功能**

- 支持 34+ 种过滤操作符
- 支持 OR 条件、算术运算、字符串匹配等复杂查询

**企业级特性**

- 完整的事务控制功能
- 详细的错误类型和处理机制
- 基于 SQLAlchemy 2.0 异步引擎

## 快速开始

### 安装

```bash
pip install sqlalchemy-crud-plus
```

### 基本使用

```python
from sqlalchemy_crud_plus import CRUDPlus

# 创建 CRUD 实例
crud_user = CRUDPlus(User)

# 基础 CRUD 操作
user = await crud_user.create_model(session, user_data)
user = await crud_user.select_model(session, pk=1)
await crud_user.update_model(session, pk=1, obj=update_data)
await crud_user.delete_model(session, pk=1)
```

### 关系查询

```python
# 预加载关系
user = await crud_user.select_model(
    session,
    pk=1,
    load_strategies=['posts', 'profile']
)

# JOIN 查询
users = await crud_user.select_models(
    session,
    join_conditions={'posts': 'inner'},
    name__like='%admin%'
)
```

## 下一步

- [安装指南](installing.md) - 了解如何安装
- [快速开始](getting-started/quick-start.md) - 5分钟上手指南
- [基础用法](usage/crud.md) - 学习核心 CRUD 操作
- [关系查询](relationships/overview.md) - 掌握关系查询操作
