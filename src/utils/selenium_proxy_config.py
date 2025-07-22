# src/utils/selenium_proxy_config.py
"""
Configuração de proxies para Selenium WebDriver
"""
import os
import tempfile
import zipfile
import json
import logging
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType

from .proxy_rotator import ProxyInfo, proxy_manager

logger = logging.getLogger(__name__)

class SeleniumProxyConfig:
    """Configurador de proxies para Selenium"""
    
    def __init__(self):
        self.temp_files = []  # Para limpeza posterior
    
    def create_chrome_proxy_extension(self, proxy: ProxyInfo) -> str:
        """
        Cria extensão Chrome para proxy com autenticação
        
        Returns:
            str: Caminho para o arquivo da extensão
        """
        manifest_json = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy Extension",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            }
        }
        
        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "{proxy.protocol}",
                    host: "{proxy.ip}",
                    port: parseInt("{proxy.port}")
                }},
                bypassList: ["localhost"]
            }}
        }};
        
        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{
            console.log('Proxy configurado:', config);
        }});
        
        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy.username}",
                    password: "{proxy.password}"
                }}
            }};
        }}
        
        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """
        
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        # Escrever arquivos da extensão
        manifest_path = os.path.join(temp_dir, 'manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest_json, f, indent=2)
        
        background_path = os.path.join(temp_dir, 'background.js')
        with open(background_path, 'w') as f:
            f.write(background_js)
        
        # Criar arquivo ZIP
        extension_path = os.path.join(temp_dir, 'proxy_extension.zip')
        with zipfile.ZipFile(extension_path, 'w') as zf:
            zf.write(manifest_path, 'manifest.json')
            zf.write(background_path, 'background.js')
        
        self.temp_files.append(temp_dir)
        return extension_path
    
    def configure_chrome_with_proxy(self, proxy: Optional[ProxyInfo] = None) -> ChromeOptions:
        """
        Configura Chrome options com proxy
        
        Args:
            proxy: Informações do proxy. Se None, pega automaticamente
            
        Returns:
            ChromeOptions: Opções configuradas do Chrome
        """
        if proxy is None:
            proxy = proxy_manager.get_proxy_for_request()
        
        options = ChromeOptions()
        
        if proxy is None:
            logger.warning("Nenhum proxy disponível, usando conexão direta")
            return options
        
        logger.info(f"Configurando Chrome com proxy: {proxy.ip}:{proxy.port}")
        
        # Se tem autenticação, usar extensão
        if proxy.username and proxy.password:
            try:
                extension_path = self.create_chrome_proxy_extension(proxy)
                
                # Extrair extensão para diretório
                extension_dir = os.path.dirname(extension_path)
                with zipfile.ZipFile(extension_path, 'r') as zf:
                    zf.extractall(extension_dir)
                
                options.add_argument(f'--load-extension={extension_dir}')
                logger.info("Extensão de proxy com autenticação carregada")
                
            except Exception as e:
                logger.error(f"Erro ao criar extensão de proxy: {e}")
                # Fallback para proxy sem autenticação
                options.add_argument(f'--proxy-server={proxy.protocol}://{proxy.ip}:{proxy.port}')
        else:
            # Proxy sem autenticação
            options.add_argument(f'--proxy-server={proxy.protocol}://{proxy.ip}:{proxy.port}')
        
        # Configurações adicionais para evitar detecção de proxy
        options.add_argument('--disable-proxy-certificate-handler')
        options.add_argument('--disable-content-security-policy')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        return options
    
    def configure_firefox_with_proxy(self, proxy: Optional[ProxyInfo] = None) -> FirefoxOptions:
        """
        Configura Firefox options com proxy
        
        Args:
            proxy: Informações do proxy. Se None, pega automaticamente
            
        Returns:
            FirefoxOptions: Opções configuradas do Firefox
        """
        if proxy is None:
            proxy = proxy_manager.get_proxy_for_request()
        
        options = FirefoxOptions()
        
        if proxy is None:
            logger.warning("Nenhum proxy disponível, usando conexão direta")
            return options
        
        logger.info(f"Configurando Firefox com proxy: {proxy.ip}:{proxy.port}")
        
        # Configurar proxy no Firefox
        profile = webdriver.FirefoxProfile()
        
        if proxy.protocol == 'http':
            profile.set_preference("network.proxy.type", 1)  # Manual proxy
            profile.set_preference("network.proxy.http", proxy.ip)
            profile.set_preference("network.proxy.http_port", proxy.port)
            profile.set_preference("network.proxy.ssl", proxy.ip)
            profile.set_preference("network.proxy.ssl_port", proxy.port)
        elif proxy.protocol == 'socks5':
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.socks", proxy.ip)
            profile.set_preference("network.proxy.socks_port", proxy.port)
            profile.set_preference("network.proxy.socks_version", 5)
        
        # Configurações de autenticação (se disponível)
        if proxy.username and proxy.password:
            # Firefox não suporta autenticação de proxy diretamente
            # Seria necessário usar extensão ou configuração manual
            logger.warning("Firefox não suporta autenticação de proxy automaticamente")
        
        # Não usar proxy para localhost
        profile.set_preference("network.proxy.no_proxies_on", "localhost,127.0.0.1")
        
        options.profile = profile
        return options
    
    def create_selenium_proxy_object(self, proxy: Optional[ProxyInfo] = None) -> Optional[Proxy]:
        """
        Cria objeto Proxy do Selenium
        
        Args:
            proxy: Informações do proxy. Se None, pega automaticamente
            
        Returns:
            Proxy: Objeto proxy do Selenium ou None
        """
        if proxy is None:
            proxy = proxy_manager.get_proxy_for_request()
        
        if proxy is None:
            return None
        
        selenium_proxy = Proxy()
        selenium_proxy.proxy_type = ProxyType.MANUAL
        
        proxy_address = f"{proxy.ip}:{proxy.port}"
        
        if proxy.protocol == 'http':
            selenium_proxy.http_proxy = proxy_address
            selenium_proxy.ssl_proxy = proxy_address
        elif proxy.protocol == 'socks5':
            selenium_proxy.socksProxy = proxy_address
        
        return selenium_proxy
    
    def test_proxy_with_selenium(self, proxy: ProxyInfo, browser: str = 'chrome') -> bool:
        """
        Testa proxy usando Selenium
        
        Args:
            proxy: Proxy para testar
            browser: 'chrome' ou 'firefox'
            
        Returns:
            bool: True se proxy funcionar
        """
        driver = None
        try:
            if browser == 'chrome':
                options = self.configure_chrome_with_proxy(proxy)
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                driver = webdriver.Chrome(options=options)
            elif browser == 'firefox':
                options = self.configure_firefox_with_proxy(proxy)
                options.add_argument('--headless')
                
                driver = webdriver.Firefox(options=options)
            else:
                raise ValueError(f"Browser não suportado: {browser}")
            
            # Testar navegação
            driver.get('http://httpbin.org/ip')
            
            # Verificar se conseguiu carregar a página
            page_source = driver.page_source
            if 'origin' in page_source.lower():
                logger.info(f"Proxy {proxy.ip}:{proxy.port} funcionando com Selenium")
                return True
            else:
                logger.warning(f"Proxy {proxy.ip}:{proxy.port} não retornou resposta esperada")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao testar proxy {proxy.ip}:{proxy.port} com Selenium: {e}")
            return False
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def cleanup(self):
        """Remove arquivos temporários criados"""
        for temp_file in self.temp_files:
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                elif os.path.isdir(temp_file):
                    import shutil
                    shutil.rmtree(temp_file)
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo temporário {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def __del__(self):
        """Cleanup automático"""
        self.cleanup()

# Instância global
selenium_proxy_config = SeleniumProxyConfig()
