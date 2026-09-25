import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# --- BANCO DE DADOS ---
def conectar_bd():
    conn = sqlite3.connect("gestao_toldos.db")
    cursor = conn.cursor()
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT,
            detalhes TEXT,
            entrada REAL DEFAULT 0.0
        )
    ''')
    
    # Tabela de Gastos com vínculo ao cliente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()

# --- FUNÇÕES ---
def salvar_cliente():
    nome = entry_nome.get()
    tel = entry_tel.get()
    end = entry_end.get()
    detalhes = entry_detalhes.get()
    entrada_str = entry_entrada.get()

    if not nome:
        messagebox.showwarning("Aviso", "O nome do cliente é obrigatório!")
        return

    try:
        entrada_val = float(entrada_str.replace(",", ".")) if entrada_str else 0.0
    except ValueError:
        messagebox.showerror("Erro", "Valor de entrada inválido!")
        return

    conn = sqlite3.connect("gestao_toldos.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, telefone, endereco, detalhes, entrada) VALUES (?, ?, ?, ?, ?)",
        (nome, tel, end, detalhes, entrada_val)
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Sucesso", "Cliente registrado com sucesso!")
    limpar_campos_cliente()
    carregar_clientes()
    atualizar_combobox_clientes()
    atualizar_resumo_geral()

def zerar_banco_de_dados():
    # Pede a senha do administrador
    senha = simpledialog.askstring("Acesso Restrito", "Digite a senha de administrador:", show="*")
    
    # Você pode alterar a senha "1234" abaixo para a senha que desejar
    if senha != "6900":
        if senha is not None:  # Não exibe erro se o usuário clicar em Cancelar
            messagebox.showerror("Erro", "Senha incorreta! Acesso negado.")
        return

    # Se a senha estiver correta, solicita confirmação
    confirmar = messagebox.askyesno(
        "Atenção!", 
        "Senha confirmada!\n\nDeseja realmente apagar TODOS os clientes e gastos do sistema?"
    )
    if confirmar:
        conn = sqlite3.connect("gestao_toldos.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gastos")
        cursor.execute("DELETE FROM clientes")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='gastos' OR name='clientes'")
        conn.commit()
        conn.close()

        messagebox.showinfo("Sistema Zerado", "Todos os dados foram apagados com sucesso!")
        
        # Atualiza a tela
        carregar_clientes()
        atualizar_combobox_clientes()
        atualizar_resumo_geral()
        
        combo_filtro_cliente.set('')
        for linha in tabela_gastos_obra.get_children():
            tabela_gastos_obra.delete(linha)
        lbl_obra_entrada.config(text="R$ 0,00")
        lbl_obra_gastos.config(text="R$ 0,00")
        lbl_obra_saldo.config(text="R$ 0,00")

def excluir_cliente():
    item_selecionado = tabela_clientes.selection()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Selecione um cliente na tabela para excluir!")
        return

    cliente_valores = tabela_clientes.item(item_selecionado, "values")
    cliente_id = cliente_valores[0]
    cliente_nome = cliente_valores[1]

    confirmar = messagebox.askyesno(
        "Confirmar Exclusão", 
        f"Tem certeza que deseja excluir o cliente '{cliente_nome}' e todos os gastos vinculados a ele?"
    )

    if confirmar:
        conn = sqlite3.connect("gestao_toldos.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        cursor.execute("DELETE FROM gastos WHERE cliente_id = ?", (cliente_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Cliente e seus gastos foram excluídos com sucesso!")
        carregar_clientes()
        atualizar_combobox_clientes()
        atualizar_resumo_geral()
        
        combo_filtro_cliente.set('')
        for linha in tabela_gastos_obra.get_children():
            tabela_gastos_obra.delete(linha)
        lbl_obra_entrada.config(text="R$ 0,00")
        lbl_obra_gastos.config(text="R$ 0,00")
        lbl_obra_saldo.config(text="R$ 0,00")

def ver_gastos_cliente_selecionado():
    item_selecionado = tabela_clientes.selection()
    if not item_selecionado:
        messagebox.showwarning("Aviso", "Selecione um cliente na tabela primeiro!")
        return

    cliente_valores = tabela_clientes.item(item_selecionado, "values")
    cliente_id = cliente_valores[0]
    cliente_nome = cliente_valores[1]

    combo_filtro_cliente.set(f"{cliente_id} - {cliente_nome}")
    filtrar_gastos_por_cliente()
    notebook.select(aba_gastos_obra)

def salvar_gasto():
    cliente_selecionado = combo_gasto_cliente.get()
    desc = entry_gasto_desc.get()
    valor_str = entry_gasto_valor.get()
    data = entry_gasto_data.get()

    if not cliente_selecionado:
        messagebox.showwarning("Aviso", "Selecione o cliente/obra referente ao gasto!")
        return

    if not desc or not valor_str:
        messagebox.showwarning("Aviso", "Descrição e Valor são obrigatórios!")
        return

    try:
        valor_float = float(valor_str.replace(",", "."))
    except ValueError:
        messagebox.showerror("Erro", "Valor de gasto inválido!")
        return

    cliente_id = int(cliente_selecionado.split(" - ")[0])

    conn = sqlite3.connect("gestao_toldos.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO gastos (cliente_id, descricao, valor, data) VALUES (?, ?, ?, ?)",
        (cliente_id, desc, valor_float, data)
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Sucesso", "Gasto registrado com sucesso para a obra!")
    limpar_campos_gasto()
    atualizar_resumo_geral()
    filtrar_gastos_por_cliente()

def carregar_clientes():
    for linha in tabela_clientes.get_children():
        tabela_clientes.delete(linha)

    conn = sqlite3.connect("gestao_toldos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, telefone, endereco, detalhes, entrada FROM clientes")
    registros = cursor.fetchall()
    conn.close()

    for r in registros:
        entrada_fmt = f"R$ {r[5]:,.2f}".replace(".", "v").replace(",", ".").replace("v", ",")
        tabela_clientes.insert("", tk.END, values=(r[0], r[1], r[2], r[3], r[4], entrada_fmt))

def atualizar_combobox_clientes():
    conn = sqlite3.connect("gestao_toldos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes")
    clientes = cursor.fetchall()
    conn.close()

    lista_formatada = [f"{c[0]} - {c[1]}" for c in clientes]
    combo_gasto_cliente['values'] = lista_formatada
    combo_filtro_cliente['values'] = lista_formatada

def filtrar_gastos_por_cliente(event=None):
    cliente_selecionado = combo_filtro_cliente.get()
    if not cliente_selecionado:
        return

    cliente_id = int(cliente_selecionado.split(" - ")[0])

    for linha in tabela_gastos_obra.get_children():
        tabela_gastos_obra.delete(linha)

    conn = sqlite3.connect("gestao_toldos.db")
    cursor = conn.cursor()

    cursor.execute("SELECT entrada FROM clientes WHERE id = ?", (cliente_id,))
    res_cliente = cursor.fetchone()
    entrada = res_cliente[0] if res_cliente else 0.0

    cursor.execute("SELECT descricao, valor, data FROM gastos WHERE cliente_id = ?", (cliente_id,))
    gastos = cursor.fetchall()
    conn.close()

    total_gastos_obra = 0.0
    for g in gastos:
        valor_fmt = f"R$ {g[1]:,.2f}".replace(".", "v").replace(",", ".").replace("v", ",")
        tabela_gastos_obra.insert("", tk.END, values=(g[0], valor_fmt, g[2]))
        total_gastos_obra += g[1]

    saldo_obra = entrada - total_gastos_obra

    lbl_obra_entrada.config(text=f"R$ {entrada:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))
    lbl_obra_gastos.config(text=f"R$ {total_gastos_obra:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))
    lbl_obra_saldo.config(text=f"R$ {saldo_obra:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))

    if saldo_obra < 0:
        lbl_obra_saldo.config(foreground="red")
    else:
        lbl_obra_saldo.config(foreground="green")

def atualizar_resumo_geral():
    conn = sqlite3.connect("gestao_toldos.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(entrada) FROM clientes")
    total_entradas = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(valor) FROM gastos")
    total_gastos = cursor.fetchone()[0] or 0.0

    conn.close()

    saldo = total_entradas - total_gastos

    lbl_total_entradas.config(text=f"R$ {total_entradas:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))
    lbl_total_gastos.config(text=f"R$ {total_gastos:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))
    lbl_saldo.config(text=f"R$ {saldo:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))

    if saldo < 0:
        lbl_saldo.config(foreground="red")
    else:
        lbl_saldo.config(foreground="green")

def limpar_campos_cliente():
    entry_nome.delete(0, tk.END)
    entry_tel.delete(0, tk.END)
    entry_end.delete(0, tk.END)
    entry_detalhes.delete(0, tk.END)
    entry_entrada.delete(0, tk.END)

def limpar_campos_gasto():
    combo_gasto_cliente.set('')
    entry_gasto_desc.delete(0, tk.END)
    entry_gasto_valor.delete(0, tk.END)
    entry_gasto_data.delete(0, tk.END)

# --- INTERFACE GRÁFICA ---
conectar_bd()

janela = tk.Tk()
janela.title("Controle de Gestão - Loja de Toldos")
janela.geometry("800x580")

notebook = ttk.Notebook(janela)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# ABA 1: CLIENTES
aba_clientes = ttk.Frame(notebook)
notebook.add(aba_clientes, text=" Cadastrar Cliente ")

ttk.Label(aba_clientes, text="Nome do Cliente:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
entry_nome = ttk.Entry(aba_clientes, width=40)
entry_nome.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(aba_clientes, text="Telefone / WhatsApp:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_tel = ttk.Entry(aba_clientes, width=40)
entry_tel.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(aba_clientes, text="Endereço:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_end = ttk.Entry(aba_clientes, width=40)
entry_end.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(aba_clientes, text="Detalhes do Toldo / Medidas:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
entry_detalhes = ttk.Entry(aba_clientes, width=40)
entry_detalhes.grid(row=3, column=1, padx=10, pady=5)

ttk.Label(aba_clientes, text="Entrada / Sinal Pago (R$):").grid(row=4, column=0, sticky="w", padx=10, pady=5)
entry_entrada = ttk.Entry(aba_clientes, width=40)
entry_entrada.grid(row=4, column=1, padx=10, pady=5)

btn_salvar_cliente = ttk.Button(aba_clientes, text="Salvar Cliente e Entrada", command=salvar_cliente)
btn_salvar_cliente.grid(row=5, column=0, columnspan=2, pady=20)

# ABA 2: LISTAR CLIENTES
aba_lista_clientes = ttk.Frame(notebook)
notebook.add(aba_lista_clientes, text=" Clientes Salvos ")

colunas = ("ID", "Nome", "Telefone", "Endereço", "Detalhes", "Entrada")
tabela_clientes = ttk.Treeview(aba_lista_clientes, columns=colunas, show="headings", height=13)

tabela_clientes.heading("ID", text="ID")
tabela_clientes.heading("Nome", text="Nome")
tabela_clientes.heading("Telefone", text="Telefone")
tabela_clientes.heading("Endereço", text="Endereço")
tabela_clientes.heading("Detalhes", text="Detalhes/Medidas")
tabela_clientes.heading("Entrada", text="Entrada (R$)")

tabela_clientes.column("ID", width=35, anchor="center")
tabela_clientes.column("Nome", width=120)
tabela_clientes.column("Telefone", width=100)
tabela_clientes.column("Endereço", width=150)
tabela_clientes.column("Detalhes", width=180)
tabela_clientes.column("Entrada", width=90, anchor="e")

tabela_clientes.pack(fill="both", expand=True, padx=10, pady=10)

frame_botoes_cliente = ttk.Frame(aba_lista_clientes)
frame_botoes_cliente.pack(fill="x", padx=10, pady=5)

btn_ver_gastos = ttk.Button(frame_botoes_cliente, text="Ver Gastos da Obra", command=ver_gastos_cliente_selecionado)
btn_ver_gastos.pack(side="left", padx=5)

btn_excluir_cliente = ttk.Button(frame_botoes_cliente, text="Excluir Cliente Selecionado", command=excluir_cliente)
btn_excluir_cliente.pack(side="right", padx=5)

# ABA 3: REGISTRAR GASTO
aba_gastos = ttk.Frame(notebook)
notebook.add(aba_gastos, text=" Registrar Gasto ")

ttk.Label(aba_gastos, text="Selecione o Cliente/Obra:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
combo_gasto_cliente = ttk.Combobox(aba_gastos, width=38, state="readonly")
combo_gasto_cliente.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(aba_gastos, text="Descrição do Gasto (ex: Lona, Metalon):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_gasto_desc = ttk.Entry(aba_gastos, width=40)
entry_gasto_desc.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(aba_gastos, text="Valor (R$):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
entry_gasto_valor = ttk.Entry(aba_gastos, width=40)
entry_gasto_valor.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(aba_gastos, text="Data (DD/MM/AAAA):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
entry_gasto_data = ttk.Entry(aba_gastos, width=40)
entry_gasto_data.grid(row=3, column=1, padx=10, pady=5)

btn_salvar_gasto = ttk.Button(aba_gastos, text="Salvar Gasto da Obra", command=salvar_gasto)
btn_salvar_gasto.grid(row=4, column=0, columnspan=2, pady=20)

# ABA 4: GASTOS POR OBRA/CLIENTE
aba_gastos_obra = ttk.Frame(notebook)
notebook.add(aba_gastos_obra, text=" Gastos por Obra ")

frame_topo_filtro = ttk.Frame(aba_gastos_obra)
frame_topo_filtro.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_topo_filtro, text="Selecione o Cliente/Obra:").pack(side="left", padx=5)
combo_filtro_cliente = ttk.Combobox(frame_topo_filtro, width=35, state="readonly")
combo_filtro_cliente.pack(side="left", padx=5)
combo_filtro_cliente.bind("<<ComboboxSelected>>", filtrar_gastos_por_cliente)

colunas_gasto = ("Descrição", "Valor", "Data")
tabela_gastos_obra = ttk.Treeview(aba_gastos_obra, columns=colunas_gasto, show="headings", height=8)
tabela_gastos_obra.heading("Descrição", text="Descrição do Material / Serviço")
tabela_gastos_obra.heading("Valor", text="Valor (R$)")
tabela_gastos_obra.heading("Data", text="Data")

tabela_gastos_obra.column("Descrição", width=350)
tabela_gastos_obra.column("Valor", width=120, anchor="e")
tabela_gastos_obra.column("Data", width=100, anchor="center")
tabela_gastos_obra.pack(fill="both", expand=True, padx=10, pady=5)

frame_resumo_obra = ttk.LabelFrame(aba_gastos_obra, text=" Resumo da Obra Selecionada ")
frame_resumo_obra.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_resumo_obra, text="Entrada Recebida:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
lbl_obra_entrada = ttk.Label(frame_resumo_obra, text="R$ 0,00", font=("Arial", 10, "bold"), foreground="blue")
lbl_obra_entrada.grid(row=0, column=1, padx=10, pady=5, sticky="w")

ttk.Label(frame_resumo_obra, text="Total de Gastos na Obra:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
lbl_obra_gastos = ttk.Label(frame_resumo_obra, text="R$ 0,00", font=("Arial", 10, "bold"), foreground="orange")
lbl_obra_gastos.grid(row=0, column=3, padx=10, pady=5, sticky="w")

ttk.Label(frame_resumo_obra, text="Saldo Restante da Entrada:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
lbl_obra_saldo = ttk.Label(frame_resumo_obra, text="R$ 0,00", font=("Arial", 11, "bold"))
lbl_obra_saldo.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# ABA 5: RESUMO GERAL
aba_resumo = ttk.Frame(notebook)
notebook.add(aba_resumo, text=" Caixa Geral ")

ttk.Label(aba_resumo, text="Total Recebido (Todas as Entradas):", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=15, pady=15)
lbl_total_entradas = ttk.Label(aba_resumo, text="R$ 0,00", font=("Arial", 11, "bold"), foreground="blue")
lbl_total_entradas.grid(row=0, column=1, sticky="w", padx=15, pady=15)

ttk.Label(aba_resumo, text="Total de Gastos em Materiais:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=15, pady=15)
lbl_total_gastos = ttk.Label(aba_resumo, text="R$ 0,00", font=("Arial", 11, "bold"), foreground="orange")
lbl_total_gastos.grid(row=1, column=1, sticky="w", padx=15, pady=15)

ttk.Label(aba_resumo, text="------------------------------------------------", font=("Arial", 11)).grid(row=2, column=0, columnspan=2, padx=15)

ttk.Label(aba_resumo, text="SALDO GERAL EM CAIXA:", font=("Arial", 13, "bold")).grid(row=3, column=0, sticky="w", padx=15, pady=15)
lbl_saldo = ttk.Label(aba_resumo, text="R$ 0,00", font=("Arial", 13, "bold"))
lbl_saldo.grid(row=3, column=1, sticky="w", padx=15, pady=15)

# Botão protegido por senha
btn_zerar_bd = ttk.Button(aba_resumo, text="🔒 Configurações Avançadas (Zerar Sistema)", command=zerar_banco_de_dados)
btn_zerar_bd.grid(row=4, column=0, columnspan=2, pady=30, padx=15)

# Inicialização
carregar_clientes()
atualizar_combobox_clientes()
atualizar_resumo_geral()

janela.mainloop()