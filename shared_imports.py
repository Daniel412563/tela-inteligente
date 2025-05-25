"""
Arquivo central para importações compartilhadas entre módulos
"""

# Bibliotecas padrão
import os
import sys

# Bibliotecas de terceiros
import customtkinter as ctk
import wikipedia

# Módulos internos
from utils.web_search_manager import WebSearchManager
from gui import *
from media import *

__all__ = [
    'os', 'sys',
    'ctk', 'wikipedia',
    'WebSearchManager'
]