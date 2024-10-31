import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.api.categories import categories_router as api_categories_router
from routers.api.replies import replies_router
from routers.api.tokens import token_router
from routers.api.topics import topics_router
from routers.api.users import users_router as api_users_router
from routers.api.votes import votes_router
from routers.api.messages import messages_router as api_messages_router
from routers.api.conversations import conversations_router as api_conversations_router
import logging

from routers.web.categories import categories_router
from routers.web.conversations import conversations_router
from routers.web.home import index_router
from routers.web.messages import messages_router
from routers.web.users import users_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(api_categories_router)
app.include_router(topics_router)
app.include_router(replies_router)
app.include_router(api_users_router)
app.include_router(votes_router)
app.include_router(token_router)
app.include_router(api_messages_router)
app.include_router(api_conversations_router)


# web routers
app.include_router(index_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(conversations_router)
app.include_router(messages_router)



if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000)