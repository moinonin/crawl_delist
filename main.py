from fastapi import FastAPI
from crawler import *
import uvicorn

app = FastAPI()


@app.get("/api/delisted/{exchange}/")
async def get_pairs(exchange: str):
    return scraper(f'{exchange}')


if __name__ == '__main__':
    from firecrawl import FirecrawlApp
    uvicorn.run(app, host="0.0.0.0", port=10000)


