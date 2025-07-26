# cache_manager.py
import json
import os
import hashlib
from datetime import datetime, timedelta

CACHE_FILE = "reflora_cache.json"
CACHE_EXPIRE_DAYS = 30

def get_species_hash(nome_cientifico):
    return hashlib.md5(nome_cientifico.lower().encode()).hexdigest()

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def check_cache(nome_cientifico):
    cache = load_cache()
    species_hash = get_species_hash(nome_cientifico)
    if species_hash in cache:
        cached_data = cache[species_hash]
        cache_date = datetime.strptime(cached_data['cache_date'], '%Y-%m-%d')
        if datetime.now() - cache_date < timedelta(days=CACHE_EXPIRE_DAYS):
            return cached_data['data']
    return None

def update_cache(nome_cientifico, data):
    cache = load_cache()
    species_hash = get_species_hash(nome_cientifico)
    cache[species_hash] = {
        'data': data,
        'cache_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_cache(cache)