"""
Editor/Visualizador de ZPL com interface gráfica.

Funcionalidades:
    - Selecionar um arquivo .zpl pelo Explorer
    - Ver o preview renderizado da etiqueta (via API do Labelary)
    - Ver a quantidade atual definida no comando ^PQ (tag de quantidade)
    - Definir uma nova quantidade e salvar como um NOVO arquivo .zpl,
      sem sobrescrever o original.

Requisitos:
    pip install requests pillow --break-system-packages

Como executar:
    python zpl_editor_gui.py
"""

import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from io import BytesIO

import requests
from PIL import Image, ImageTk


LABELARY_URL = "http://api.labelary.com/v1/printers/{dpmm}dpmm/labels/{width}x{height}/{index}/"

# Regex para localizar o comando de quantidade: ^PQq,p,r,o,e
# q = quantidade total a imprimir (o único valor obrigatório)
PQ_REGEX = re.compile(r"\^PQ\s*(\d+)([^^]*)")


def extrair_quantidade(zpl_texto: str):
    """Retorna (quantidade_atual, encontrou_tag) a partir do texto ZPL."""
    m = PQ_REGEX.search(zpl_texto)
    if m:
        return int(m.group(1)), True
    return 1, False  # ZPL sem ^PQ imprime 1 etiqueta por padrão


def substituir_quantidade(zpl_texto: str, nova_qtd: int) -> str:
    """Retorna uma NOVA string ZPL com a quantidade alterada.
    Se não existir ^PQ, insere um antes do primeiro ^XZ encontrado."""
    m = PQ_REGEX.search(zpl_texto)
    if m:
        resto = m.group(2)  # mantém eventuais parâmetros extras (,p,r,o,e)
        novo_comando = f"^PQ{nova_qtd}{resto}"
        return zpl_texto[: m.start()] + novo_comando + zpl_texto[m.end() :]

    # Não havia ^PQ: insere um novo comando antes do primeiro ^XZ
    idx = zpl_texto.find("^XZ")
    novo_comando = f"^PQ{nova_qtd}\n"
    if idx == -1:
        # Não encontrou ^XZ (arquivo fora do padrão) -> só acrescenta no final
        return zpl_texto + "\n" + novo_comando
    return zpl_texto[:idx] + novo_comando + zpl_texto[idx:]


def renderizar_preview(zpl_texto: str, dpmm: int, largura: float, altura: float) -> Image.Image:
    """Chama a API do Labelary e retorna a primeira etiqueta como imagem PIL."""
    url = LABELARY_URL.format(dpmm=dpmm, width=largura, height=altura, index=0)
    headers = {
        "Accept": "image/png",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = requests.post(url, data=zpl_texto.encode("utf-8"), headers=headers, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"Erro {resp.status_code} da API Labelary: {resp.text[:300]}")
    return Image.open(BytesIO(resp.content))


class ZplEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Quantidade ZPL")
        self.geometry("580x720")
        self.resizable(True, True)  # Permitir redimensionamento

        self.caminho_entrada = None
        self.zpl_original = None
        self.preview_imgtk = None  # precisa manter referência viva

        self._montar_widgets()

    # ---------- UI ----------
    def _montar_widgets(self):
        # Container principal com Scrollbar para garantir que nada suma da tela
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(container)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Habilitar rolagem com a roda do mouse
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        pad = {"padx": 10, "pady": 6}

        # Seleção de arquivo
        frame_arquivo = ttk.LabelFrame(self.scrollable_frame, text="1. Arquivo ZPL de entrada")
        frame_arquivo.pack(fill="x", **pad)

        self.lbl_arquivo = ttk.Label(frame_arquivo, text="Nenhum arquivo selecionado", foreground="gray")
        self.lbl_arquivo.pack(side="left", padx=8, pady=8)

        ttk.Button(frame_arquivo, text="Selecionar arquivo...", command=self.selecionar_arquivo).pack(
            side="right", padx=8, pady=8
        )

        # Parâmetros de renderização
        frame_params = ttk.LabelFrame(self.scrollable_frame, text="2. Parâmetros da etiqueta (para o preview)")
        frame_params.pack(fill="x", **pad)

        ttk.Label(frame_params, text="Densidade (dpmm):").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.var_dpmm = tk.StringVar(value="8")
        ttk.Combobox(
            frame_params, textvariable=self.var_dpmm, values=["6", "8", "12", "24"], width=6, state="readonly"
        ).grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(frame_params, text="Largura (pol):").grid(row=0, column=2, sticky="w", padx=8, pady=4)
        self.var_largura = tk.StringVar(value="4")
        ttk.Entry(frame_params, textvariable=self.var_largura, width=6).grid(row=0, column=3, sticky="w", pady=4)

        ttk.Label(frame_params, text="Altura (pol):").grid(row=0, column=4, sticky="w", padx=8, pady=4)
        self.var_altura = tk.StringVar(value="2")
        ttk.Entry(frame_params, textvariable=self.var_altura, width=6).grid(row=0, column=5, sticky="w", pady=4)

        ttk.Button(frame_params, text="Atualizar preview", command=self.atualizar_preview).grid(
            row=0, column=6, padx=8, pady=4
        )

        # Preview
        frame_preview = ttk.LabelFrame(self.scrollable_frame, text="3. Preview da etiqueta")
        frame_preview.pack(fill="both", expand=True, **pad)

        self.lbl_preview = ttk.Label(frame_preview, text="O preview aparece aqui após selecionar um arquivo.")
        self.lbl_preview.pack(expand=True, padx=8, pady=8)

        # Quantidade
        frame_qtd = ttk.LabelFrame(self.scrollable_frame, text="4. Quantidade de etiquetas")
        frame_qtd.pack(fill="x", **pad)

        self.lbl_qtd_atual = ttk.Label(frame_qtd, text="De: --")
        self.lbl_qtd_atual.grid(row=0, column=0, sticky="w", padx=8, pady=8)

        ttk.Label(frame_qtd, text="    →    Para:").grid(row=0, column=1, sticky="w", pady=8)

        self.var_nova_qtd = tk.StringVar(value="")
        self.entry_nova_qtd = ttk.Entry(frame_qtd, textvariable=self.var_nova_qtd, width=10, state="disabled")
        self.entry_nova_qtd.grid(row=0, column=2, sticky="w", padx=8, pady=8)

        # Salvar
        frame_salvar = ttk.Frame(self.scrollable_frame)
        frame_salvar.pack(fill="x", **pad)

        self.btn_salvar = ttk.Button(
            frame_salvar, text="Salvar novo arquivo ZPL...", command=self.salvar_novo_arquivo, state="disabled"
        )
        self.btn_salvar.pack(fill="x")

        # Barra de status
        self.var_status = tk.StringVar(value="Selecione um arquivo ZPL para começar.")
        ttk.Label(self.scrollable_frame, textvariable=self.var_status, foreground="gray").pack(fill="x", padx=10, pady=(0, 8))

    # ---------- Ações ----------
    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo ZPL",
            filetypes=[("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        try:
            with open(caminho, "r", encoding="utf-8", errors="replace") as f:
                conteudo = f.read()
        except Exception as e:
            messagebox.showerror("Erro ao ler arquivo", str(e))
            return

        self.caminho_entrada = caminho
        self.zpl_original = conteudo
        self.lbl_arquivo.config(text=caminho, foreground="black")

        qtd_atual, tinha_tag = extrair_quantidade(conteudo)
        texto_de = f"De: {qtd_atual}" + ("" if tinha_tag else "  (arquivo não tinha ^PQ, padrão é 1)")
        self.lbl_qtd_atual.config(text=texto_de)
        self.var_nova_qtd.set(str(qtd_atual))
        self.entry_nova_qtd.config(state="normal")
        self.btn_salvar.config(state="normal")

        self.atualizar_preview()

    def atualizar_preview(self):
        if not self.zpl_original:
            return

        try:
            dpmm = int(self.var_dpmm.get())
            largura = float(self.var_largura.get())
            altura = float(self.var_altura.get())
        except ValueError:
            messagebox.showerror("Parâmetros inválidos", "Verifique dpmm, largura e altura.")
            return

        self.var_status.set("Renderizando preview...")
        self.lbl_preview.config(image="", text="Carregando...")

        # Pega a quantidade real que o usuário definiu ou que veio no arquivo
        try:
            qtd_real = int(self.var_nova_qtd.get())
        except ValueError:
            qtd_real = 1

        # A API do Labelary aceita no máximo 50. Se for maior que 50,
        # geramos uma cópia temporária do ZPL com o ^PQ ajustado para 50 apenas para o preview.
        zpl_para_preview = self.zpl_original
        if qtd_real > 50:
            zpl_para_preview = substituir_quantidade(self.zpl_original, 50)

        def worker():
            try:
                # Envia o ZPL ajustado (máximo 50) para a API
                img = renderizar_preview(zpl_para_preview, dpmm, largura, altura)
                img.thumbnail((480, 480))
                imgtk = ImageTk.PhotoImage(img)
                self.after(0, lambda: self._exibir_preview(imgtk))
            except Exception as e:
                self.after(0, lambda: self._erro_preview(e))

        threading.Thread(target=worker, daemon=True).start()
    def _exibir_preview(self, imgtk):
        self.preview_imgtk = imgtk  # mantém referência para não ser coletado pelo GC
        self.lbl_preview.config(image=imgtk, text="")
        self.var_status.set("Preview atualizado.")

    def _erro_preview(self, erro):
        self.lbl_preview.config(text=f"Não foi possível renderizar o preview:\n{erro}")
        self.var_status.set("Falha ao renderizar preview (verifique sua conexão com a internet).")

    def salvar_novo_arquivo(self):
        if not self.zpl_original:
            return

        try:
            nova_qtd = int(self.var_nova_qtd.get())
            if nova_qtd < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Quantidade inválida", "Digite um número inteiro maior ou igual a 1.")
            return

        destino = filedialog.asksaveasfilename(
            title="Salvar novo arquivo ZPL",
            defaultextension=".zpl",
            filetypes=[("Arquivo ZPL", "*.zpl"), ("Todos os arquivos", "*.*")],
            initialfile="etiqueta_editada.zpl",
        )
        if not destino:
            return

        novo_conteudo = substituir_quantidade(self.zpl_original, nova_qtd)

        try:
            with open(destino, "w", encoding="utf-8") as f:
                f.write(novo_conteudo)
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))
            return

        self.var_status.set(f"Salvo em: {destino}")
        messagebox.showinfo(
            "Concluído",
            f"Novo arquivo salvo com sucesso!\n\nQuantidade alterada para: {nova_qtd}\n"
            f"Arquivo original preservado em:\n{self.caminho_entrada}",
        )


if __name__ == "__main__":
    app = ZplEditorApp()
    app.mainloop()
