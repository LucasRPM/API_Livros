#CRUD (Create, Read, Update, Delete)

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os

class Livro(BaseModel):
    titulo: str
    autor: str
    ano: int

app = FastAPI(
    title="API de Livros",
    description="API para gerenciar livros",
    version="1.0.0",
    contact={
        "nome": "Lucas Pedroso",
        "email": "myrapha_pedroso@hotmail.com",
        "github": "https://github.com/LucasRPM"
    }
)

meu_usuario = "admin"
minha_senha = "admin"

security = HTTPBasic()

def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, meu_usuario)
    is_password_correct = secrets.compare_digest(credentials.password, minha_senha)
    
    if is_username_correct and is_password_correct:
        return credentials.username
    else:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos", headers={"WWW-Authenticate": "Basic"})

dicionario = {
    1 : {"titulo": "Jogador Nº1", "autor": "Ernest Cline", "ano": 2011},
    2 : {"titulo": "Senhor dos Anéis", "autor": "J.R.R. Tolkien", "ano": 1954},
    3 : {"titulo": "Harry Potter e a Pedra Filosofal", "autor": "J.K. Rowling", "ano": 1997},
    4 : {"titulo": "O nome do vento", "autor": "Patrick Rothfuss", "ano": 2007},
    5 : {"titulo": "O último império", "autor": "Brandon Sanderson", "ano": 2006},
    6 : {"titulo": "O caminho dos Reis", "autor": "Brandon Sanderson", "ano": 2010},
    7 : {"titulo": "A roda do tempo", "autor": "Robert Jordan", "ano": 1990},
    8 : {"titulo": "1984", "autor": "George Orwell", "ano": 1949},
    9 : {"titulo": "Admirável Mundo Novo", "autor": "Aldous Huxley", "ano": 1932},
    10 : {"titulo": "Fahrenheit 451", "autor": "Ray Bradbury", "ano": 1953},
    11 : {"titulo": "Duna", "autor": "Frank Herbert", "ano": 1965},
    12 : {"titulo": "Neuromancer", "autor": "William Gibson", "ano": 1984},
    13 : {"titulo": "O Guia do Mochileiro das Galáxias", "autor": "Douglas Adams", "ano": 1979},
    14 : {"titulo": "Fundação", "autor": "Isaac Asimov", "ano": 1951},
    15 : {"titulo": "Eu, Robô", "autor": "Isaac Asimov", "ano": 1950},
    16 : {"titulo": "O Código Da Vinci", "autor": "Dan Brown", "ano": 2003},
    17 : {"titulo": "Anjos e Demônios", "autor": "Dan Brown", "ano": 2000},
    18 : {"titulo": "A Guerra dos Tronos", "autor": "George R. R. Martin", "ano": 1996},
    19 : {"titulo": "O Iluminado", "autor": "Stephen King", "ano": 1977},
    20 : {"titulo": "It: A Coisa", "autor": "Stephen King", "ano": 1986},
    21 : {"titulo": "Orgulho e Preconceito", "autor": "Jane Austen", "ano": 1813},
    22 : {"titulo": "Dom Quixote", "autor": "Miguel de Cervantes", "ano": 1605},
    23 : {"titulo": "O Pequeno Príncipe", "autor": "Antoine de Saint-Exupéry", "ano": 1943},
    24 : {"titulo": "A Menina que Roubava Livros", "autor": "Markus Zusak", "ano": 2005},
    25 : {"titulo": "Sapiens: Uma Breve História da Humanidade", "autor": "Yuval Noah Harari", "ano": 2011},
}

#dicionario = {}

#GET--------------------------------------------------------------------------------
@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10, credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page ou limit inválidos")
    
    if not dicionario:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    
    start = (page - 1) * limit
    end = start + limit

    livros_paginados = [
        {"id": id, "nome_livro": livro_data["titulo"], "autor": livro_data["autor"], "ano": livro_data["ano"]}
        for id, livro_data in list(dicionario.items())[start:end]
    ]

    return {
        "page": page,
        "limit": limit,
        "total": len(dicionario),
        "livros": livros_paginados
    }

@app.get("/livros/{id}")
def get_livro(id: int, credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    if id not in dicionario:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        return dicionario[id]

#POST------------------------------------------------------------------------------
@app.post("/adicionar")
def adicionar_livro(id: int, livro: Livro, credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    if id in dicionario:
        raise HTTPException(status_code=400, detail="Livro já cadastrado")
    else:
        dicionario[id] = livro.dict()
        return {"message": "Livro adicionado com sucesso"}

#PUT--------------------------------------------------------------------------------
@app.put("/atualizar/{id}")
def atualizar_livro(id: int, livro:Livro, credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    livro_atualizado = dicionario.get(id)
    if not livro_atualizado:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        dicionario[id] = livro.dict()
        return {"message": "Livro atualizado com sucesso"}

#DELETE----------------------------------------------------------------------------
@app.delete("/deletar/{id}")
def deletar_livro(id: int, credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    if id not in dicionario:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        del dicionario[id]
        return {"message": "Livro deletado com sucesso"}
    