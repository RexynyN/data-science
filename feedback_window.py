import os
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Style
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
from os.path import isdir, join

CLASS1 = "Memory"
CLASS2 = "Garbage"
PATH1 = "memories"
PATH2 = "garbage"

path = ""
index = 0
files = []

def path_handler():
    global path, files, index
    try:
        path = askdirectory(mustexist=True)
        if not isdir(join(path, PATH1)) or not isdir(join(path, PATH2)):
            messagebox.showerror("Erro de pasta", "A pasta especificada não possui as subpastas 'memories' e 'garbage'")
            return

        slice1 = [join(path, PATH1, foile) for foile in os.listdir(join(path, PATH1))]
        slice2 = [join(path, PATH2, foile) for foile in os.listdir(join(path, PATH2))]
        files = slice1 + slice2 
        index = 0
    except FileNotFoundError:
        messagebox.showerror("Erro de Arquivos", "O caminho especificado não existe ou não possui arquivos")
        return

def render_next(pic=None):
    global files, index

    if not pic:
        index += 1
        pic = index

    imagem = Image.open(files[pic])  
    imagem = imagem.resize((500, 300), Image.LANCZOS)
    imagem = ImageTk.PhotoImage(imagem)

    label_imagem.configure(image=imagem)
    label_imagem.image = imagem

def handle_memory():
    global files, index
    if files[index].find(PATH1) == -1:
        os.rename(files[index], files[index].replace(PATH2, PATH1))
        files[index] = files[index].replace(PATH2, PATH1)

    render_next()

def handle_garbage():
    global files, index
    if files[index].find(PATH2) == -1:
        os.rename(files[index], files[index].replace(PATH1, PATH2))
        files[index] = files[index].replace(PATH1, PATH2)

    render_next()

def handle_back():
    global index
    index -= 1
    render_next(index)


def handle_forward():
    global index
    index += 1
    render_next(index)

# Criar a janela principal
janela = tk.Tk()
janela.title("Interface com Tkinter")

# Define o estilo
estilo = Style()
estilo.configure("TFrame", background="#f0f0f0", relief="solid", borderwidth=1)
estilo.configure("TLabel", background="#f0f0f0", padding=10)
estilo.configure("TButton", background="#dddddd", padding=5)

# Define as margens da janela
margem_superior = 20
margem_inferior = 20
margem_esquerda = 20
margem_direita = 20
janela.geometry(f"+{margem_esquerda}+{margem_superior}")

# Botão centralizado no topo
botao_topo = tk.Button(janela, text="Procurar Imagens", command=path_handler)
botao_topo.pack(pady=20)

# Renderizar a imagem
imagem = Image.open("floppa.jpg") 
imagem = imagem.resize((500, 300), Image.LANCZOS) 
imagem = ImageTk.PhotoImage(imagem)

label_imagem = tk.Label(janela, image=imagem)
label_imagem.pack(pady=20, padx=20)

# Dois botões lado a lado
frame_botoes = tk.Frame(janela)
frame_botoes.pack()

backButton = tk.Button(frame_botoes, text="<< Voltar", command=handle_back)
backButton.pack(side=tk.LEFT, padx=10, pady=20)

mbutton = tk.Button(frame_botoes, text=CLASS1, command=handle_memory)
mbutton.pack(side=tk.LEFT, padx=10, pady=20)

gbutton = tk.Button(frame_botoes, text=CLASS2, command=handle_garbage)
gbutton.pack(side=tk.LEFT, padx=10, pady=20)

forwardButton = tk.Button(frame_botoes, text="Pular >>", command=handle_forward)
forwardButton.pack(side=tk.LEFT, padx=10, pady=20)

# Binda o callback para mudar a foto do frame
janela.bind("<Return>", render_next)

# Iniciar o loop principal da aplicação
janela.mainloop()