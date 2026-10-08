import os
import time
import requests
import pandas as pd
import unicodedata
import psycopg2 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def normalize_text(texto):
    """Removes accents, extra spaces, and converts to uppercase to avoid false positives."""
    if pd.isna(texto) or texto is None:
        return ""
    texto = str(texto).upper().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def clean_cep(cep_raw):
    """Cleans the postal code string, removing decimals and ensuring 8 digits."""
    if pd.isna(cep_raw):
        return ""
    
    cep_str = str(cep_raw).replace('.0', '').strip()
    cep_clean = ''.join(filter(str.isdigit, cep_str))
    
    if 0 < len(cep_clean) < 8:
        cep_clean = cep_clean.zfill(8)
        
    return cep_clean if len(cep_clean) == 8 else None

# In-memory cache to avoid duplicate API requests and prevent rate limiting
cache_ceps = {}

def fetch_cep_api(cep):
    """Fetches address data from BrasilAPI using the Postal Code (CEP)."""
    cep_clean = clean_cep(cep)
    
    if not cep_clean:
        return None
    
    if cep_clean in cache_ceps:
        return cache_ceps[cep_clean]
        
    try:
        resp = requests.get(f"https://brasilapi.com.br/api/cep/v1/{cep_clean}", timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            result = {
                'street': normalize_text(data.get('street', '')),
                'neighborhood': normalize_text(data.get('neighborhood', '')),
                'city': normalize_text(data.get('city', ''))
            }
            cache_ceps[cep_clean] = result
            time.sleep(0.4) # Respect API rate limits
            return result
            
        elif resp.status_code == 404:
            cache_ceps[cep_clean] = "NOT_FOUND"
            time.sleep(0.4)
            return "NOT_FOUND"
            
    except Exception:
        pass
        
    time.sleep(0.4)
    return None

def validate_address(api_data, erp_street, erp_neighborhood, erp_city):
    """Compares the ERP address with the official API address."""
    if api_data == "NOT_FOUND":
        return "Invalid CEP", "Invalid CEP", "Invalid CEP"
        
    if not api_data:
        return "Format/Connection Error", "Format/Connection Error", "Format/Connection Error"
    
    api_street = api_data['street']
    api_neighborhood = api_data['neighborhood']
    api_city = api_data['city']
    
    st_city = "OK" if api_city == erp_city and erp_city != "" else "DIVERGENT"
    st_neigh = "OK" if (api_neighborhood in erp_neighborhood or erp_neighborhood in api_neighborhood) and erp_neighborhood != "" else "DIVERGENT"
    
    if api_street == "" and api_city != "":
        st
