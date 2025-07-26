from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Tuple, List, Dict, Optional
import re
import unicodedata
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
from selenium.webdriver.common.by import By




class DataReader:
    """Classe otimizada para extração de dados do Reflora com busca textual"""

    DOMINIOS_VALIDOS = {
        "Amazônia", "Caatinga", "Cerrado", 
        "Mata Atlântica", "Pampa", "Pantanal"
    }

    # Dicionários completos para busca
    ESTADOS_BR = {
        'Acre': ['AC', 'Acre'],
        'Alagoas': ['AL', 'Alagoas'],
        'Amapá': ['AP', 'Amapá', 'Amapa'],
        'Amazonas': ['AM', 'Amazonas'],
        'Bahia': ['BA', 'Bahia'],
        'Ceará': ['CE', 'Ceará', 'Ceara'],
        'Distrito Federal': ['DF', 'Distrito Federal'],
        'Espírito Santo': ['ES', 'Espírito Santo', 'Espirito Santo'],
        'Goiás': ['GO', 'Goiás', 'Goias'],
        'Maranhão': ['MA', 'Maranhão', 'Maranhao'],
        'Mato Grosso': ['MT', 'Mato Grosso'],
        'Mato Grosso do Sul': ['MS', 'Mato Grosso do Sul'],
        'Minas Gerais': ['MG', 'Minas Gerais'],
        'Pará': ['PA', 'Pará', 'Para'],
        'Paraíba': ['PB', 'Paraíba', 'Paraiba'],
        'Paraná': ['PR', 'Paraná', 'Parana'],
        'Pernambuco': ['PE', 'Pernambuco'],
        'Piauí': ['PI', 'Piauí', 'Piaui'],
        'Rio de Janeiro': ['RJ', 'Rio de Janeiro'],
        'Rio Grande do Norte': ['RN', 'Rio Grande do Norte'],
        'Rio Grande do Sul': ['RS', 'Rio Grande do Sul'],
        'Rondônia': ['RO', 'Rondônia', 'Rondonia'],
        'Roraima': ['RR', 'Roraima'],
        'Santa Catarina': ['SC', 'Santa Catarina'],
        'São Paulo': ['SP', 'São Paulo', 'Sao Paulo'],
        'Sergipe': ['SE', 'Sergipe'],
        'Tocantins': ['TO', 'Tocantins']
    }

    DOMINIOS_FITOGEOGRAFICOS = {
        'Amazônia': ['Amazonia', 'Amazon', 'Amazônia'],
        'Cerrado': ['Cerrado'],
        'Mata Atlântica': ['Mata Atlântica', 'Mata Atlantica', 'Atlantic Forest'],
        'Caatinga': ['Caatinga'],
        'Pampa': ['Pampa', 'Pampas'],
        'Pantanal': ['Pantanal'],
        'Restinga': ['Restinga'],
        'Campos Rupestres': ['Campos Rupestres', 'Rupestrian Fields'],
        'Manguezal': ['Manguezal', 'Mangrove']
    }

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        """Normaliza texto removendo acentos e caracteres especiais"""
        texto = unicodedata.normalize('NFKD', texto.lower())
        return ''.join(c for c in texto if not unicodedata.combining(c))

    @staticmethod
    def _buscar_padroes(texto: str, padroes: Dict[str, List[str]]) -> List[str]:
        """Busca padrões em um texto ignorando case e acentos"""
        texto_normalizado = DataReader._normalizar_texto(texto)
        encontrados = set()
        
        for nome, variacoes in padroes.items():
            for variacao in variacoes:
                variacao_normalizada = DataReader._normalizar_texto(variacao)
                if re.search(rf'\b{re.escape(variacao_normalizada)}\b', texto_normalizado):
                    encontrados.add(nome)
                    break
                    
        return sorted(encontrados)

    @staticmethod
    def read_distribuicao(driver) -> str:
        """Busca sistemática por estados e domínios fitogeográficos"""
        page_text = driver.page_source
        resultados = []
        
        # Busca estados
        estados = DataReader._buscar_padroes(page_text, DataReader.ESTADOS_BR)
        if estados:
            resultados.append(f"Estados: {', '.join(estados)}")
        
        # Busca domínios
        dominios = DataReader._buscar_padroes(page_text, DataReader.DOMINIOS_FITOGEOGRAFICOS)
        if dominios:
            resultados.append(f"Domínios: {', '.join(dominios)}")
        
        return " | ".join(resultados) if resultados else "Distribuição não registrada"

    @staticmethod
    def read_familia(driver) -> str:
        """Extrai família botânica com múltiplos fallbacks"""
        strategies = [
            ("li.flora.e.funga.hier1", lambda el: el.text.split('\n')[0].strip()),
            ("[title='Família']", lambda el: el.text.replace("Família:", "").strip()),
            (".taxon-family", lambda el: el.text.strip()),
            (".taxon", lambda el: el.text.strip() if any(
                ext in el.text.lower() for ext in ['aceae', 'eae', 'idae']) else None)
        ]

        for selector, processor in strategies:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    result = processor(el)
                    if result:
                        return re.sub(r'\(.*?\)', '', result).strip()
            except NoSuchElementException:
                continue
        return "Família não identificada"

    @staticmethod
    def read_autor(driver) -> str:
        """Método robusto para extração de autores com múltiplas estratégias"""
        strategies = [
            {
                'selector': ".noneAutorInfraGeneric",
                'processor': lambda el: el.text.strip()
            },
            {
                'selector': ".taxon-author, .autor, [itemprop='author'], .author-name",
                'processor': lambda el: el.text.strip()
            },
            {
                'selector': ".nome.taxon, .scientific-name, .taxon-name",
                'processor': lambda el: (
                    el.text.split("(")[1].split(")")[0].strip() 
                    if "(" in el.text and ")" in el.text else None
                )
            },
            {
                'selector': ".nomeAutorSupraGenerico",
                'processor': lambda el: el.text.strip()
            },
            {
                'selector': "meta[name='author'], meta[property='author']",
                'processor': lambda el: el.get_attribute("content").strip()
            }
        ]

        for strategy in strategies:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, strategy['selector'])
                for el in elements:
                    try:
                        result = strategy['processor'](el)
                        if result and len(result) > 1:
                            clean_result = re.sub(r'^\W+|\W+$', '', result)
                            clean_result = re.sub(r'\s+', ' ', clean_result)
                            if clean_result:
                                return clean_result
                    except Exception:
                        continue
            except NoSuchElementException:
                continue
        
        try:
            body_text = driver.find_element(By.CSS_SELECTOR, "body").text
            match = re.search(r'\((.*?)\)', body_text)
            if match:
                result = match.group(1).strip()
                if len(result) > 1:
                    return result
        except:
            pass
        
        return "Autor não identificado"

    @staticmethod
    def read_status_nome(driver, nome_buscado: str) -> Tuple[str, str]:
        """Verificação robusta de status taxonômico"""
        try:
            status_elements = driver.find_elements(
                By.CSS_SELECTOR, 
                ".taxon-status, .status-badge, [class*='status']"
            )
            for element in status_elements:
                status_text = element.text.lower()
                if any(kw in status_text for kw in ["synonym", "sinônimo", "inválido"]):
                    try:
                        accepted = driver.find_element(
                            By.CSS_SELECTOR,
                            ".accepted-name, .taxon-accepted"
                        ).text.split('\n')[0].strip()
                        return ("Nome desatualizado", f"Sugerido: {accepted}")
                    except:
                        return ("Nome desatualizado", "")
        except:
            pass

        try:
            displayed_name = driver.find_element(
                By.CSS_SELECTOR,
                ".scientific-name, .taxon-name"
            ).text.split('\n')[0].strip()
            
            if "(" in displayed_name:
                displayed_name = displayed_name.split("(")[0].strip()
            
            if displayed_name.lower() != nome_buscado.lower():
                return ("Possível sinônimo", f"Nome exibido: {displayed_name}")
        except:
            pass

        return ("Nome válido", "")
    
    @staticmethod
    def read_forma_e_substrato(driver) -> Tuple[str, str]:
        """Extrai Forma de Vida e Substrato com separação correta e sem duplicações"""
        forma_vida, substrato = "", ""
        
        # Estratégia 1: Usar BeautifulSoup para parsing preciso
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            container = soup.find(id="forma-de-vida-e-substrato")

            if container:
                # Buscar especificamente cada div
                forma_div = container.find("div", class_="forma-de-vida")
                substrato_div = container.find("div", class_="substrato")

                if forma_div:
                    # Pegar todo o texto e separar pela tag <br>
                    forma_content = str(forma_div)
                    if '<br/>' in forma_content or '<br>' in forma_content:
                        # Extrair apenas o que vem depois do <br>
                        texto_completo = forma_div.get_text(separator='\n', strip=True)
                        linhas = [linha.strip() for linha in texto_completo.split('\n') if linha.strip()]
                        # A primeira linha é "Forma de Vida", o resto é o conteúdo
                        if len(linhas) > 1:
                            # Remover duplicatas mantendo ordem
                            linhas_unicas = []
                            for linha in linhas[1:]:
                                if linha not in linhas_unicas and linha != "Forma de Vida":
                                    linhas_unicas.append(linha)
                            forma_vida = ', '.join(linhas_unicas)

                if substrato_div:
                    # Mesmo processo para substrato
                    substrato_content = str(substrato_div)
                    if '<br/>' in substrato_content or '<br>' in substrato_content:
                        texto_completo = substrato_div.get_text(separator='\n', strip=True)
                        linhas = [linha.strip() for linha in texto_completo.split('\n') if linha.strip()]
                        # A primeira linha é "Substrato", o resto é o conteúdo
                        if len(linhas) > 1:
                            # Remover duplicatas mantendo ordem
                            linhas_unicas = []
                            for linha in linhas[1:]:
                                if linha not in linhas_unicas and linha != "Substrato":
                                    linhas_unicas.append(linha)
                            substrato = ', '.join(linhas_unicas)

                # Se conseguiu extrair pelo menos um, retorna
                if forma_vida or substrato:
                    return forma_vida.strip(), substrato.strip()
                    
        except Exception as e:
            print(f"Erro na estratégia BeautifulSoup: {e}")

        # Estratégia 2: Usar JavaScript para extração mais precisa
        try:
            # Executar JavaScript para extrair o conteúdo após <br>
            js_script = """
            function extrairFormaESubstrato() {
                const container = document.getElementById('forma-de-vida-e-substrato');
                if (!container) return {forma: '', substrato: ''};
                
                const formaDiv = container.querySelector('.forma-de-vida');
                const substratoDiv = container.querySelector('.substrato');
                
                let forma = '';
                let substrato = '';
                
                if (formaDiv) {
                    const nodes = formaDiv.childNodes;
                    let afterBr = false;
                    let formaItems = new Set(); // Usar Set para evitar duplicatas
                    for (let node of nodes) {
                        if (node.tagName === 'BR') {
                            afterBr = true;
                            continue;
                        }
                        if (afterBr && node.nodeType === Node.TEXT_NODE) {
                            const text = node.textContent.trim();
                            if (text && text !== 'Forma de Vida') {
                                formaItems.add(text);
                            }
                        }
                    }
                    forma = Array.from(formaItems).join(', ');
                }
                
                if (substratoDiv) {
                    const nodes = substratoDiv.childNodes;
                    let afterBr = false;
                    let substratoItems = new Set(); // Usar Set para evitar duplicatas
                    for (let node of nodes) {
                        if (node.tagName === 'BR') {
                            afterBr = true;
                            continue;
                        }
                        if (afterBr && node.nodeType === Node.TEXT_NODE) {
                            const text = node.textContent.trim();
                            if (text && text !== 'Substrato') {
                                substratoItems.add(text);
                            }
                        }
                    }
                    substrato = Array.from(substratoItems).join(', ');
                }
                
                return {
                    forma: forma.trim(),
                    substrato: substrato.trim()
                };
            }
            
            return extrairFormaESubstrato();
            """
            
            result = driver.execute_script(js_script)
            if result and (result.get('forma') or result.get('substrato')):
                return result.get('forma', ''), result.get('substrato', '')
                
        except Exception as e:
            print(f"Erro na estratégia JavaScript: {e}")

        # Estratégia 3: Usar XPath mais específico
        try:
            from selenium.webdriver.common.by import By
            
            # XPath para pegar texto após <br> em forma de vida
            forma_xpath = "//div[@class='forma-de-vida']/br/following-sibling::text()"
            substrato_xpath = "//div[@class='substrato']/br/following-sibling::text()"
            
            forma_elements = driver.find_elements(By.XPATH, forma_xpath)
            substrato_elements = driver.find_elements(By.XPATH, substrato_xpath)
            
            if forma_elements:
                # Usar set para evitar duplicatas
                forma_items = set()
                for el in forma_elements:
                    text = el.strip()
                    if text and text != 'Forma de Vida':
                        forma_items.add(text)
                forma_vida = ', '.join(sorted(forma_items))
            
            if substrato_elements:
                # Usar set para evitar duplicatas
                substrato_items = set()
                for el in substrato_elements:
                    text = el.strip()
                    if text and text != 'Substrato':
                        substrato_items.add(text)
                substrato = ', '.join(sorted(substrato_items))
                
            if forma_vida or substrato:
                return forma_vida.strip(), substrato.strip()
                
        except Exception as e:
            print(f"Erro na estratégia XPath: {e}")

        # Estratégia 4: Parsing manual do HTML bruto
        try:
            import re
            page_source = driver.page_source
            
            # Buscar o container no HTML
            container_pattern = r'<div[^>]*id="forma-de-vida-e-substrato"[^>]*>(.*?)</div>\s*</div>'
            container_match = re.search(container_pattern, page_source, re.DOTALL | re.IGNORECASE)
            
            if container_match:
                container_html = container_match.group(1)
                
                # Extrair forma de vida
                forma_pattern = r'<div[^>]*class="forma-de-vida"[^>]*>.*?<br[^>]*>(.*?)</div>'
                forma_match = re.search(forma_pattern, container_html, re.DOTALL | re.IGNORECASE)
                if forma_match:
                    forma_raw = forma_match.group(1)
                    # Limpar tags HTML
                    forma_clean = re.sub(r'<[^>]+>', '', forma_raw).strip()
                    # Remover duplicatas
                    forma_items = set()
                    for item in forma_clean.split(','):
                        item = item.strip()
                        if item and item != 'Forma de Vida':
                            forma_items.add(item)
                    forma_vida = ', '.join(sorted(forma_items))
                
                # Extrair substrato
                substrato_pattern = r'<div[^>]*class="substrato"[^>]*>.*?<br[^>]*>(.*?)</div>'
                substrato_match = re.search(substrato_pattern, container_html, re.DOTALL | re.IGNORECASE)
                if substrato_match:
                    substrato_raw = substrato_match.group(1)
                    # Limpar tags HTML
                    substrato_clean = re.sub(r'<[^>]+>', '', substrato_raw).strip()
                    # Remover duplicatas
                    substrato_items = set()
                    for item in substrato_clean.split(','):
                        item = item.strip()
                        if item and item != 'Substrato':
                            substrato_items.add(item)
                    substrato = ', '.join(sorted(substrato_items))
                
                if forma_vida or substrato:
                    return forma_vida.strip(), substrato.strip()
                    
        except Exception as e:
            print(f"Erro na estratégia HTML manual: {e}")

        # Estratégia 5: Fallback melhorado - separar dados que vieram juntos
        try:
            # Se chegou até aqui, tentar os métodos originais
            forma_elements = driver.find_elements(By.CSS_SELECTOR, ".forma-de-vida")
            substrato_elements = driver.find_elements(By.CSS_SELECTOR, ".substrato")
            
            texto_completo = ""
            for el in forma_elements + substrato_elements:
                texto_completo += el.text + "\n"
            
            if texto_completo:
                # Tentar separar por padrões conhecidos
                linhas = [linha.strip() for linha in texto_completo.split('\n') if linha.strip()]
                
                forma_encontrada = False
                substrato_encontrado = False
                forma_items = set()  # Usar set para evitar duplicatas
                substrato_items = set()  # Usar set para evitar duplicatas
                
                for linha in linhas:
                    # Pular títulos
                    if linha in ["Forma de Vida", "Substrato"]:
                        if linha == "Forma de Vida":
                            forma_encontrada = True
                            substrato_encontrado = False
                        elif linha == "Substrato":
                            substrato_encontrado = True
                            forma_encontrada = False
                        continue
                    
                    # Palavras-chave para forma de vida
                    palavras_forma = ['Arbusto', 'Árvore', 'Erva', 'Liana', 'Subarbusto', 'Trepadeira', 'Herbácea']
                    # Palavras-chave para substrato
                    palavras_substrato = ['Terrícola', 'Rupícola', 'Epífita', 'Aquática', 'Epifítica']
                    
                    # Classificar baseado no contexto ou palavras-chave
                    if forma_encontrada or any(palavra in linha for palavra in palavras_forma):
                        forma_items.add(linha)
                        forma_encontrada = False  # Resetar para não pegar tudo
                    elif substrato_encontrado or any(palavra in linha for palavra in palavras_substrato):
                        substrato_items.add(linha)
                        substrato_encontrado = False  # Resetar para não pegar tudo
                
                # Converter sets para strings
                if forma_items:
                    forma_vida = ', '.join(sorted(forma_items))
                if substrato_items:
                    substrato = ', '.join(sorted(substrato_items))
                    
        except Exception as e:
            print(f"Erro na estratégia fallback: {e}")

        # Limpeza final e remoção de duplicatas adicionais
        def clean_and_deduplicate(text):
            if not text:
                return ""
            
            # Limpeza básica
            text = re.sub(r'^[:\s,]+|[:\s,]+$', '', text)
            text = re.sub(r'\s+', ' ', text)
            
            # Separar por vírgula e remover duplicatas
            items = []
            seen = set()
            for item in text.split(','):
                item = item.strip()
                item_lower = item.lower()
                if item and item_lower not in seen and item_lower not in ['forma de vida', 'substrato']:
                    items.append(item)
                    seen.add(item_lower)
            
            return ', '.join(items)
        
        forma_vida = clean_and_deduplicate(forma_vida)
        substrato = clean_and_deduplicate(substrato)

        return forma_vida, substrato

    # Função auxiliar para debug - adicione esta também
    @staticmethod
    def debug_forma_substrato(driver):
        """Função para debugar o que está sendo extraído"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            container = soup.find(id="forma-de-vida-e-substrato")
            
            if container:
                print("=== DEBUG FORMA E SUBSTRATO ===")
                print("HTML do container:")
                print(container.prettify())
                print("\n")
                
                forma_div = container.find("div", class_="forma-de-vida")
                substrato_div = container.find("div", class_="substrato")
                
                if forma_div:
                    print("Forma de vida div:")
                    print(forma_div.prettify())
                    print("Texto extraído:", forma_div.get_text(separator='|'))
                    print("\n")
                    
                if substrato_div:
                    print("Substrato div:")
                    print(substrato_div.prettify()) 
                    print("Texto extraído:", substrato_div.get_text(separator='|'))
                    print("\n")
        except Exception as e:
            print(f"Erro no debug: {e}")

    @staticmethod
    def read_reflora_link(driver) -> str:
        """Extrai URL canônico ou atual"""
        try:
            return driver.find_element(
                By.CSS_SELECTOR,
                "link[rel='canonical']"
            ).get_attribute('href')
        except:
            return driver.current_url
    
    
    @staticmethod
    def read_origem_e_endemismo(driver, nome_planta: str) -> Tuple[str, str]:
        """Extrai Origem e Endemismo usando a lógica do plantas.py"""
        def get_info_by_label(label_text):
            try:
                elemento_h4 = driver.find_element(By.XPATH, f"//h4[contains(text(), '{label_text}')]")
                div_valor = elemento_h4.find_element(By.XPATH, "./following-sibling::div")
                return div_valor.text.strip()
            except:
                return "Não encontrado"

        nome_url = quote_plus(nome_planta)
        url = f"https://reflora.jbrj.gov.br/consulta/?grupo=6&familia=null&genero=&especie=&autor=&nomeVernaculo=&nomeCompleto={nome_url}&formaVida=null&substrato=null&ocorreBrasil=QUALQUER&ocorrencia=OCORRE&endemismo=TODOS&origem=TODOS&regiao=QUALQUER&ilhaOceanica=32767&estado=QUALQUER&domFitogeograficos=QUALQUER&vegetacao=TODOS&mostrarAte=SUBESP_VAR&opcoesBusca=TODOS_OS_NOMES&loginUsuario=Visitante&senhaUsuario=&contexto=consulta-publica&pagina=1"
        
        try:
            driver.get(url)
            time.sleep(2)
            origem = get_info_by_label("Origem")
            endemismo = get_info_by_label("Endemismo")
            
            # Padronização dos valores
            origem = "Nativa" if "Nativa" in origem else ("Exótica" if "Exótica" in origem else origem)
            endemismo = "Endêmica" if "Endêmico" in endemismo or "Endêmica" in endemismo else ("Não endêmica" if "Não endêmico" in endemismo or "Não endêmica" in endemismo else endemismo)
            
            return origem, endemismo
        except Exception as e:
            print(f"Erro ao buscar origem/endemismo para {nome_planta}: {e}")
            return "Erro na coleta", "Erro na coleta"
        
    from selenium.webdriver.common.by import By

    @staticmethod
    def get_distribution_info(driver):
        """Versão simplificada apenas para manter compatibilidade"""
        try:
            content_divs = driver.find_elements(By.CLASS_NAME, "content")
            for div in content_divs:
                texto = div.text
                if any(regiao in texto for regiao in ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]):
                    return div.get_attribute('innerHTML').strip()
            return "Não encontrado"
        except:
            return "Não encontrado"

    @staticmethod
    def read_distribuicao_from_html(html_content: str) -> str:
        """Processa HTML de distribuição"""
        # Implemente aqui a lógica de parse que você tinha antes
        # ou simplesmente retorne o html_content se não precisar processar
        return html_content


    @staticmethod
    def extract_fitogeographic_data(driver) -> dict:
        """Extrai dados de domínios fitogeográficos e tipos de vegetação IDÊNTICO ao dominios.py"""
        try:
            # Espera para garantir que a página carregou
            time.sleep(2)
            
            # Pega a div principal que contém os dados
            div_text = driver.find_element(By.XPATH, '//div[@class="text"]')
            full_text = div_text.get_attribute('textContent').strip()
            
            # Extrai os Domínios Fitogeográficos
            dominios = full_text.split("Domínios Fitogeográficos")[1].split("Tipo de Vegetação")[0].strip()
            dominios = dominios.replace('\n', '').replace('\t', '')  # Remove formatação
            
            # Filtra apenas os domínios válidos
            dominios_encontrados = [
                d.strip() 
                for d in dominios.split(',') 
                if d.strip() in DataReader.DOMINIOS_VALIDOS
            ]
            
            # Extrai os Tipos de Vegetação
            vegetacao = full_text.split("Tipo de Vegetação")[1].strip()
            vegetacao = vegetacao.split('\n')[0].strip()  # Pega apenas a primeira linha
            
            return {
                "dominios_fitogeograficos": ", ".join(dominios_encontrados) if dominios_encontrados else "Não encontrado",
                "tipos_vegetacao": vegetacao if vegetacao else "Não encontrado"
            }
        except Exception as e:
            print(f"Erro ao extrair dados fitogeográficos: {e}")
            return {
                "dominios_fitogeograficos": "Erro na extração",
                "tipos_vegetacao": "Erro na extração"
            }

    @staticmethod
    def read_dominios_fitogeograficos(driver) -> str:
        """Método específico para domínios fitogeográficos"""
        try:
            data = DataReader.extract_fitogeographic_data(driver)
            return data["dominios_fitogeograficos"]
        except:
            return "Erro na coleta"

    @staticmethod
    def read_tipos_vegetacao(driver) -> str:
        """Método específico para tipos de vegetação"""
        try:
            data = DataReader.extract_fitogeographic_data(driver)
            return data["tipos_vegetacao"]
        except:
            return "Erro na coleta"
    @staticmethod
    def parse_distribution_html(html_content: str) -> str:
        """Mantém compatibilidade com chamadas existentes"""
        return DataReader.read_distribuicao_from_html(html_content)