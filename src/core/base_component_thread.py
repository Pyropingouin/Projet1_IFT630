from threading import Thread
import random
import time
import logging
from typing import Optional

class BaseComponentThread(Thread):
    """Classe de base pour tous les threads de composants"""
    
    def __init__(self, component, stop_event, name: str):
        super().__init__(name=name)
        self.component = component
        self.stop_event = stop_event
        self.logger = logging.getLogger('simulation')
        
    def sleep_random(self, min_sec: float, max_sec: float):
        """Attente aléatoire entre deux valeurs"""
        time.sleep(random.uniform(min_sec, max_sec))
