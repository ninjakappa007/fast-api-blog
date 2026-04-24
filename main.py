from fastapi import FastAPI
from snippets import POSTS
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
@app.get("/posts", response_class=HTMLResponse)
async def root():
    return f"<h1>{POSTS[0]['title']}</h1>"

@app.get("/api/posts")
def get_posts():
    return POSTS