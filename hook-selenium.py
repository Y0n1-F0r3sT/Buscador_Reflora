# hook-selenium.py
from PyInstaller.utils.hooks import collect_all, collect_data_files
from PyInstaller.utils.hooks import logger

# Coleta tudo do Selenium
datas, binaries, hiddenimports = collect_all('selenium')

# Adiciona imports ocultos necessários
hiddenimports += [
    'selenium.webdriver',
    'selenium.webdriver.common',
    'selenium.webdriver.chrome',
    'selenium.webdriver.remote',
    'webdriver_manager',
    'webdriver_manager.chrome'
]

# Log para depuração
logger.info(f"Selenium datas: {datas}")
logger.info(f"Selenium binaries: {binaries}")
logger.info(f"Selenium hiddenimports: {hiddenimports}")