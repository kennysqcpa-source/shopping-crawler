"""
美国亚马逊爬虫模块
"""

import logging
import json
import re
from typing import List, Dict, Any
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from utils.request_helper import RequestHelper
from utils.parser_helper import ParserHelper

logger = logging.getLogger(__name__)


class AmazonCrawler:
    """亚马逊爬虫类"""

    BASE_URL = "https://www.amazon.com"
    SEARCH_URL = "https://www.amazon.com/s"

    def __init__(self):
        """初始化爬虫"""
        pass

    def search_products(self, keyword: str, pages: int = 5) -> List[Dict[str, Any]]:
        """
        搜索产品
        
        Args:
            keyword: 搜索关键字
            pages: 搜索页数
            
        Returns:
            产品列表
        """
        all_products = []
        
        for page in range(1, pages + 1):
            logger.info(f"正在爬取亚马逊第 {page}/{pages} 页: {keyword}")
            
            try:
                products = self._fetch_page_products(keyword, page)
                if products:
                    all_products.extend(products)
                    logger.info(f"第 {page} 页获取到 {len(products)} 个产品")
                else:
                    logger.warning(f"第 {page} 页未获取到产品")
                    break
                    
            except Exception as e:
                logger.error(f"爬取第 {page} 页失败: {e}")
                continue
        
        logger.info(f"共获取 {len(all_products)} 个亚马逊产品")
        return all_products

    def _fetch_page_products(self, keyword: str, page: int) -> List[Dict[str, Any]]:
        """
        获取单页产品
        
        Args:
            keyword: 搜索关键字
            page: 页码
            
        Returns:
            产品列表
        """
        try:
            params = {
                'k': keyword,
                'page': page,
            }

            url = f"{self.SEARCH_URL}?{urlencode(params)}"
            html = RequestHelper.fetch_page(url)
            
            if not html:
                return []

            return self._parse_html_page(html)

        except Exception as e:
            logger.error(f"获取亚马逊单页产品失败: {e}")
            return []

    def _parse_html_page(self, html: str) -> List[Dict[str, Any]]:
        """
        从 HTML 页面解析产品
        
        Args:
            html: HTML 内容
            
        Returns:
            产品列表
        """
        soup = ParserHelper.get_soup(html)
        if not soup:
            return []

        products = []
        
        # 亚马逊搜索结果容器
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for item in items:
            try:
                product = self._parse_product_item(item)
                if product:
                    products.append(product)
                    
            except Exception as e:
                logger.debug(f"解析亚马逊产品项失败: {e}")
                continue
        
        return products

    def _parse_product_item(self, item: BeautifulSoup) -> Dict[str, Any]:
        """
        解析单个产品项
        
        Args:
            item: BeautifulSoup 元素
            
        Returns:
            产品字典
        """
        try:
            # 提取 ASIN
            asin = item.get('data-asin', '')
            if not asin:
                return None

            # 提取标题
            title_elem = item.find('h2', class_='s-size-mini')
            title = ''
            if title_elem:
                title_link = title_elem.find('a')
                if title_link:
                    title = ParserHelper.clean_text(title_link.text)

            if not title:
                return None

            # 提取价格
            price = 0
            price_elem = item.find('span', class_='a-price-whole')
            if price_elem:
                price = ParserHelper.extract_price(price_elem.text)

            # 提取评分
            rating = 0
            rating_elem = item.find('span', class_='a-icon-star-small')
            if rating_elem:
                rating_text = rating_elem.find('span')
                if rating_text:
                    rating = ParserHelper.extract_rating(rating_text.text)

            # 提取评价数量
            rating_count = 0
            rating_count_elem = item.find('span', {'aria-label': re.compile(r'.*reviews')})
            if rating_count_elem:
                rating_count = ParserHelper.extract_number(rating_count_elem.text)

            # 提取卖家信息
            seller_name = ''
            seller_elem = item.find('div', class_='a-row a-size-base a-color-secondary')
            if seller_elem:
                seller_text = seller_elem.text
                if 'Sold by' in seller_text:
                    seller_name = ParserHelper.clean_text(seller_text.replace('Sold by', '').strip())

            # 提取库存状态
            stock_status = '有货'
            stock_elem = item.find('span', class_='a-size-base a-color-price')
            if stock_elem and 'stock' in stock_elem.text.lower():
                stock_status = ParserHelper.clean_text(stock_elem.text)

            # 提取产品链接
            url = ''
            link_elem = item.find('a', class_='a-link-normal')
            if link_elem and link_elem.get('href'):
                url = self.BASE_URL + link_elem.get('href')

            product = {
                'asin': asin,
                'title': title,
                'price': price if price else 0,
                'original_price': price if price else 0,
                'rating': rating,
                'rating_count': rating_count,
                'seller_name': seller_name,
                'stock_status': stock_status,
                'url': url,
                'image_url': self._extract_image_url(item),
                'description': '',
                'category': '厨房用品',
            }

            return product

        except Exception as e:
            logger.debug(f"解析亚马逊产品项详情失败: {e}")
            return None

    def _extract_image_url(self, item: BeautifulSoup) -> str:
        """
        提取产品图片 URL
        
        Args:
            item: 产品项元素
            
        Returns:
            图片 URL
        """
        try:
            img_elem = item.find('img', class_='s-image')
            if img_elem and img_elem.get('src'):
                return img_elem.get('src')
        except Exception as e:
            logger.debug(f"提取图片 URL 失败: {e}")
        
        return ''
