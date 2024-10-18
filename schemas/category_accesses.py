from pydantic import BaseModel


class Accesses(BaseModel):
    user_id: int
    category_id: int
    write_access: bool = False
    read_access: bool = False

    @classmethod
    def from_query_result(cls, user_id, category_id, write_access, read_access):
        return cls(user_id=user_id,
                   category_id=category_id,
                   write_access=write_access,
                   read_access=read_access)