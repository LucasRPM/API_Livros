#CRUD (Create, Read, Update, Delete)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

class Livro(BaseModel):
    titulo: str
    autor: str
    ano: int

app = FastAPI()

"""dicionario = {
    1 : {"titulo": "Jogador Nº1", "autor": "Ernest Cline", "ano": 2011},
    2 : {"titulo": "Senhor dos Anéis", "autor": "J.R.R. Tolkien", "ano": 1954},
    3 : {"titulo": "Harry Potter e a Pedra Filosofal", "autor": "J.K. Rowling", "ano": 1997},
    4 : {"titulo": "O nome do vento", "autor": "Patrick Rothfuss", "ano": 2007},
    5 : {"titulo": "O último império", "autor": "Brandon Sanderson", "ano": 2006},
    6 : {"titulo": "O caminho dos Reis", "autor": "Brandon Sanderson", "ano": 2010},
    7 : {"titulo": "A roda do tempo", "autor": "Robert Jordan", "ano": 1990},
    8 : {"titulo": "A saga do herdeiro", "autor": "Brandon Sanderson", "ano": 2015},
    9 : {"titulo": "Mistborn: O Império Final", "autor": "Brandon Sanderson", "ano": 2006},
    10 : {"titulo": "A máscara da loucura", "autor": "Brandon Sanderson", "ano": 2006},
}"""

dicionario = {}

#GET--------------------------------------------------------------------------------
@app.get("/livros")
def get_livros():
    if not dicionario:
        return {"message": "Nenhum livro encontrado"}
    else:
        return dicionario

@app.get("/livros/{id}")
def get_livro(id: int):
    if id not in dicionario:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        return dicionario[id]

#POST------------------------------------------------------------------------------
@app.post("/adicionar")
def adicionar_livro(id: int, livro: Livro):
    if id in dicionario:
        raise HTTPException(status_code=400, detail="Livro já cadastrado")
    else:
        dicionario[id] = livro.dict()
        return {"message": "Livro adicionado com sucesso"}

#PUT--------------------------------------------------------------------------------
@app.put("/atualizar/{id}")
def atualizar_livro(id: int, livro:Livro):
    livro_atualizado = dicionario.get(id)
    if not livro_atualizado:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        dicionario[id] = livro.dict()
        return {"message": "Livro atualizado com sucesso"}

#DELETE----------------------------------------------------------------------------
@app.delete("/deletar/{id}")
def deletar_livro(id: int):
    if id not in dicionario:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        del dicionario[id]
        return {"message": "Livro deletado com sucesso"}
    