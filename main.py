#CRUD (Create, Read, Update, Delete)

# Importações do FastAPI para criar as rotas da API, tratar erros e injetar dependências
from fastapi import FastAPI, HTTPException, Depends
# Importações para utilizar autenticação HTTP Basic (usuário e senha)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
# Pydantic é usado para validar os dados que entram na API (schemas)
from pydantic import BaseModel
from typing import Optional
# Usado para comparar senhas de forma segura contra ataques de timing
import secrets
import os

# Importações do SQLAlchemy, o ORM para interagir com o banco de dados como objetos Python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# URL de conexão com o banco de dados (neste caso, um arquivo local SQLite)
DATA_BASE_URL = "sqlite:///./livros.db"

# Cria a engine do SQLAlchemy. 
# 'check_same_thread': False é importante no SQLite para permitir que requisições em diferentes threads do FastAPI acessem o banco
engine = create_engine(DATA_BASE_URL, connect_args={"check_same_thread": False})
# Define a fábrica de sessões do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base para a criação das classes que vão mapear as tabelas do banco de dados
Base = declarative_base()

# Classe que mapeia a tabela "Livros" no banco de dados através do SQLAlchemy
class LivroDB(Base):
    __tablename__ = "Livros"
    # Definição das colunas da tabela
    id = Column(Integer, primary_key = True, index = True)
    nome_livro = Column(String, index = True)
    autor_livro = Column(String, index = True)
    ano_livro = Column(Integer)

# Classe Pydantic que serve como um Schema/Contrato dos dados.
# Essa classe será exigida quando enviarmos dados JSON (ex: POST ou PUT)
class Livro(BaseModel):
    titulo: str
    autor: str
    ano: int

# Função dependência (Dependency) que cria uma sessão do banco para cada requisição
# e garante o fechamento da conexão (db.close) quando a requisição finalizar
def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Executa a criação das tabelas no banco de dados caso ainda não existam
Base.metadata.create_all(bind=engine)

# Inicialização da aplicação FastAPI, adicionando metadados úteis para a documentação gerada automaticamente
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

# Definição de credenciais de administrador (em produção usaríamos variáveis de ambiente)
meu_usuario = "admin"
minha_senha = "admin"

# Configuração do esquema de segurança (Basic Auth, pop-up de login no navegador/docs)
security = HTTPBasic()

# Função dependência de segurança: valida se o usuário e senha enviados na requisição estão corretos
def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, meu_usuario)
    is_password_correct = secrets.compare_digest(credentials.password, minha_senha)
    
    if is_username_correct and is_password_correct:
        return credentials.username
    else:
        # Lança erro 401 caso as credenciais sejam inválidas
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos", headers={"WWW-Authenticate": "Basic"})

dicionario = {
    105 : {"titulo": "Jogador Nº1", "autor": "Ernest Cline", "ano": 2011},
    34 : {"titulo": "Senhor dos Anéis", "autor": "J.R.R. Tolkien", "ano": 1954},
    12 : {"titulo": "Harry Potter e a Pedra Filosofal", "autor": "J.K. Rowling", "ano": 1997},
    89 : {"titulo": "O nome do vento", "autor": "Patrick Rothfuss", "ano": 2007},
    7 : {"titulo": "O último império", "autor": "Brandon Sanderson", "ano": 2006},
    2 : {"titulo": "O caminho dos Reis", "autor": "Brandon Sanderson", "ano": 2010},
    55 : {"titulo": "A roda do tempo", "autor": "Robert Jordan", "ano": 1990},
    99 : {"titulo": "1984", "autor": "George Orwell", "ano": 1949},
    14 : {"titulo": "Admirável Mundo Novo", "autor": "Aldous Huxley", "ano": 1932},
    23 : {"titulo": "Fahrenheit 451", "autor": "Ray Bradbury", "ano": 1953},
    77 : {"titulo": "Duna", "autor": "Frank Herbert", "ano": 1965},
    42 : {"titulo": "Neuromancer", "autor": "William Gibson", "ano": 1984},
    68 : {"titulo": "O Guia do Mochileiro das Galáxias", "autor": "Douglas Adams", "ano": 1979},
    1 : {"titulo": "Fundação", "autor": "Isaac Asimov", "ano": 1951},
    3 : {"titulo": "Eu, Robô", "autor": "Isaac Asimov", "ano": 1950},
    200 : {"titulo": "O Código Da Vinci", "autor": "Dan Brown", "ano": 2003},
    150 : {"titulo": "Anjos e Demônios", "autor": "Dan Brown", "ano": 2000},
    8 : {"titulo": "A Guerra dos Tronos", "autor": "George R. R. Martin", "ano": 1996},
    19 : {"titulo": "O Iluminado", "autor": "Stephen King", "ano": 1977},
    31 : {"titulo": "It: A Coisa", "autor": "Stephen King", "ano": 1986},
    64 : {"titulo": "Orgulho e Preconceito", "autor": "Jane Austen", "ano": 1813},
    4 : {"titulo": "Dom Quixote", "autor": "Miguel de Cervantes", "ano": 1605},
    111 : {"titulo": "O Pequeno Príncipe", "autor": "Antoine de Saint-Exupéry", "ano": 1943},
    22 : {"titulo": "A Menina que Roubava Livros", "autor": "Markus Zusak", "ano": 2005},
    5 : {"titulo": "Sapiens: Uma Breve História da Humanidade", "autor": "Yuval Noah Harari", "ano": 2011},
}

#GET--------------------------------------------------------------------------------
# Rota GET para listar os livros com paginação. 
# Requer conexão com DB (db) e credenciais válidas (credentials)
@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10, db: Session = Depends(sessao_db), credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    # Valida parâmetros da página
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page ou limit inválidos")
    
    # Realiza consulta no banco, pulando 'offset' registros e limitando a 'limit' registros
    livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()
    
    if not livros:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")

    # Consulta o total de registros disponíveis
    total_livros = db.query(LivroDB).count()

    """livros_paginados = [
        {"id": id, "nome_livro": livro_data["titulo"], "autor": livro_data["autor"], "ano": livro_data["ano"]}
        for id, livro_data in livros_ordenados[start:end]
    ]"""

    # Retorna o resultado JSON formatado com metadados da paginação
    return {
        "page": page,
        "limit": limit,
        "total": total_livros,
        "livros": [{
            "id": livro.id,
            "nome_livro": livro.nome_livro,
            "autor_livro": livro.autor_livro,
            "ano_livro": livro.ano_livro
        } for livro in livros]
    }

# Rota GET para buscar um livro específico pelo seu ID
@app.get("/livros/{id}")
def get_livro(id: int, db: Session = Depends(sessao_db), credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    # Filtra e busca o primeiro (first) livro com o ID correspondente no banco de dados
    db_livro = db.query(LivroDB).filter(LivroDB.id == id).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        return {
            "id": db_livro.id,
            "nome_livro": db_livro.nome_livro,
            "autor_livro": db_livro.autor_livro,
            "ano_livro": db_livro.ano_livro
        }

#POST------------------------------------------------------------------------------
# Rota POST utilizada para criação (inserção) de novos registros no banco de dados
@app.post("/adicionar")
def adicionar_livro(livro: Livro, db: Session = Depends(sessao_db), credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    # Verifica se já não existe um livro com o mesmo título e mesmo autor para evitar duplicidade
    db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.titulo, LivroDB.autor_livro == livro.autor).first()
    if db_livro:
        raise HTTPException(status_code=400, detail="Livro já existe")

    # Cria uma nova instância do modelo LivroDB preenchido com as propriedades vindas do usuário (JSON)
    novo_livro = LivroDB(
        nome_livro = livro.titulo,
        autor_livro = livro.autor,
        ano_livro = livro.ano
    )

    # Adiciona a nova instância à sessão de banco de dados
    db.add(novo_livro)
    # Efetiva as transações (salva fisicamente as mudanças) no banco de dados
    db.commit()
    # Atualiza a variável `novo_livro` com as informações preenchidas pelo banco (como o novo `id` gerado)
    db.refresh(novo_livro)
    return {"message": "Livro adicionado com sucesso"}

#PUT--------------------------------------------------------------------------------
# Rota PUT utilizada para atualização completa de registros existentes usando seu ID
@app.put("/atualizar/{id}")
def atualizar_livro(id: int, livro:Livro, db: Session = Depends(sessao_db), credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    # Busca pelo registro
    db_livro = db.query(LivroDB).filter(LivroDB.id == id).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        # Substitui os dados originais pelos novos fornecidos na requisição
        db_livro.nome_livro = livro.titulo
        db_livro.autor_livro = livro.autor
        db_livro.ano_livro = livro.ano
        
        # Salva e efetiva no banco de dados
        db.commit()
        db.refresh(db_livro)
        return {"message": "Livro atualizado com sucesso"}
    

#DELETE----------------------------------------------------------------------------
# Rota DELETE utilizada para exclusão de um registro existente pelo seu ID
@app.delete("/deletar/{id}")
def deletar_livro(id: int, db: Session = Depends(sessao_db), credentals: HTTPBasicCredentials = Depends(autenticar_meu_usuario)):
    # Identifica o livro alvo
    db_livro = db.query(LivroDB).filter(LivroDB.id == id).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado no banco de dados")
    
    # Executa a remoção
    db.delete(db_livro)
    # Efetiva as transações (salva as mudanças no banco de dados)
    db.commit()
    
    return {"message": "Livro deletado com sucesso"}