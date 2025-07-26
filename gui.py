import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
from excel_utils import read_excel, salvar_planilha
from scraper import fetch_data, cancel_search_event
from selenium import webdriver
import webbrowser
import os
import pandas as pd


class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Buscador Reflora")
        self.root.resizable(False, False)
        
        # ===== CONFIGURAÇÃO DE CORES PERSONALIZADAS =====
        # Cores principais do tema personalizado
        self.colors = {
            'primary': '#52C79A',           # Verde menta principal
            'secondary': '#95D5B2',         # Verde menta claro
            'success': '#52C79A',           # Verde sucesso
            'info': '#74C0FC',             # Azul info
            'warning': '#FFD43B',          # Amarelo aviso
            'danger': '#FF6B6B',           # Vermelho erro
            'light': '#F0F8F0',            # ===== FUNDO VERDINHO CLARINHO =====
            'dark': '#495057',             # Texto escuro
            'button_green': '#8FBC8F',     # Verde oliva claro para botões
            'button_hover': '#7AA67A',     # Verde oliva mais escuro para hover
            'progress_bg': '#E9ECEF',      # Fundo da barra de progresso
        }
        
        # Aplicar estilo personalizado
        self.setup_custom_styles()
        
        # Variáveis
        self.file_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Pronto para buscar")
        self.use_headless = tk.BooleanVar(value=True)
        self.sheet_names = []
        self.dataframes = {}
        self.selected_sheets = []
        self.progress_value = tk.IntVar(value=0)
        self.progress_max = tk.IntVar(value=100)

        # Interface
        self.build_gui()
        self.show_cache_stats()

    def setup_custom_styles(self):
        """Configura estilos personalizados para os widgets"""
        style = ttk.Style()
        
        # ===== FORÇAR FUNDO VERDINHO EM TODA A INTERFACE =====
        # Configurar tema para usar fundo verdinho
        style.theme_use('minty')
        style.configure('.', background=self.colors['light'])  # Fundo verdinho para todos os widgets
        
        # ===== ESTILO DOS BOTÕES =====
        # Botão principal com verde oliva claro
        style.configure(
            "Custom.TButton",
            background=self.colors['button_green'],     # Cor de fundo verde oliva claro
            foreground='white',                         # Texto branco
            borderwidth=1,
            focuscolor='none',
            font=('Segoe UI', 9, 'bold')
        )
        
        # Efeito hover para botões
        style.map(
            "Custom.TButton",
            background=[('active', self.colors['button_hover'])],  # Cor quando hover
            relief=[('pressed', 'flat'), ('!pressed', 'raised')]
        )
        
        # ===== ESTILO DA BARRA DE PROGRESSO =====
        # Configuração da barra de progresso personalizada
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background=self.colors['primary'],          # Verde menta para progresso
            troughcolor=self.colors['progress_bg'],     # Fundo cinza claro
            borderwidth=1,
            lightcolor=self.colors['primary'],
            darkcolor=self.colors['primary'],
            thickness=25                                # Altura da barra
        )
        
        # ===== ESTILO DOS LABELS =====
        # Labels com texto mais escuro para melhor legibilidade
        style.configure(
            "Custom.TLabel",
            background=self.colors['light'],            # Fundo claro
            foreground=self.colors['dark'],             # Texto escuro
            font=('Segoe UI', 9)
        )
        
        # ===== ESTILO DOS CHECKBUTTONS =====
        # Checkbox personalizado
        style.configure(
            "Custom.TCheckbutton",
            background=self.colors['light'],            # Fundo claro
            foreground=self.colors['dark'],             # Texto escuro
            focuscolor='none',
            font=('Segoe UI', 9)
        )
        
        # ===== ESTILO DOS ENTRIES =====
        # Campo de entrada personalizado
        style.configure(
            "Custom.TEntry",
            relief='solid',
            borderwidth=1,
            insertcolor=self.colors['dark'],            # Cor do cursor
            font=('Segoe UI', 9)
        )

    def build_gui(self):
        # ===== FRAME PRINCIPAL COM COR DE FUNDO VERDINHA =====
        self.root.geometry("700x450")  # Largura x Altura
        
        # Frame principal com fundo verdinho clarinho

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.configure(style="Custom.TFrame")
        main_frame.grid()
        
        # ===== CONFIGURAR COR DE FUNDO DA JANELA PRINCIPAL =====
        # Configurar cor de fundo verdinha da janela principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.configure(bg=self.colors['light'])    # Fundo verdinho clarinho


        # ===== BOTÃO DE CRÉDITOS =====
        # Botão de informações no canto superior direito
        credits_btn = ttk.Button(
            main_frame, 
            text="ℹ", 
            width=2, 
            command=self.show_credits,
            style="Custom.TButton"                      # Aplicar estilo personalizado
        )
        credits_btn.grid(row=0, column=2, sticky="ne", pady=(0, 10))

        # ===== SEÇÃO DE SELEÇÃO DE ARQUIVO =====
        # Label para seleção de arquivo
        ttk.Label(
            main_frame, 
            text="Planilha com nomes científicos:",
            style="Custom.TLabel"                       # Estilo personalizado para labels
        ).grid(row=1, column=0, sticky="w")
        
        # Campo de entrada para caminho do arquivo
        ttk.Entry(
            main_frame, 
            textvariable=self.file_path, 
            width=60,
            style="Custom.TEntry"                       # Estilo personalizado para entries
        ).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Botão para selecionar arquivo
        ttk.Button(
            main_frame, 
            text="Selecionar arquivo", 
            command=self.choose_file,
            style="Custom.TButton"                      # Botão com verde oliva
        ).grid(row=2, column=2, padx=5)

        # ===== CHECKBOX PARA MODO HEADLESS =====
        # Checkbox para executar com navegador oculto
        ttk.Checkbutton(
            main_frame,
            text="Executar com navegador oculto (headless)",
            variable=self.use_headless,
            style="Custom.TCheckbutton"                 # Estilo personalizado para checkbox
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=5)

        # ===== SEÇÃO DE SELEÇÃO DE ABAS =====
        # Label para seleção de abas
        ttk.Label(
            main_frame, 
            text="Selecione as abas que deseja processar:",
            style="Custom.TLabel"
        ).grid(row=4, column=0, columnspan=3, sticky="w")
        
        # ===== LISTBOX PERSONALIZADA =====
        # Frame para listbox com scrollbar
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Listbox com cores personalizadas
        self.sheet_listbox = tk.Listbox(
            listbox_frame, 
            selectmode=tk.MULTIPLE, 
            width=60, 
            height=6,
            bg=self.colors['light'],                    # Fundo claro
            fg=self.colors['dark'],                     # Texto escuro
            selectbackground=self.colors['secondary'], # Fundo de seleção verde menta claro
            selectforeground='white',                   # Texto de seleção branco
            font=('Segoe UI', 9),
            relief='solid',
            borderwidth=1
        )
        self.sheet_listbox.grid(row=0, column=0)
        
        # Scrollbar para listbox
        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical')
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.sheet_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.sheet_listbox.yview)

        # ===== BARRA DE PROGRESSO COLORIDA =====
        # Barra de progresso com estilo personalizado
        self.progress = ttk.Progressbar(
            main_frame, 
            variable=self.progress_value,
            maximum=100,
            length=400,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"      # Estilo personalizado da barra
        )
        self.progress.grid(row=6, column=0, columnspan=3, pady=10)

        # ===== FRAME DE BOTÕES PRINCIPAIS =====
        # Frame centralizado para os botões principais
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=15, sticky="ew") #mais espaço

        button_options = {
            'style': "Custom.TButton",
            'width': 15  # Largura fixa para todos os botões
        }

        # ===== BOTÕES PRINCIPAIS COM VERDE OLIVA =====
        # Botão Iniciar busca
        ttk.Button(
            button_frame, 
            text="Iniciar busca", 
            command=self.run_search,
            style="Custom.TButton"                      # Verde oliva claro
        ).grid(row=0, column=0, padx=5)
        
        # Botão Inserir nomes manualmente
        ttk.Button(
            button_frame, 
            text="Inserir nomes manualmente", 
            command=self.open_manual_entry,
            style="Custom.TButton"                      # Verde oliva claro
        ).grid(row=0, column=4, padx=5)
        
        # Botão Cancelar
        ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=self.cancel_search,
            style="Custom.TButton"                      # Verde oliva claro
        ).grid(row=0, column=1, padx=5)
        
        # Botão Sair
        ttk.Button(
            button_frame, 
            text="Sair", 
            command=self.root.quit,
            style="Custom.TButton"                      # Verde oliva claro
        ).grid(row=0, column=2, padx=5)
        
        # Botão Limpar Cache
        ttk.Button(
            button_frame, 
            text="Limpar Cache", 
            command=self.clear_cache,
            style="Custom.TButton"                      # Verde oliva claro
        ).grid(row=0, column=3, padx=5)
        
    # Botão para limpar o progresso manualmente
        ttk.Button(
            button_frame, 
            text="Limpar Progresso", 
            command=self.clear_progress,
            style="Custom.TButton"
        ).grid(row=0, column=5, padx=5)

        # Configurar expansão das colunas do button_frame
        for i in range(5):
            button_frame.grid_columnconfigure(i, weight=1)
        
        # Ajustar a barra de status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=8, column=0, columnspan=3, pady=(15, 0), sticky="ew")
        
        ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            style="Custom.TLabel",
            font=('Segoe UI', 10)  # Fonte um pouco maior
        ).pack(expand=True)

        
        # Adicione o método para limpar progresso:
    def clear_progress(self):
        """Limpa o progresso salvo"""
        from scraper import clear_progress
        if messagebox.askyesno("Limpar Progresso", "Deseja limpar o progresso salvo?"):
            clear_progress()
            self.status_var.set("Progresso salvo foi limpo")
        # Sem código de interface aqui - apenas lógica


    def update_progress_color(self):
        """Atualiza a cor da barra de progresso baseada no valor"""
        value = self.progress_value.get()
        style = ttk.Style()
        
        # ===== CORES DA BARRA DE PROGRESSO BASEADAS NO PROGRESSO =====
        if value < 20:
            color = '#DC3545'       # Vermelho para início
        elif value < 40:
            color = '#FD7E14'       # Laranja para progresso baixo
        elif value < 60:
            color = '#FFC107'       # Amarelo para progresso médio
        elif value < 80:
            color = '#198754'       # Verde para progresso alto
        elif value < 100:
            color = '#20C997'       # Verde menta para quase completo
        else:
            color = '#198754'       # Verde escuro para completo

        # Aplicar nova cor à barra de progresso
        style.configure(
            "Custom.Horizontal.TProgressbar", 
            background=color,                           # Cor principal baseada no progresso
            lightcolor=color,
            darkcolor=color
        )

    def show_cache_stats(self):
        """Mostra estatísticas do cache"""
        try:
            from cache_manager import load_cache
            cache = load_cache()
            cache_size = len(cache)
            
            if cache_size > 0:
                self.status_var.set(f"Cache: {cache_size} espécies salvas")
            else:
                self.status_var.set("Cache vazio")
                
        except Exception as e:
            self.status_var.set("Erro ao verificar cache")

    def clear_cache(self):
        """Limpa o cache"""
        # ===== MESSAGEBOX COM CORES PERSONALIZADAS =====
        if messagebox.askyesno("Limpar Cache", "Deseja limpar o cache de espécies?"):
            try:
                from cache_manager import CACHE_FILE
                if os.path.exists(CACHE_FILE):
                    os.remove(CACHE_FILE)
                    self.status_var.set("Cache limpo com sucesso!")
                else:
                    self.status_var.set("Nenhum cache encontrado")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar cache: {e}")

    def show_credits(self):
        """Mostra informações sobre o desenvolvedor"""
        credits = """
        BUSCADOR REFLORA

Desenvolvido por: [Antonio MSP Figueiredo]
    Versão: 1.1
    Ano: 2025
    https://github.com/Y0n1-F0r3sT
    © Todos os direitos reservados
    """
        messagebox.showinfo("Créditos", credits)

    def choose_file(self):
        """Abre diálogo para seleção de arquivo Excel"""
        path = filedialog.askopenfilename(
            title="Selecione a planilha Excel",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls")]
        )
        if path:
            self.file_path.set(path)
            try:
                self.dataframes = read_excel(path)
                self.sheet_names = list(self.dataframes.keys())
                self.sheet_listbox.delete(0, tk.END)
                for name in self.sheet_names:
                    self.sheet_listbox.insert(tk.END, name)
                self.status_var.set(f"{len(self.sheet_names)} abas carregadas.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler planilha: {e}")

    def run_search(self):
        """Inicia a busca das espécies selecionadas"""
        selection = self.sheet_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma aba para processar.")
            return

        # Verificar se há progresso salvo
        from scraper import load_progress
        progress = load_progress()
        resume = False
        
        if progress:
            resume = messagebox.askyesno(
                "Progresso salvo",
                f"Foi encontrado um progresso salvo com {len(progress['processed_rows'])} espécies processadas. Deseja continuar de onde parou?"
            )

        self.selected_sheets = [self.sheet_names[i] for i in selection]
        self.status_var.set("Iniciando busca...")
        self.progress_value.set(0)
        self.update_progress_color()
        cancel_search_event.clear()

        threading.Thread(
            target=self._process_sheets, 
            args=(resume,),  # Passar a flag de continuar
            daemon=True
        ).start()

    def _process_sheets(self):
        """Processa as abas selecionadas"""
        resultados = {}
        try:
            total_species = sum(len(self.dataframes[sheet]) for sheet in self.selected_sheets)
            processed_species = 0
            
            for sheet_name in self.selected_sheets:
                self.status_var.set(f"Processando aba '{sheet_name}'...")
                df = self.dataframes[sheet_name]
                
                def progress_callback(current, total, name, elapsed, remaining):
                    nonlocal processed_species
                    processed_species = current
                    percent = int((processed_species / total_species) * 100)
                    self.progress_value.set(percent)
                    self.update_progress_color()
                    self.status_var.set(
                        f"Processando: {name} ({current}/{total_species}) | "
                        f"Tempo decorrido: {elapsed:.1f}s | "
                        f"Estimado: {remaining:.1f}s"
                    )
                    self.root.update_idletasks()
                
                resultados[sheet_name] = fetch_data(
                    df, 
                    headless=self.use_headless.get(),
                    cancel_event=cancel_search_event,
                    callback=progress_callback,
                    resume=resume  # Passar a flag para o scraper
                )
                
                if resume:
                    # Se estava continuando, desativa a flag após a primeira execução
                    resume = False
                    
                if cancel_search_event.is_set():
                    self.status_var.set("Processo cancelado pelo usuário.")
                    return



            self.status_var.set("Salvando resultados...")
            salvar_planilha(resultados)
            self.progress_value.set(100)
            self.update_progress_color()
            self.status_var.set("Busca concluída com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
            self.status_var.set("Erro no processamento.")

    def cancel_search(self):
        """Cancela a busca em andamento"""
        if messagebox.askyesno("Cancelar", "Deseja realmente cancelar o processo?"):
            cancel_search_event.set()
            self.status_var.set("Cancelando...")
    
    def open_manual_entry(self):
        """Abre uma janela para o usuário inserir nomes manualmente"""
        # ===== JANELA MODAL COM FUNDO VERDINHO =====
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Inserir nomes científicos")
        manual_window.geometry("500x400")
        manual_window.configure(bg=self.colors['light'])    # Fundo verdinho clarinho
        manual_window.resizable(False, False)
        
        # Centralizar janela
        manual_window.transient(self.root)
        manual_window.grab_set()

        # Label de instrução
        ttk.Label(
            manual_window, 
            text="Digite ou cole um nome por linha:",
            style="Custom.TLabel"
        ).pack(pady=10)

        # ===== TEXT WIDGET COM FUNDO VERDINHO =====
        # Campo de texto com fundo verdinho e cores personalizadas
        text_input = tk.Text(
            manual_window, 
            height=15, 
            width=60,
            bg=self.colors['light'],                    # Fundo verdinho clarinho
            fg=self.colors['dark'],                     # Texto escuro
            insertbackground=self.colors['primary'],    # Cursor verde menta
            selectbackground=self.colors['secondary'],  # Seleção verde menta claro
            selectforeground='white',
            font=('Segoe UI', 10),
            relief='solid',
            borderwidth=1,
            wrap='word'
        )
        text_input.pack(padx=10, pady=5)

        # Frame para botões
        button_frame = ttk.Frame(manual_window)
        button_frame.pack(pady=10)

        def process_manual_input():
            """Processa a entrada manual de nomes"""
            content = text_input.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Aviso", "Insira pelo menos um nome científico.")
                return

            nomes = [linha.strip() for linha in content.splitlines() if linha.strip()]
            if not nomes:
                messagebox.showwarning("Aviso", "A entrada não contém nomes válidos.")
                return

            df = pd.DataFrame({"Nome Científico": nomes})
            self.status_var.set("Iniciando busca manual...")
            self.progress_value.set(0)
            self.update_progress_color()
            cancel_search_event.clear()

            # Rodar a busca manual em nova thread
            threading.Thread(
                target=self.run_manual_fetch, 
                args=(df,),
                daemon=True
            ).start()

            manual_window.destroy()

        # ===== BOTÕES DA JANELA MODAL =====
        # Botão Iniciar busca
        ttk.Button(
            button_frame, 
            text="Iniciar busca", 
            command=process_manual_input,
            style="Custom.TButton"                      # Verde oliva claro
        ).grid(row=0, column=0, padx=5)
        
        # Botão Cancelar
        ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=manual_window.destroy,
            style="Custom.TButton"                      # Verde oliva claro
        ).grid(row=0, column=1, padx=5)

    def run_manual_fetch(self, df_manual):
        """Processa nomes inseridos manualmente"""
        try:
            total = len(df_manual)

            def progress_callback(current, total_, name, elapsed, remaining):
                percent = int((current / total) * 100)
                self.progress_value.set(percent)
                self.update_progress_color()
                self.status_var.set(
                    f"Processando: {name} ({current}/{total}) | "
                    f"Tempo decorrido: {elapsed:.1f}s | "
                    f"Estimado: {remaining:.1f}s"
                )
                self.root.update_idletasks()

            resultados = {"Consulta Manual": fetch_data(
                df_manual,
                headless=self.use_headless.get(),
                cancel_event=cancel_search_event,
                callback=progress_callback
            )}

            if cancel_search_event.is_set():
                self.status_var.set("Busca manual cancelada.")
                return

            self.status_var.set("Salvando resultados...")
            salvar_planilha(resultados)
            self.progress_value.set(100)
            self.update_progress_color()
            self.status_var.set("Busca manual concluída com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
            self.status_var.set("Erro na busca manual.")


def start_app():
    """Inicia a aplicação com tema ttkbootstrap minty"""
    # ===== INICIALIZAÇÃO COM TEMA MINTY E FUNDO VERDINHO =====
    root = ttk.Window(themename="minty")                # Tema minty do ttkbootstrap
    root.title("Buscador Reflora")
    root.resizable(False, False)
    
    # ===== FORÇAR FUNDO VERDINHO NA JANELA RAIZ =====
    root.configure(bg='#F0F8F0')                        # Fundo verdinho clarinho na janela principal
    
    app = ScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    start_app()