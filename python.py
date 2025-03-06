import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
import sqlite3

# Configuração do banco de dados (uso global da conexão)
conn = sqlite3.connect('filmes.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS filmes
             (titulo TEXT, status TEXT, vontade INTEGER, nota INTEGER, comentarios TEXT)''')
conn.commit()

def salvar_filme(janela, titulo, status, vontade, nota, comentarios, rowid=None):
    if not titulo or not vontade.isdigit() or not nota.isdigit():
        messagebox.showwarning("Erro", "Preencha os campos corretamente.")
        return
    
    vontade, nota = int(vontade), int(nota)

    if rowid:
        c.execute("UPDATE filmes SET titulo=?, status=?, vontade=?, nota=?, comentarios=? WHERE rowid=?", 
                  (titulo, status, vontade, nota, comentarios, rowid))
    else:
        c.execute("INSERT INTO filmes VALUES (?, ?, ?, ?, ?)", (titulo, status, vontade, nota, comentarios))

    conn.commit()
    janela.destroy()
    atualizar_lista()

def abrir_janela_filme(titulo='', status='Deseja Assistir', vontade='', nota='', comentarios='', rowid=None):
    janela = Toplevel(root)
    janela.title("Editar Filme" if rowid else "Adicionar Filme")

    labels = ["Título", "Status", "Vontade (1-5)", "Nota (1-10)", "Comentários"]
    for i, texto in enumerate(labels):
        tk.Label(janela, text=texto).grid(row=i, column=0, padx=5, pady=5, sticky="w")

    entry_titulo = tk.Entry(janela); entry_titulo.insert(0, titulo)
    entry_titulo.grid(row=0, column=1, padx=5, pady=5)

    var_status = tk.StringVar(value=status)
    tk.OptionMenu(janela, var_status, "Deseja Assistir", "Já Assistiu").grid(row=1, column=1, padx=5, pady=5)

    entry_vontade = tk.Entry(janela); entry_vontade.insert(0, vontade)
    entry_vontade.grid(row=2, column=1, padx=5, pady=5)

    entry_nota = tk.Entry(janela); entry_nota.insert(0, nota)
    entry_nota.grid(row=3, column=1, padx=5, pady=5)

    entry_comentarios = tk.Text(janela, height=5, width=30)
    entry_comentarios.insert(tk.END, comentarios)
    entry_comentarios.grid(row=4, column=1, padx=5, pady=5)

    tk.Button(janela, text="Salvar", command=lambda: salvar_filme(
        janela, entry_titulo.get(), var_status.get(), entry_vontade.get(), entry_nota.get(), entry_comentarios.get("1.0", tk.END), rowid)
    ).grid(row=5, column=0, columnspan=2, pady=10)

def editar_filme():
    selecionados = tree.selection()
    if not selecionados:
        messagebox.showwarning("Erro", "Selecione um filme para editar.")
        return

    item = selecionados[0]
    valores = tree.item(item, 'values')
    abrir_janela_filme(valores[1], valores[2], valores[3], valores[4], valores[5], valores[0])

def remover_filme():
    selecionados = tree.selection()
    if not selecionados:
        messagebox.showwarning("Erro", "Selecione um filme para remover.")
        return

    if messagebox.askyesno("Confirmação", "Remover filme(s) selecionado(s)?"):
        rowids = [(tree.item(item, 'values')[0],) for item in selecionados]
        c.executemany("DELETE FROM filmes WHERE rowid=?", rowids)
        conn.commit()
        atualizar_lista()

def atualizar_lista():
    tree.delete(*tree.get_children())
    for filme in c.execute("SELECT rowid, * FROM filmes").fetchall():
        tree.insert("", "end", values=filme)

# Configuração da interface
root = tk.Tk()
root.title("Lista de Filmes")

# Definir tamanho inicial da janela
root.geometry("800x400")  # Largura x Altura (Ajuste conforme necessário)
root.minsize(600, 300)  # Tamanho mínimo permitido


frame_botoes = tk.Frame(root)
frame_botoes.pack(anchor='w', padx=5, pady=5)

tk.Button(frame_botoes, text="Adicionar", command=lambda: abrir_janela_filme()).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botoes, text="Editar", command=editar_filme).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botoes, text="Remover", command=remover_filme).pack(side=tk.LEFT, padx=5)

frame_tabela = tk.Frame(root)
frame_tabela.pack(expand=True, fill="both", padx=5, pady=5)

# Definição das colunas e ajuste de larguras
colunas = ("ID", "Título", "Status", "Vontade", "Nota", "Comentários")
tree = ttk.Treeview(frame_tabela, columns=colunas, show='headings', height=10)

tree.heading("ID", text="ID")
tree.column("ID", anchor="center", width=50, minwidth=50, stretch=False)

tree.heading("Título", text="Título")
tree.column("Título", anchor="w", width=200, minwidth=150, stretch=True)

tree.heading("Status", text="Status")
tree.column("Status", anchor="center", width=120, minwidth=100, stretch=True)

tree.heading("Vontade", text="Vontade")
tree.column("Vontade", anchor="center", width=60, minwidth=50, stretch=False)

tree.heading("Nota", text="Nota")
tree.column("Nota", anchor="center", width=60, minwidth=50, stretch=False)

tree.heading("Comentários", text="Comentários")
tree.column("Comentários", anchor="w", width=250, minwidth=150, stretch=True)


for col in colunas:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=120 if col == "Título" else 80)

# Adicionando scrollbar
scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

tree.pack(expand=True, fill="both")
atualizar_lista()

root.mainloop()

conn.close()
