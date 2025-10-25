# Real world app

This example shows how `adaptix` can be integrated into production code.

Here are five real-world scenarios:
1) Config is loaded from env variables (file `config.py`)
2) Storing cache in Redis-like storage (file `user_gateway.py`)
3) Transformation SQLAlchemy model to Pydantic model (file `routes.py`)
4) Serializing SQLAlchemy model directly (file `routes.py`)
5) Storing JSON in DB with transparent parsing and dumping (file `db_models.py`)
