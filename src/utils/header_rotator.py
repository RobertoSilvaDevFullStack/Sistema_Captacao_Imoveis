# src/utils/header_rotator.py
"""
Sistema de rotação de headers e user-agents para evitar detecção
"""
import random
import time
from typing import Dict, List, Optional

class HeaderRotator:
    """Classe para rotacionar headers e user-agents"""
    
    def __init__(self):
        self.user_agents = [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            
            # Chrome Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            
            # Mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]
        
        self.accept_languages = [
            'pt-BR,pt;q=0.9,en;q=0.8',
            'pt-BR,pt;q=0.8,en;q=0.5,en-US;q=0.3',
            'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'pt-BR,pt;q=0.9,en;q=0.7,es;q=0.6'
        ]
        
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
    def get_random_user_agent(self) -> str:
        """Retorna um user-agent aleatório"""
        return random.choice(self.user_agents)
    
    def get_random_headers(self, portal: Optional[str] = None) -> Dict[str, str]:
        """Gera headers aleatórios otimizados para cada portal"""
        headers = self.base_headers.copy()
        
        # User-Agent aleatório
        headers['User-Agent'] = self.get_random_user_agent()
        
        # Accept-Language aleatório
        headers['Accept-Language'] = random.choice(self.accept_languages)
        
        # Headers específicos por portal
        if portal == 'zapimoveis':
            headers.update(self._get_zapimoveis_headers())
        elif portal == 'olx':
            headers.update(self._get_olx_headers())
        elif portal == 'vivareal':
            headers.update(self._get_vivareal_headers())
            
        # Variações aleatórias
        if random.choice([True, False]):
            headers['Cache-Control'] = random.choice(['no-cache', 'max-age=0', 'no-store'])
            
        return headers
    
    def _get_zapimoveis_headers(self) -> Dict[str, str]:
        """Headers específicos para ZapImóveis"""
        return {
            'Referer': 'https://www.zapimoveis.com.br/',
            'Origin': 'https://www.zapimoveis.com.br',
            'Sec-Fetch-Site': 'same-origin'
        }
    
    def _get_olx_headers(self) -> Dict[str, str]:
        """Headers específicos para OLX"""
        return {
            'Referer': 'https://www.olx.com.br/',
            'Origin': 'https://www.olx.com.br',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }
    
    def _get_vivareal_headers(self) -> Dict[str, str]:
        """Headers específicos para VivaReal"""
        return {
            'Referer': 'https://www.vivareal.com.br/',
            'Origin': 'https://www.vivareal.com.br',
            'Sec-Fetch-Site': 'same-origin'
        }
    
    def get_mobile_headers(self, portal: Optional[str] = None) -> Dict[str, str]:
        """Gera headers para simular acesso mobile"""
        mobile_user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]
        
        headers = {
            'User-Agent': random.choice(mobile_user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua-mobile': '?1'
        }
        
        if portal:
            if portal == 'zapimoveis':
                headers['Referer'] = 'https://www.zapimoveis.com.br/'
            elif portal == 'olx':
                headers['Referer'] = 'https://www.olx.com.br/'
            elif portal == 'vivareal':
                headers['Referer'] = 'https://www.vivareal.com.br/'
                
        return headers
    
    def get_selenium_options(self, portal: Optional[str] = None) -> List[str]:
        """Retorna opções para configurar Selenium com headers anti-detecção"""
        user_agent = self.get_random_user_agent()
        
        options = [
            f'--user-agent={user_agent}',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-extensions',
            '--no-first-run',
            '--disable-default-apps',
            '--disable-sync',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--window-size=1920,1080'
        ]
        
        # Adicionar variações aleatórias
        if random.choice([True, False]):
            options.append('--incognito')
            
        if random.choice([True, False]):
            options.append('--disable-gpu')
            
        return options

# Instância global para uso fácil
header_rotator = HeaderRotator()
