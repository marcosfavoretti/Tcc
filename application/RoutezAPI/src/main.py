
from fastapi import FastAPI
from delivery import algoritmos_rotas
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.include_router(algoritmos_rotas.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou especifique: ["http://localhost:4200"] por exemplo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def ping():
    return 'pong'