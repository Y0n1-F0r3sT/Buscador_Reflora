import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading
import pandas as pd
from data_reader import DataReader
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cache_manager import check_cache, update_cache
from collections import defaultdict
import re
import random
from functools import wraps
import json
import os
from datetime import datetime

PROGRESS_FILE = "search_progress.json"

def retry_with_backoff(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt + random.uniform(0, 1)
                    print(f"Tentativa {attempt + 1} falhou: {e}. Retentando em {wait_time:.2f}s...")
                    time.sleep(wait_time)
        return wrapper
    return decorator

def save_progress(df, current_index, results):
    """Salva o progresso atual em um arquivo JSON."""
    progress_data = {
        "timestamp": datetime.now().isoformat(),
        "current_index": current_index,
        "processed_rows": results,
        "total_rows": len(df)
    }
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress():
    """Carrega o progresso salvo, se existir."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def clear_progress():
    """Limpa o arquivo de progresso."""
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

# ... (a classe PerformanceMetrics e o resto do código continuam aqui)

class PerformanceMetrics:
    def __init__(self):
        self.metrics = defaultdict(list)

    def record_timing(self, operation: str, duration: float):
        self.metrics[operation].append(duration)

    def get_stats(self) -> dict:
        stats = {}
        for op, times in self.metrics.items():
            stats[op] = {
                'count': len(times),
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times)
            }
        return stats


cancel_search_event = threading.Event()

class ReusableDriver:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.is_alive = False
    
    def get_driver(self):
        if not self.driver or not self.is_alive:
            self._init_driver()
        return self.driver
    
    def _init_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        
        self.driver = webdriver.Chrome(service=service, options=options)
        self.is_alive = True
    
    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.is_alive = False
    
    def refresh_driver(self):
        """Reinicia o driver se necessário"""
        self.cleanup()
        self._init_driver()

@retry_with_backoff(max_retries=3, backoff_factor=2)
def search_species(name: str, driver_instance: ReusableDriver, timeout=20) -> dict:
    cached = check_cache(name)
    if cached:
        print(f" Cache hit para: {name}")
        return cached

    driver = driver_instance.get_driver()
    url = f"http://servicos.jbrj.gov.br/flora/search/{name.replace(' ', '_')}"
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, timeout)

        # Aguardar carregamento do nome científico
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.CSS_SELECTOR, ".nome.taxon, .taxon, .nomeAutorSupraGenerico").text.strip() != ""
            )
        except:
            wait.until(
                lambda d: d.find_element(By.CSS_SELECTOR, ".nome.taxon, .taxon, .nomeAutorSupraGenerico").text.strip() != ""
            )

        # Aguardar um pouco mais para garantir que toda a página carregou
        time.sleep(2)
        
        # Tentar aguardar o container de forma de vida especificamente
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "forma-de-vida-e-substrato"))
            )
        except:
            # Se não encontrar, continua mesmo assim
            pass

        result = extract_species_data(driver, name, url)
        update_cache(name, result)
        return result

    except Exception as e:
        print(f"ERRO com {name}, tentando refresh do driver: {str(e)}")
        return {
            "familia": "",
            "autor": "",
            "reflora_link": "",
            "distribuicao_geografica": "",
            "dominios_fitogeograficos": "",
            "tipos_vegetacao": "",
            "forma_vida": "",
            "substrato": "",
            "inconsistencia": "Espécie fora da base de dados.",
            "Status Nome": "Erro na verificação"
        }

def extract_species_data(driver, name, url):
    status_nome, inconsistencia = DataReader.read_status_nome(driver, name)
    forma_vida, substrato = DataReader.read_forma_e_substrato(driver)
    origem, endemismo = DataReader.read_origem_e_endemismo(driver, name)
    
    # NOVO: Extrai dados fitogeográficos usando o método do dominios.py
    fitogeo_data = DataReader.extract_fitogeographic_data(driver)
    
    result = {
        "familia": DataReader.read_familia(driver),
        "autor": DataReader.read_autor(driver),
        "reflora_link": url,
        "distribuicao_geografica": DataReader.read_distribuicao(driver),
        "dominios_fitogeograficos": fitogeo_data["dominios_fitogeograficos"],  # Usa o novo método
        "tipos_vegetacao": fitogeo_data["tipos_vegetacao"],  # Usa o novo método
        "forma_vida": forma_vida,
        "substrato": substrato,
        "origem": origem,
        "endemismo": endemismo,
        "inconsistencia": inconsistencia,
        "Status Nome": status_nome
    }
    
    if status_nome != "Nome válido":
        result["inconsistencia"] += " | Nome científico desatualizado"

    if not result["familia"]:
        result["inconsistencia"] += " | Família não encontrada"
    if not result["autor"]:
        result["inconsistencia"] += " | Autor não encontrado"

    print(f"\n{'-'*50}")
    print(f"Espécie: {name}")
    print(f"Origem: {origem}")
    print(f"Endemismo: {endemismo}")
    print(f"{'-'*50}\n")
    return result

def fallback_origem_endemismo(driver):
    """Fallback para quando o método principal falhar"""
    try:
        # Tenta extrair via JavaScript direto
        js_script = """
        function extractOrigemEndemismo() {
            const labels = ['Origem', 'Endemismo'];
            const result = {};
            
            labels.forEach(label => {
                const h4 = [...document.querySelectorAll('h4')]
                    .find(el => el.textContent.includes(label));
                
                if (h4) {
                    const nextDiv = h4.nextElementSibling;
                    if (nextDiv && nextDiv.tagName === 'DIV') {
                        result[label] = nextDiv.textContent.trim();
                    }
                }
            });
            return result;
        }
        return extractOrigemEndemismo();
        """
        result = driver.execute_script(js_script)
        return result.get('Origem', ''), result.get('Endemismo', '')
    except:
        return "", ""

#def parse_distribution_separated(driver):
    """
    Função aprimorada que separa corretamente os dados de distribuição
    em três categorias distintas
    """
    elementos = driver.find_elements(By.CSS_SELECTOR, "*")
    
    # Estrutura para armazenar os dados separadamente
    dados_distribuicao = {
        "distribuicao_geografica": [],
        "dominios_fitogeograficos": [],
        "tipos_vegetacao": []
    }
    
    # Mapeamento dos títulos para as chaves
    titulo_para_chave = {
        "Distribuição Geográfica": "distribuicao_geografica",
        "Domínios Fitogeográficos": "dominios_fitogeograficos", 
        "Tipo de Vegetação": "tipos_vegetacao"
    }
    
    bloco_atual = None
    
    for el in elementos:
        try:
            texto = el.text.strip()
            if not texto or len(texto) > 500:
                continue
                
            # Verificar se é um título de seção
            if texto in titulo_para_chave:
                bloco_atual = titulo_para_chave[texto]
                continue  # Pula o título

            elif bloco_atual and texto in titulo_para_chave.keys():
                continue  # Evita reaproveitar título como conteúdo

            elif bloco_atual and texto not in dados_distribuicao[bloco_atual]:
                if not _is_generic_text(texto):
                    dados_distribuicao[bloco_atual].append(texto)

            
            # Se estamos em um bloco válido, adicionar o texto
            if bloco_atual and texto not in dados_distribuicao[bloco_atual]:
                # Filtrar textos muito genéricos ou irrelevantes
                if not _is_generic_text(texto):
                    dados_distribuicao[bloco_atual].append(texto)
            
            # Parar se coletamos dados suficientes para todas as seções
            if all(dados_distribuicao.values()):
                break
                
        except Exception:
            continue
    
    # Formatar os resultados
    resultado = {}
    for chave, lista_dados in dados_distribuicao.items():
        if lista_dados:
            # Remover duplicatas mantendo a ordem
            dados_unicos = []
            vistos = set()
            for item in lista_dados:
                item_limpo = item.strip()
                if item_limpo and item_limpo not in vistos:
                    dados_unicos.append(item_limpo)
                    vistos.add(item_limpo)
            
            resultado[chave] = "; ".join(dados_unicos)
        else:
            resultado[chave] = ""
    
    return resultado


def _is_generic_text(texto):
    """
    Verifica se o texto é muito genérico ou irrelevante
    para ser incluído nos dados de distribuição
    """
    texto_lower = texto.lower()
    
    # Textos genéricos a serem ignorados
    textos_genericos = [
        "clique aqui", "mais informações", "ver mais", "voltar",
        "página inicial", "buscar", "pesquisar", "filtrar",
        "ordenar", "classificar", "imprimir", "salvar",
        "compartilhar", "ajuda", "sobre", "contato",
        "termos", "política", "privacidade", "cookies"
    ]
    
    # Verificar se contém texto genérico
    for generico in textos_genericos:
        if generico in texto_lower:
            return True
    
    # Verificar se é muito curto (provavelmente não é informação útil)
    if len(texto.strip()) < 3:
        return True
    
    # Verificar se contém apenas números ou símbolos
    if re.match(r'^[\d\s\-\(\)\[\]]+$', texto):
        return True
    
    return False


def fetch_data(df, callback=None, headless=True, cancel_event=None, resume=False):
    results = []
    start_time = time.time()

    if "Nome Científico" not in df.columns:
        raise ValueError("A planilha deve conter a coluna 'Nome Científico'")

    # PRÉ-VALIDAÇÃO E LIMPEZA
    valid_names = []
    invalid_names = []

    for idx, row in df.iterrows():
        name = str(row["Nome Científico"]).strip()

        # Validar formato básico
        if not name or len(name.split()) < 2:
            invalid_names.append((idx, name, "Nome inválido"))
            continue

        # Remover caracteres especiais problemáticos
        cleaned_name = re.sub(r'[^\w\s.-]', '', name)
        if cleaned_name != name:
            print(f" Nome limpo: '{name}' → '{cleaned_name}'")
            name = cleaned_name

        valid_names.append((idx, name))

    print(f" Nomes válidos: {len(valid_names)}")
    print(f" Nomes inválidos: {len(invalid_names)}")

    # Processar nomes inválidos primeiro
    for idx, name, error in invalid_names:
        results.append({
            "Nº": idx + 1,
            "Nome Científico": name,
            "Família": "",
            "Autor": "",
            "Link Reflora": "",
            "Distribuição": "",
            "Forma de Vida": "",
            "Substrato": "",
            "Origem": "",
            "Endemismo": "",
            "Domínios Fitogeográficos": "",
            "Tipos de Vegetação": "",
            "Inconsistências": error,
            "Status Nome": "Nome inválido"
        })

    # CRIAR DRIVER APENAS SE HOUVER NOMES VÁLIDOS
    if not valid_names:
        return pd.DataFrame(results)

    driver_instance = ReusableDriver(headless=headless)

    try:
        for i, (idx, name) in enumerate(valid_names):
            if cancel_event and cancel_event.is_set():
                break

            print(f"🔍 Buscando: {name}")
            result = search_species(name, driver_instance)

            results.append({
                "Nº": idx + 1,
                "Nome Científico": name,
                "Família": result["familia"],
                "Autor": result["autor"],
                "Link Reflora": result["reflora_link"],
                "Distribuição": result["distribuicao_geografica"],
                "Forma de Vida": result["forma_vida"],
                "Substrato": result["substrato"],
                "Origem": result["origem"],
                "Endemismo": result["endemismo"],
                "Domínios Fitogeográficos": result["dominios_fitogeograficos"],
                "Tipos de Vegetação": result["tipos_vegetacao"],
                "Inconsistências": result["inconsistencia"],
                "Status Nome": result["Status Nome"]
            })


            # Salva o progresso a cada 5 espécies processadas
            if i % 5 == 0:
                save_progress(df, idx, results)

            if callback:
                elapsed = time.time() - start_time
                avg_time = elapsed / (len(results))
                estimated = avg_time * (len(df) - len(results))
                callback(len(results), len(df), name, elapsed, estimated)

        # Limpa o progresso ao concluir
        clear_progress()
        return pd.DataFrame(results)

    except Exception as e:
        # Em caso de erro, mantém o progresso salvo para recuperação
        print(f"Erro durante a busca: {e}")
        raise
    finally:
        driver_instance.cleanup()