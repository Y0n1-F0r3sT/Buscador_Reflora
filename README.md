# Buscador_Reflora
O Buscador Reflora é uma ferramenta automatizada para coleta de dados taxonômicos do portal Reflora (Jardim Botânico do Rio de Janeiro), com foco em espécies vegetais, no link https://reflora.jbrj.gov.br/. Sendo capaz de ler uma entrada manual ou então planilha excel com uma coluna "Nome Científico" e ler os nomes das espécies vegetais, iterar sobre cada uma delas e coletar resultados botânicos significativos sobre as espécies, economizando horas de trabalho manual e exaustivo.

ÍNDICE
- [Funcionalidades](#-funcionalidades)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Dados Coletados](#-dados-coletados)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Limitações](#-limitações)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contribuição](#-contribuição)
- [Citação](#-citação)
- [Contato](#-contato)

FUNCIONALIDADES
Seus principais recursos são:
1) Extração automática de dados do Reflora
2) Suporte para planilhas excel com múltiplas abas
3) Entrada manual de nomes científicos
4) Cache de resultados para consultas repetidas
5) Interface gráfica amigavel
6) barra de progresso com estimativa de tempo

INSTALAÇÃO
1) Certifique-se de ter o Python 3.10+ instalado caso use o código sem o executável.
2) Ao usar o código, instale as dependências pip install pandas openpyxl selenium beautifulsoup4 ttkbootstrap webdriver-manager
3) Tenha o Google Chrome instalado em seu computador
4) Windows 10/11 (64-bit)

COMO USAR
1) Verifique se está conectado à internet, não funciona offline.
2) Caso use o código, execute com python main.py
3) Selecione uma planilha Excel contendo uma coluna "Nome Científico".
4) Escolha as abas que deseja processar.
5) Clique em iniciar busca.
6) Espere carregar e salve os resultados.

OPÇÕES AVANÇADAS: 
* Modo Headless: (já vem ativado) Serve para executar sem abrir a janela do navegador, muito mais rápido. Desaconselha-se desativar.
* Inserção Manual: Para poucas espécies sem a necessidade da planilha
* Limpar cache: Remove dados armazenados localmente.
* Saída em formato .xlsx (compativel com excel, librecalc)

DADOS COLETADOS
O programa extrai automaticamente: Nome do Autor, Familia botânica, status do nome, inconsistencia do nome (se ele existe, se está desatualizado ou fora da base de dados), o respectivo Link da espécie, a Distribuição geográfica, os domínios fitogeográficos, bem como o tipo de vegetação, forma de vida, substrato, origem e endemismo.

ESTRUTURA DO PROJETO:
buscador-reflora/
├── main.py            # Ponto de entrada do programa
├── gui.py             # Interface gráfica
├── scraper.py         # Lógica de scraping
├── data_reader.py     # Extração de dados das páginas
├── cache_manager.py   # Gerenciamento de cache
├── excel_utils.py     # Manipulação de planilhas
├── config.py          # Configurações do programa
└── hook-selenium.py   # Configuração para PyInstaller

lIMITAÇÕES CONHECIDAS
1) Requer conexão estável com a internet
2) Depende da estrutura atual do site Reflora, não funcionando quando o site está fora do ar.
3) Algumas informações podem não estar disponíveis para todas as espécies
4) Apenas coleta dados presentes no REFLORA, não contemplando espécies que não estão catalogadas no mesmo.
5) Por enquanto, só é capaz de coletar dados de vegetais cadastrados no reflora, não coletando nem informando adequadamente dados de espécies de outros reinos.

TROUBLESHOOTING
Problemas comuns e soluções
Sintomas:                            Soluções:
"ChromeDriver não encontrado" ----> Instale o Google Chrome.
Antivírus bloqueia o .exe --------> Adicione exceção ou execute como administrador.
Erro ao ler planilha -------------> Verifique se a coluna se chama EXATAMENTE: Nome Científico (com acento)
Dados incompletos ----------------> Verifique se o nome científico está grafado corretamente

FAQ (Perguntas Frequentes)
P: Posso usar nomes vernáculos (populares)?
R: Não! O sistema só funciona com **nomes científicos** no formato "Gênero espécie".

P: O programa funciona offline?
R: Não, o programa usa o webscrapping em sua concepção, é necessária a conexão com internet.

P: Posso personalizar as colunas de saída?
R: Atualmente não, mas é uma funcionalidade planejado para a versão 2.0.

Quer reportar um bug? ------> Abra uma issue no GitHub

CONTRIBUIÇÃO
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

LICENÇA
Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

CITAÇÃO: Como citar o software em trabalhos
(ABNT - Brasil)
@software{Buscador_Reflora_2025,
  author = {FIGUEIREDO, A. M. S. P.},
  title = {Buscador Reflora: Coletor automatizado de dados taxonômicos},
  year = {2025},
  url = {https://github.com/Y0n1-F0r3sT/buscador-reflora},
  version = {1.1},
  note = {Software desenvolvido para extração de dados do Reflora (Jardim Botânico do Rio de Janeiro)}
}
(APA - Internacional)
Figueiredo, A. M. S. P. (2025). *Buscador Reflora* (Version 1.1) [Computer software]. 
GitHub. https://github.com/Y0n1-F0r3sT/buscador-reflora

CONTATO
Desenvolvido por Antonio Marcos Silva Pereira Figueiredo
email: amspfigueiredo@gmail.com
GitHub: Y0n1-F0r3sT
Ano: 2025

NOTAS FINAIS: 
Dados coletados são para uso acadêmico/pesquisa.
Sem garantia de funcionamento contínuo (depende do Reflora)
Compatível oficialmente com Windows, mas pode ser adaptado para Linux/MacOs.
Para arquivos com grandes volumes de dados, recomenda-se dividir em planilhas e fazer uma por vez.

AGRADECIMENTOS:
- Ao [Jardim Botânico do RJ](https://www.jbrj.gov.br/) pelo acesso ao Reflora, plataforma que auxilia pesquisadores todos os dias na coleta e atualização de dados botânicos.
- Aos contribuidores do projeto
