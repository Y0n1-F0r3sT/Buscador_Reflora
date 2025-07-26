import os
from cache_manager import CACHE_FILE

if os.path.exists(CACHE_FILE):
    os.remove(CACHE_FILE)
    print("Cache limpo com sucesso!")
else:
    print("Nenhum cache encontrado para limpar.")