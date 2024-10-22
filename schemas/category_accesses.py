from pydantic import BaseModel


class Accesses(BaseModel):
    user_id: int
    category_id: int
    type_access: bool = True

    @classmethod
    def from_query_result(cls, user_id, category_id, type_access):
        return cls(user_id=user_id,
                   category_id=category_id,
                   type_access=type_access)