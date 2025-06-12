# 安装

## 系统要求

- Python 3.10+
- SQLAlchemy 2.0+
- Pydantic 2.0+

## 从 PyPI 安装

```bash
pip install sqlalchemy-crud-plus
```

## 从源码安装

```bash
git clone https://github.com/wu-clan/sqlalchemy-crud-plus.git
cd sqlalchemy-crud-plus
pip install -e .
```

## 可选依赖

### 数据库驱动

对于不同的数据库，您需要安装相应的驱动程序：

**PostgreSQL**
```bash
pip install asyncpg
```

**MySQL**
```bash
pip install aiomysql
```

**SQLite**
```bash
# Python 内置，无需额外驱动
pip install aiosqlite  # 异步支持
```

### 开发依赖

如果您想要贡献代码或运行测试：

```bash
pip install sqlalchemy-crud-plus[dev]
```

包含以下工具：
- pytest
- pytest-asyncio
- black
- isort
- mypy

## 验证安装

```python
import sqlalchemy_crud_plus
print(f"版本: {sqlalchemy_crud_plus.__version__}")
```

## 下一步

- [快速开始](getting-started/quick-start.md) - 5分钟上手指南
- [基础用法](usage/crud.md) - CRUD 操作详解
