# 安装

本页面将指导您如何安装 SQLAlchemy CRUD Plus。

## 系统要求

- Python 3.10+
- SQLAlchemy 2.0+
- Pydantic 2.0+

## 安装

使用 pip 安装 SQLAlchemy CRUD Plus：

```bash
pip install sqlalchemy-crud-plus
```

这将安装核心库及其必需的依赖项：

- `sqlalchemy>=2.0.0`
- `pydantic>=2.0.0`

## 验证安装

安装完成后，您可以验证安装是否成功：

```python
import sqlalchemy_crud_plus

print(sqlalchemy_crud_plus.__version__)
```

## 下一步

安装完成后，您可以：

- 查看 [快速开始](getting-started/quick-start.md) 了解基本用法
- 阅读 [基础用法](usage/crud.md) 学习 CRUD 操作
- 探索 [关系查询](relationships/overview.md) 了解关系查询功能
