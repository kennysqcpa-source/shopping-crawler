"""
台湾虾皮爬虫模块
"""

import logging
import json
import re
from typing import List, Dict, Any
from urllib.parse import urlencode
from utils.request_helper import RequestHelper
from utils.parser_helper import ParserHelper

logger = logging.getLogger(__name__)


class ShopeeeCrawler:
    """虾皮爬虫类"""

    BASE_URL = "https://shopee.tw"
    API_URL = "https://shopee.tw/api/v2/search_items"

    def __init__(self):
        """初始化爬虫"""
        self.session = None

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
        
        for page in range(pages):
            logger.info(f"正在爬取虾皮第 {page + 1}/{pages} 页: {keyword}")
            
            try:
                products = self._fetch_page_products(keyword, page)
                if products:
                    all_products.extend(products)
                    logger.info(f"第 {page + 1} 页获取到 {len(products)} 个产品")
                else:
                    logger.warning(f"第 {page + 1} 页未获取到产品")
                    break
                    
            except Exception as e:
                logger.error(f"爬取第 {page + 1} 页失败: {e}")
                continue
        
        logger.info(f"共获取 {len(all_products)} 个虾皮产品")
        return all_products

    def _fetch_page_products(self, keyword: str, page: int) -> List[Dict[str, Any]]:
        """
        获取单页产品
        
        Args:
            keyword: 搜索关键字
            page: 页码（从0开始）
            
        Returns:
            产品列表
        """
        try:
            # 虾皮使用 API 获取数据
            params = {
                'by': 'relevancy',
                'keyword': keyword,
                'limit': 50,
                'offset': page * 50,
                'newest': 0,
                'order': 'relevancy',
                'page_type': 'search',
                'scenario': 'SE_NO_ADS',
                'version': 2,
            }

            url = f"{self.API_URL}?{urlencode(params)}"
            html = RequestHelper.fetch_page(url)
            
            if not html:
                return []

            # 尝试解析 JSON
            try:
                data = json.loads(html)
                items = data.get('data', {}).get('items', [])
                
                products = []
                for item in items:
                    product = self._parse_product(item)
                    if product:
                        products.append(product)
                
                return products
                
            except json.JSONDecodeError:
                logger.warning("虾皮 API 返回非 JSON 数据，尝试解析 HTML")
                return self._parse_html_page(html)

        except Exception as e:
            logger.error(f"获取虾皮单页产品失败: {e}")
            return []

    def _parse_product(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析单个产品数据
        
        Args:
            item: 产品项数据
            
        Returns:
            解析后的产品字典
        """
        try:
            itemid = item.get('itemid', '')
            shopid = item.get('shopid', '')
            
            product = {
                'product_id': f"{shopid}_{itemid}",
                'title': item.get('name', ''),
                'price': item.get('price_min', 0) / 100000 if item.get('price_min') else 0,
                'original_price': item.get('price_max', 0) / 100000 if item.get('price_max') else 0,
                'sales_count': item.get('sales', 0),
                'rating': item.get('rating_star', 0),
                'rating_count': item.get('cmt_count', 0),
                'seller_name': item.get('shop_name', ''),
                'seller_id': str(shopid),
                'stock': 0,  # 虾皮 API 通常不提供库存信息
                'url': f"{self.BASE_URL}/search?keyword={item.get('name', '')}",
                'image_url': item.get('image', ''),
                'description': item.get('description', ''),
                'category': '厨房用品',
            }
            
            return product
            
        except Exception as e:
            logger.error(f"解析虾皮产品失败: {e}")
            return None

    def _parse_html_page(self, html: str) -> List[Dict[str, Any]]:
        """
        从 HTML 页面解析产品（备用方案）
        
        Args:
            html: HTML 内容
            
        Returns:
            产品列表
        """
        soup = ParserHelper.get_soup(html)
        if not soup:
            return []

        products = []
        
        # 这是备用解析方案，实际 HTML 结构可能需要调整
        items = soup.find_all('div', class_='shopee-search-item-result__item')
        
        for item in items:
            try:
                title_elem = item.find('span', class_='line-clamp')
                price_elem = item.find('span', class_='price')
                seller_elem = item.find('div', class_='shop-name')
                
                product = {
                    'product_id': item.get('data-itemid', ''),
                    'title': ParserHelper.clean_text(title_elem.text) if title_elem else '',
                    'price': ParserHelper.extract_price(price_elem.text) if price_elem else 0,
                    'sales_count': 0,
                    'rating': 0,
                    'rating_count': 0,
                    'seller_name': ParserHelper.clean_text(seller_elem.text) if seller_elem else '',
                    'seller_id': '',
                    'stock': 0,
                    'url': '',
                    'image_url': '',
                    'description': '',
                    'category': '厨房用品',
                }
                
                if product['title']:
                    products.append(product)
                    
            except Exception as e:
                logger.debug(f"解析虾皮 HTML 产品失败: {e}")
                continue
        
        return products
