from pydantic import BaseModel


class Accesses(BaseModel):
    user_id: int
    username: str
    category_id: int
    write_access: bool 

    @classmethod
    def from_query_result(cls, user_id, username, category_id, write_access):
        return cls(user_id=user_id,
                   username=username,
                   category_id=category_id,
                   write_access=write_access)
