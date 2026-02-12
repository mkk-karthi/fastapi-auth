from typing import Type, TypeVar
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Query

SchemaType = TypeVar("SchemaType", bound=BaseModel)


def paginate(query: Query, schema: Type[SchemaType] = None, page: int = 1, size: int = 10):
    total = query.count()

    items = query.offset((page - 1) * size).limit(size).all()

    if schema:
        items = [schema.model_validate(item) for item in items]

    return {
        "items": jsonable_encoder(items),
        "page": page,
        "size": size,
        "total": total,
    }
