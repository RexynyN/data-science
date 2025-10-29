import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

# Inicialização
fake = Faker()
random.seed(42)
Faker.seed(42)

# Conexão SQLite
conn = sqlite3.connect("eduplus.db")
cursor = conn.cursor()

# Criação de tabelas
cursor.executescript("""
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS cursos;
DROP TABLE IF EXISTS matriculas;
DROP TABLE IF EXISTS avaliacoes;
DROP TABLE IF EXISTS certificados;

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT,
    data_cadastro DATE,
    idade INTEGER,
    genero TEXT,
    pais TEXT
);

CREATE TABLE cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    categoria TEXT,
    nivel TEXT,
    duracao_horas REAL,
    instrutor TEXT
);

CREATE TABLE matriculas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    id_curso INTEGER,
    data_matricula DATE,
    status TEXT,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY(id_curso) REFERENCES cursos(id)
);

CREATE TABLE avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    id_curso INTEGER,
    nota INTEGER,
    comentario TEXT,
    data_avaliacao DATE,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY(id_curso) REFERENCES cursos(id)
);

CREATE TABLE certificados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    id_curso INTEGER,
    data_emissao DATE,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY(id_curso) REFERENCES cursos(id)
);
""")

# Dados auxiliares
generos = ['Masculino', 'Feminino', 'Outro']
paises = ['Brasil', 'EUA', 'Canadá', 'Alemanha', 'Índia']
categorias = ['Programação', 'Negócios', 'Design', 'Marketing', 'Finanças']
niveis = ['Iniciante', 'Intermediário', 'Avançado']
status_matricula = ['ativa', 'concluída', 'cancelada']

# Usuários
usuarios = []
for _ in range(500):
    nome = fake.name()
    email = fake.email()
    data_cadastro = fake.date_between(start_date='-2y', end_date='today')
    idade = random.randint(16, 65)
    genero = random.choice(generos)
    pais = random.choice(paises)
    usuarios.append((nome, email, data_cadastro, idade, genero, pais))

cursor.executemany("""
INSERT INTO usuarios (nome, email, data_cadastro, idade, genero, pais)
VALUES (?, ?, ?, ?, ?, ?)""", usuarios)

# Cursos
cursos = []
for _ in range(50):
    titulo = fake.sentence(nb_words=3)
    categoria = random.choice(categorias)
    nivel = random.choice(niveis)
    duracao = round(random.uniform(1.5, 40.0), 1)
    instrutor = fake.name()
    cursos.append((titulo, categoria, nivel, duracao, instrutor))

cursor.executemany("""
INSERT INTO cursos (titulo, categoria, nivel, duracao_horas, instrutor)
VALUES (?, ?, ?, ?, ?)""", cursos)

# Matriculas
matriculas = []
avaliacoes = []
certificados = []

for usuario_id in range(1, 501):
    cursos_usuario = random.sample(range(1, 51), random.randint(1, 8))
    for curso_id in cursos_usuario:
        data_matricula = fake.date_between(start_date='-2y', end_date='today')
        status = random.choices(status_matricula, weights=[0.2, 0.6, 0.2])[0]
        matriculas.append((usuario_id, curso_id, data_matricula, status))

        if status == 'concluída':
            # Avaliação
            nota = random.randint(1, 5)
            comentario = fake.sentence()
            data_avaliacao = data_matricula + timedelta(days=random.randint(5, 90))
            avaliacoes.append((usuario_id, curso_id, nota, comentario, data_avaliacao))

            # Certificado (80% chance)
            if random.random() < 0.8:
                data_emissao = data_matricula + timedelta(days=random.randint(20, 180))
                certificados.append((usuario_id, curso_id, data_emissao))

# Inserção
cursor.executemany("""
INSERT INTO matriculas (id_usuario, id_curso, data_matricula, status)
VALUES (?, ?, ?, ?)""", matriculas)

cursor.executemany("""
INSERT INTO avaliacoes (id_usuario, id_curso, nota, comentario, data_avaliacao)
VALUES (?, ?, ?, ?, ?)""", avaliacoes)

cursor.executemany("""
INSERT INTO certificados (id_usuario, id_curso, data_emissao)
VALUES (?, ?, ?)""", certificados)

conn.commit()
conn.close()

print("Base de dados 'eduplus.db' criada com sucesso.")
