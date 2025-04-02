"""
改進的命令行介面模組
"""
import os
import sys
from colorama import init, Fore, Style

# 初始化 colorama
init()

class CLI:
    """改進的命令行介面"""
    
    @staticmethod
    def print_header(title):
        """打印標題"""
        print("\n" + "="*60)
        print(f"{Fore.CYAN}{title}{Style.RESET_ALL}".center(60))
        print("="*60)
    
    @staticmethod
    def print_success(message):
        """打印成功信息"""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_error(message):
        """打印錯誤信息"""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_warning(message):
        """打印警告信息"""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_info(message):
        """打印信息"""
        print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")
        
    @staticmethod
    def get_input(prompt):
        """獲取用戶輸入"""
        return input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")