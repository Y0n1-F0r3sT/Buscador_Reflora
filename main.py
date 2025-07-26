from gui import start_app
from config import get_config, update_config
import tkinter as tk
from tkinter import messagebox
from webdriver_manager.chrome import ChromeDriverManager
import os
import subprocess
import sys
from datetime import datetime


def create_manual_file():
    # ==============================================
    # COLE AQUI O TEXTO COMPLETO DO SEU MANUAL
    # (todo o conteúdo que você forneceu anteriormente)
    # Mantenha as aspas triplas (""") no início e no final
    # ==============================================
    manual_content = """
        
=============================
COLETOR DE DADOS REFLORA
=============================

📌 SOBRE O APLICATIVO:
-----------------------------
O Coletor Reflora é uma ferramenta desenvolvida para auxiliar pesquisadores, estudantes e profissionais que trabalham com botânica, taxonomia ou levantamentos florísticos. Ele automatiza o processo de coleta de informações taxonômicas a partir do portal Reflora, um repositório oficial de dados sobre a flora brasileira.

### O PROBLEMA QUE ELE RESOLVE:

Se você já precisou montar uma tabela com dezenas ou centenas de espécies vegetais, sabe o quanto é cansativo procurar manualmente as informações de cada uma delas: acessar o site, digitar o nome, localizar a ficha correta, copiar a família, o autor, status, forma de vida, distribuição... e repetir esse processo muitas vezes. É desgastante, demorado e sujeito a erros.

O Coletor Reflora foi criado para eliminar essa etapa repetitiva e dar a você o que realmente importa: tempo para pensar, analisar, escrever e concluir seu projeto com qualidade.

Com ele, você transforma uma tarefa de 3 dias em poucos minutos, sem comprometer a precisão — os dados vêm direto da fonte, estruturados em planilhas fáceis de trabalhar.

---

=============================
🖥️ REQUISITOS MÍNIMOS
-----------------------------
Para que o programa funcione corretamente, recomendamos:

- Python 3.10 ou superior
- Navegador Google Chrome instalado
- ChromeDriver compatível com sua versão do Chrome
- Internet estável
- Sistema operacional: Windows 10 ou superior (também roda em Linux/macOS)
- Tela com resolução mínima: 1280x720

### Bibliotecas necessárias:
- `pandas`
- `openpyxl`
- `selenium`
- `beautifulsoup4`
- `ttkbootstrap` (para interface moderna)

**DICA:** Se for executar pela primeira vez, instale as dependências com:

```bash
pip install pandas openpyxl selenium beautifulsoup4 ttkbootstrap
```

---

=============================
📚 COMO USAR O COLETOR REFLORA
-----------------------------

A interface foi desenhada com clareza, para que qualquer pessoa — mesmo sem experiência em programação — possa utilizá-lo. A seguir, o passo a passo completo.

1. 📥 ABRINDO O PROGRAMA:
   - Dê dois cliques no arquivo principal ou execute via terminal (`python gui.py`).
   - Uma janela será aberta com botões, lista de abas e barra de progresso.

2. 📂 SELECIONANDO UMA PLANILHA:
   - Clique no botão “Selecionar Planilha”.
   - Escolha um arquivo .xlsx com uma ou mais abas que contenham uma coluna chamada “Nome Científico”.
   - As abas disponíveis aparecerão listadas na interface.
   - Clique em uma delas para selecionar os nomes a serem buscados.

**DICA:** O nome da coluna com os nomes científicos deve ser exatamente “Nome Científico”, com acento e inicial maiúscula.

3. ✍️ INSERINDO NOMES MANUALMENTE:
   - Caso queira fazer uma busca rápida sem planilhas, clique em “Inserir nomes manualmente”.
   - Uma nova janelinha vai se abrir. Escreva ou cole um nome por linha.
   - Exemplo:
     ```
     Paubrasilia echinata
     Cedrela fissilis
     Syagrus romanzoffiana
     ```
   - Clique em “Buscar” e pronto — o sistema inicia o processo normalmente.

4. 🚀 INICIANDO A BUSCA:
   - Após escolher uma aba ou inserir nomes, clique em “Iniciar Busca”.
   - O programa usará o navegador invisível (modo headless) para acessar cada nome no Reflora e extrair automaticamente os seguintes dados:
     - Nome Científico (confirmado)
     - Família
     - Autor
     - Link direto da ficha Reflora
     - Status nomenclatural (nome válido, sinônimo, inválido...)
     - Inconsistências observadas
     - Distribuição geográfica (estados e domínios)
     - Tipos de vegetação (campo, floresta, restinga etc.)
     - Forma de vida (árvore, arbusto, erva...)
     - Substrato (terrícola, rupícola, epífita...)

**DICA:** Durante a busca, uma barra de progresso será exibida, junto com mensagens que informam:
   - Qual nome está sendo processado
   - Quanto tempo se passou
   - Qual o tempo estimado para terminar

5. ❌ CANCELANDO UMA BUSCA:
   - Clique em “Cancelar” se quiser parar a execução.
   - O processo será interrompido com segurança.

6. 💾 SALVANDO OS RESULTADOS:
   - Assim que a busca terminar, o programa perguntará onde você deseja salvar a nova planilha.
   - Os dados serão salvos em um arquivo Excel, com colunas organizadas e padronizadas.

7. 🧹 LIMPANDO O CACHE:
   - Clique em “Limpar Cache” para apagar arquivos temporários criados durante as buscas.
   - Útil se você estiver testando ou atualizando dados antigos.

---

=============================
🎯 DICAS ÚTEIS
-----------------------------

✅ Sempre revise sua planilha antes de importar, para garantir que a coluna “Nome Científico” está bem formatada.

✅ Quanto mais precisa for a grafia do nome, mais chances o Reflora tem de encontrá-lo corretamente.

✅ Alguns nomes podem retornar status “nome desatualizado” ou “possível sinônimo”. Isso significa que a ficha original foi substituída por outra mais atual.

✅ O botão “Inserir nomes manualmente” é perfeito para testes rápidos com poucos nomes.

✅ Se você fechar a interface durante uma busca, os dados coletados até aquele momento serão perdidos. Use o botão “Cancelar” se quiser interromper com segurança.

✅ A saída final pode ser aberta no Excel, LibreOffice ou qualquer programa que leia `.xlsx`.

---

=============================
🙋‍♂️ CRÉDITOS
-----------------------------
Este aplicativo foi idealizado e desenvolvido por Antonio, estudante de Engenharia Florestal na UFES, apaixonado por automação, dados e biodiversidade. Ele surgiu da necessidade real de acelerar o processo de coleta de informações taxonômicas durante pesquisas e trabalhos acadêmicos, e foi criado com o desejo de também ajudar outros estudantes e pesquisadores da área.



Versão gerada em: 09/07/2025

    """
    
    manual_path = os.path.join(os.path.dirname(__file__), "Manual_Coletor_Reflora.txt")
    if not os.path.exists(manual_path):
        with open(manual_path, 'w', encoding='utf-8') as f:
            f.write(manual_content)
    return manual_path

def show_manual():
    try:
        manual_path = create_manual_file()
        if os.name == 'nt':  # Windows
            os.startfile(manual_path)
        elif os.name == 'posix':  # macOS e Linux
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, manual_path])
    except Exception as e:
        messagebox.showwarning("Aviso", f"Não foi possível abrir o manual: {e}")

if __name__ == "__main__":
    config = get_config()
    if config.get("first_run", True):
        show_manual()  # Abre o manual na primeira execução
        update_config("first_run", False)
    
    # Verificar/instalar ChromeDriver
    try:
        ChromeDriverManager().install()
    except Exception as e:
        messagebox.showwarning("Aviso", f"Não foi possível verificar o ChromeDriver: {e}")
    
    start_app()