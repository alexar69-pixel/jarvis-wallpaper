import requests
from bs4 import BeautifulSoup
from googlesearch import search
import logging

logging.basicConfig(level=logging.INFO)

def invisible_search(query, num_results=3):
    """
    Realiza una búsqueda web invisible en segundo plano usando Google/Chrome.
    Extrae los primeros párrafos de texto de los resultados principales.
    """
    logging.info(f"[Web Search] Buscando: {query}")
    results_text = f"RESULTADOS DE BÚSQUEDA WEB PARA: '{query}'\n\n"
    
    try:
        # Busca en google de forma invisible
        urls = search(query, num_results=num_results, advanced=False)
        
        for url in urls:
            try:
                logging.info(f"[Web Search] Scrapeando URL: {url}")
                # Cabecera para simular un navegador real (Chrome/Brave) y evitar bloqueos básicos
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extraer párrafos principales
                    paragraphs = soup.find_all('p')
                    text_content = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
                    
                    # Acortar texto para no saturar la memoria del LLM
                    summary = text_content[:500] 
                    if summary:
                        results_text += f"Fuente ({url}): {summary}...\n"
            except Exception as e:
                logging.error(f"[Web Search] Error scrapeando {url}: {e}")
                continue
                
        return results_text if "Fuente" in results_text else "No se pudo extraer información clara."

    except Exception as e:
        logging.error(f"[Web Search] Error general de búsqueda: {e}")
        return "Hubo un error al intentar conectarse a la web."

# Ejemplo de uso interno:
if __name__ == "__main__":
    print(invisible_search("noticias de hoy en españa", 2))
