"""
HTML 解析辅助模块
"""

import re
import logging
from typing import Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ParserHelper:
    """HTML 解析助手类"""

    @staticmethod
    def get_soup(html: str) -> Optional[BeautifulSoup]:
        """
        将 HTML 字符串转换为 BeautifulSoup 对象
        
        Args:
            html: HTML 字符串
            
        Returns:
            BeautifulSoup 对象或 None
        """
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"解析 HTML 失败: {e}")
            return None

    @staticmethod
    def extract_price(price_text: str) -> Optional[float]:
        """
        从文本中提取价格
        
        Args:
            price_text: 价格文本
            
        Returns:
            浮点数价格或 None
        """
        try:
            # 移除货币符号和空格
            price_text = price_text.strip()
            
            # 提取数字
            match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if match:
                return float(match.group())
        except Exception as e:
            logger.debug(f"提取价格失败: {price_text}, 错误: {e}")
        
        return None

    @staticmethod
    def extract_number(text: str) -> Optional[int]:
        """
        从文本中提取整数
        
        Args:
            text: 文本
            
        Returns:
            整数或 None
        """
        try:
            match = re.search(r'\d+', text.replace(',', ''))
            if match:
                return int(match.group())
        except Exception as e:
            logger.debug(f"提取数字失败: {text}, 错误: {e}")
        
        return None

    @staticmethod
    def extract_rating(rating_text: str) -> Optional[float]:
        """
        从文本中提取评分
        
        Args:
            rating_text: 评分文本
            
        Returns:
            浮点数评分或 None
        """
        try:
            match = re.search(r'\d+\.?\d*', rating_text)
            if match:
                rating = float(match.group())
                # 确保评分在 0-5 之间
                if 0 <= rating <= 5:
                    return rating
        except Exception as e:
            logger.debug(f"提取评分失败: {rating_text}, 错误: {e}")
        
        return None

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空格和换行
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        验证 URL 是否有效
        
        Args:
            url: URL 字符串
            
        Returns:
            是否有效
        """
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
