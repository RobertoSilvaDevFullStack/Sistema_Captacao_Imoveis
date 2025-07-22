# src/utils/selenium_stealth.py
"""
Sistema de Selenium com Stealth Mode e Simulação de Comportamento Humano
"""
import time
import random
import json
import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import math

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.common.exceptions import TimeoutException, WebDriverException
    
    # Stealth imports
    try:
        from selenium_stealth import stealth
        STEALTH_AVAILABLE = True
    except ImportError:
        STEALTH_AVAILABLE = False
        
    try:
        import undetected_chromedriver as uc
        UNDETECTED_CHROME_AVAILABLE = True
    except ImportError:
        UNDETECTED_CHROME_AVAILABLE = False
        
except ImportError:
    SELENIUM_AVAILABLE = False
else:
    SELENIUM_AVAILABLE = True

@dataclass
class HumanBehaviorConfig:
    """Configuração de comportamento humano"""
    reading_speed_wpm: int = 200  # Palavras por minuto
    min_scroll_pause: float = 0.5
    max_scroll_pause: float = 2.0
    min_click_delay: float = 0.3
    max_click_delay: float = 1.5
    typing_speed_cpm: int = 180  # Caracteres por minuto
    mouse_movement_duration: float = 1.0
    page_load_patience: float = 10.0

@dataclass
class StealthConfig:
    """Configuração do modo stealth"""
    use_stealth: bool = True
    use_undetected_chrome: bool = True
    disable_images: bool = False
    disable_css: bool = False
    disable_javascript: bool = False
    headless: bool = False
    window_size: Tuple[int, int] = (1366, 768)
    user_agent_override: Optional[str] = None

class HumanBehaviorSimulator:
    """Simula comportamento humano realístico"""
    
    def __init__(self, config: HumanBehaviorConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def calculate_reading_time(self, text: str) -> float:
        """Calcula tempo de leitura baseado na velocidade humana"""
        word_count = len(text.split())
        reading_time = (word_count / self.config.reading_speed_wpm) * 60
        # Adicionar variação humana
        variation = random.uniform(0.8, 1.3)
        return max(1.0, reading_time * variation)
    
    def human_scroll(self, driver, direction: str = 'down', distance: int = None):
        """Simula scroll humano com pausas naturais"""
        if distance is None:
            distance = random.randint(200, 600)
            
        # Dividir o scroll em pequenos movimentos
        steps = random.randint(3, 8)
        step_distance = distance // steps
        
        for i in range(steps):
            if direction == 'down':
                driver.execute_script(f"window.scrollBy(0, {step_distance});")
            else:
                driver.execute_script(f"window.scrollBy(0, -{step_distance});")
            
            # Pausa entre movimentos
            pause = random.uniform(0.1, 0.4)
            time.sleep(pause)
        
        # Pausa após o scroll
        final_pause = random.uniform(
            self.config.min_scroll_pause,
            self.config.max_scroll_pause
        )
        time.sleep(final_pause)
    
    def human_click(self, driver, element):
        """Simula clique humano com movimento de mouse"""
        try:
            # Mover mouse para o elemento
            actions = ActionChains(driver)
            
            # Adicionar movimento curvo do mouse
            self._move_mouse_naturally(actions, element)
            
            # Pequena pausa antes do clique
            pause = random.uniform(
                self.config.min_click_delay,
                self.config.max_click_delay
            )
            time.sleep(pause)
            
            # Clique
            actions.click(element).perform()
            
            # Pausa após o clique
            time.sleep(random.uniform(0.2, 0.8))
            
        except Exception as e:
            self.logger.warning(f"Erro no clique humano: {e}")
            # Fallback para clique normal
            element.click()
    
    def _move_mouse_naturally(self, actions: ActionChains, element):
        """Move o mouse de forma natural até o elemento"""
        try:
            # Obter posição atual e destino
            current_pos = actions._driver.execute_script(
                "return {x: 0, y: 0};"  # Posição atual simplificada
            )
            
            # Mover em pequenos incrementos
            for i in range(random.randint(2, 5)):
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                actions.move_to_element_with_offset(element, offset_x, offset_y)
                actions.pause(random.uniform(0.05, 0.15))
            
            # Movimento final para o centro do elemento
            actions.move_to_element(element)
            
        except Exception:
            # Fallback para movimento simples
            actions.move_to_element(element)
    
    def human_typing(self, element, text: str):
        """Simula digitação humana com velocidade variável"""
        element.clear()
        
        chars_per_minute = self.config.typing_speed_cpm
        base_delay = 60.0 / chars_per_minute
        
        for char in text:
            element.send_keys(char)
            
            # Variação na velocidade de digitação
            if char == ' ':
                delay = base_delay * random.uniform(1.5, 3.0)  # Pausas maiores em espaços
            elif char in '.,!?':
                delay = base_delay * random.uniform(2.0, 4.0)  # Pausas em pontuação
            else:
                delay = base_delay * random.uniform(0.8, 1.5)
            
            time.sleep(delay)
        
        # Pausa após terminar a digitação
        time.sleep(random.uniform(0.5, 2.0))
    
    def simulate_page_reading(self, driver, reading_duration: float = None):
        """Simula leitura de página com movimentos naturais"""
        if reading_duration is None:
            # Estimar baseado no conteúdo da página
            try:
                text_content = driver.execute_script(
                    "return document.body.innerText || document.body.textContent || '';"
                )
                reading_duration = self.calculate_reading_time(text_content)
            except:
                reading_duration = random.uniform(10.0, 30.0)
        
        self.logger.info(f"Simulando leitura por {reading_duration:.1f} segundos")
        
        start_time = time.time()
        scroll_count = 0
        
        while (time.time() - start_time) < reading_duration:
            # Scroll ocasional durante a leitura
            if random.random() < 0.3:  # 30% chance de scroll
                scroll_direction = 'down' if scroll_count < 3 else random.choice(['down', 'up'])
                self.human_scroll(driver, scroll_direction)
                scroll_count += 1 if scroll_direction == 'down' else -1
                scroll_count = max(0, scroll_count)
            
            # Pausa de leitura
            remaining_time = reading_duration - (time.time() - start_time)
            if remaining_time <= 0:
                break
                
            pause = random.uniform(3.0, 8.0)
            time.sleep(min(pause, remaining_time))

class StealthWebDriver:
    """Driver Selenium com modo stealth e comportamento humano"""
    
    def __init__(self, 
                 stealth_config: StealthConfig = None,
                 behavior_config: HumanBehaviorConfig = None,
                 browser: str = 'chrome'):
        
        self.stealth_config = stealth_config or StealthConfig()
        self.behavior_config = behavior_config or HumanBehaviorConfig()
        self.behavior_simulator = HumanBehaviorSimulator(self.behavior_config)
        self.browser = browser
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium não está disponível. Execute: pip install selenium")
    
    def create_driver(self) -> webdriver:
        """Cria driver com configurações stealth"""
        try:
            if self.browser.lower() == 'chrome':
                return self._create_chrome_driver()
            elif self.browser.lower() == 'firefox':
                return self._create_firefox_driver()
            else:
                raise ValueError(f"Browser '{self.browser}' não suportado")
                
        except Exception as e:
            self.logger.error(f"Erro ao criar driver: {e}")
            raise
    
    def _create_chrome_driver(self) -> webdriver:
        """Cria Chrome driver com stealth"""
        
        # Usar undetected-chromedriver se disponível
        if UNDETECTED_CHROME_AVAILABLE and self.stealth_config.use_undetected_chrome:
            return self._create_undetected_chrome()
        
        # Chrome normal com stealth
        options = ChromeOptions()
        
        # Configurações básicas de stealth
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Desabilitar detecção de webdriver
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Configurações de performance
        if self.stealth_config.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        if self.stealth_config.disable_css:
            options.add_argument('--disable-css')
            
        # User agent
        if self.stealth_config.user_agent_override:
            options.add_argument(f'--user-agent={self.stealth_config.user_agent_override}')
        
        # Tamanho da janela
        width, height = self.stealth_config.window_size
        options.add_argument(f'--window-size={width},{height}')
        
        # Headless mode
        if self.stealth_config.headless:
            options.add_argument('--headless')
        
        # Criar driver
        driver = webdriver.Chrome(options=options)
        
        # Aplicar stealth se disponível
        if STEALTH_AVAILABLE and self.stealth_config.use_stealth:
            stealth(driver,
                   languages=["en-US", "en"],
                   vendor="Google Inc.",
                   platform="Win32",
                   webgl_vendor="Intel Inc.",
                   renderer="Intel Iris OpenGL Engine",
                   fix_hairline=True)
        
        # Script para remover propriedades de webdriver
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        return driver
    
    def _create_undetected_chrome(self) -> webdriver:
        """Cria driver usando undetected-chromedriver"""
        options = uc.ChromeOptions()
        
        # Configurações básicas
        if self.stealth_config.headless:
            options.add_argument('--headless')
            
        if self.stealth_config.user_agent_override:
            options.add_argument(f'--user-agent={self.stealth_config.user_agent_override}')
        
        # Desabilitar recursos se necessário
        if self.stealth_config.disable_images:
            options.add_argument('--blink-settings=imagesEnabled=false')
            
        width, height = self.stealth_config.window_size
        options.add_argument(f'--window-size={width},{height}')
        
        # Criar driver undetected
        driver = uc.Chrome(options=options, version_main=None)
        
        return driver
    
    def _create_firefox_driver(self) -> webdriver:
        """Cria Firefox driver com stealth"""
        options = FirefoxOptions()
        
        if self.stealth_config.headless:
            options.add_argument('--headless')
        
        # Configurações de stealth para Firefox
        profile = webdriver.FirefoxProfile()
        
        # Desabilitar WebRTC
        profile.set_preference("media.peerconnection.enabled", False)
        
        # Configurações de user agent
        if self.stealth_config.user_agent_override:
            profile.set_preference("general.useragent.override", 
                                 self.stealth_config.user_agent_override)
        
        # Desabilitar imagens se necessário
        if self.stealth_config.disable_images:
            profile.set_preference("permissions.default.image", 2)
        
        options.profile = profile
        
        driver = webdriver.Firefox(options=options)
        return driver
    
    def __enter__(self):
        """Context manager entry"""
        self.driver = self.create_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.driver:
            self.driver.quit()
    
    def get(self, url: str, simulate_reading: bool = True):
        """Navega para URL com comportamento humano"""
        if not self.driver:
            raise RuntimeError("Driver não foi criado")
        
        self.logger.info(f"Navegando para: {url}")
        
        # Navegar
        self.driver.get(url)
        
        # Aguardar carregamento
        WebDriverWait(self.driver, self.behavior_config.page_load_patience).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Simular leitura se solicitado
        if simulate_reading:
            reading_time = random.uniform(2.0, 8.0)
            self.behavior_simulator.simulate_page_reading(self.driver, reading_time)
    
    def find_and_click(self, by: By, value: str, simulate_human: bool = True):
        """Encontra elemento e clica com comportamento humano"""
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((by, value))
        )
        
        if simulate_human:
            self.behavior_simulator.human_click(self.driver, element)
        else:
            element.click()
        
        return element
    
    def type_text(self, by: By, value: str, text: str, simulate_human: bool = True):
        """Digita texto com comportamento humano"""
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        )
        
        if simulate_human:
            self.behavior_simulator.human_typing(element, text)
        else:
            element.clear()
            element.send_keys(text)
        
        return element
    
    def scroll_page(self, direction: str = 'down', distance: int = None):
        """Faz scroll com comportamento humano"""
        self.behavior_simulator.human_scroll(self.driver, direction, distance)
    
    def wait_and_think(self, min_seconds: float = 1.0, max_seconds: float = 5.0):
        """Simula tempo de 'pensamento' humano"""
        think_time = random.uniform(min_seconds, max_seconds)
        self.logger.debug(f"Simulando pensamento por {think_time:.1f}s")
        time.sleep(think_time)

class StealthDriverManager:
    """Gerenciador de drivers stealth com pool e rotação"""
    
    def __init__(self, max_drivers: int = 3):
        self.max_drivers = max_drivers
        self.drivers = []
        self.current_index = 0
        self.logger = logging.getLogger(__name__)
        
    def create_driver_pool(self, configs: List[Dict] = None) -> List[StealthWebDriver]:
        """Cria pool de drivers com configurações diferentes"""
        if configs is None:
            configs = self._get_default_configs()
        
        for i, config in enumerate(configs[:self.max_drivers]):
            try:
                stealth_config = StealthConfig(**config.get('stealth', {}))
                behavior_config = HumanBehaviorConfig(**config.get('behavior', {}))
                
                driver_wrapper = StealthWebDriver(
                    stealth_config=stealth_config,
                    behavior_config=behavior_config,
                    browser=config.get('browser', 'chrome')
                )
                
                self.drivers.append(driver_wrapper)
                self.logger.info(f"Driver {i+1} criado com sucesso")
                
            except Exception as e:
                self.logger.error(f"Erro ao criar driver {i+1}: {e}")
        
        return self.drivers
    
    def get_next_driver(self) -> StealthWebDriver:
        """Retorna o próximo driver disponível (rotação)"""
        if not self.drivers:
            raise RuntimeError("Nenhum driver disponível")
        
        driver = self.drivers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.drivers)
        
        return driver
    
    def cleanup(self):
        """Limpa todos os drivers"""
        for driver_wrapper in self.drivers:
            try:
                if driver_wrapper.driver:
                    driver_wrapper.driver.quit()
            except Exception as e:
                self.logger.error(f"Erro ao fechar driver: {e}")
        
        self.drivers.clear()
    
    def _get_default_configs(self) -> List[Dict]:
        """Configurações padrão para diferentes perfis"""
        return [
            {
                'browser': 'chrome',
                'stealth': {
                    'use_undetected_chrome': True,
                    'headless': False,
                    'window_size': (1366, 768)
                },
                'behavior': {
                    'reading_speed_wpm': 200,
                    'typing_speed_cpm': 180
                }
            },
            {
                'browser': 'chrome',
                'stealth': {
                    'use_undetected_chrome': True,
                    'headless': False,
                    'window_size': (1920, 1080),
                    'disable_images': True
                },
                'behavior': {
                    'reading_speed_wpm': 250,
                    'typing_speed_cpm': 220
                }
            },
            {
                'browser': 'chrome',
                'stealth': {
                    'use_undetected_chrome': False,
                    'use_stealth': True,
                    'headless': True,
                    'window_size': (1440, 900)
                },
                'behavior': {
                    'reading_speed_wpm': 180,
                    'typing_speed_cpm': 160
                }
            }
        ]

# Instância global para facilitar uso
stealth_manager = StealthDriverManager()

def create_stealth_driver(portal: str = None, headless: bool = False) -> StealthWebDriver:
    """Função de conveniência para criar driver stealth"""
    
    # Configurações específicas por portal
    portal_configs = {
        'zapimoveis': {
            'window_size': (1366, 768),
            'user_agent_override': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'olx': {
            'window_size': (1920, 1080),
            'disable_images': True
        },
        'vivareal': {
            'window_size': (1440, 900),
            'user_agent_override': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    
    # Configuração base
    stealth_config = StealthConfig(headless=headless)
    
    # Aplicar configuração específica do portal
    if portal and portal in portal_configs:
        config = portal_configs[portal]
        for key, value in config.items():
            setattr(stealth_config, key, value)
    
    return StealthWebDriver(stealth_config=stealth_config)
