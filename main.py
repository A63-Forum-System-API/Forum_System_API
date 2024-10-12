import uvicorn
from fastapi import FastAPI
from routers.categories import categories_router
from routers.topics import topics_router

app = FastAPI()
app.include_router(categories_router)
app.include_router(topics_router)


if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000)