"""
数据库管理模块
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite 数据库管理类"""

    def __init__(self, db_path: str):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.ensure_db_dir()
        self.init_tables()

    def ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"创建数据库目录: {db_dir}")

    def get_connection(self):
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 支持字典式访问
            return conn
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def init_tables(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 虾皮产品表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopee_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE,
                title TEXT NOT NULL,
                price REAL,
                original_price REAL,
                sales_count INTEGER,
                rating REAL,
                rating_count INTEGER,
                seller_name TEXT,
                seller_id TEXT,
                stock INTEGER,
                url TEXT,
                image_url TEXT,
                description TEXT,
                category TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 亚马逊产品表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS amazon_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT UNIQUE,
                title TEXT NOT NULL,
                price REAL,
                original_price REAL,
                rating REAL,
                rating_count INTEGER,
                seller_name TEXT,
                stock_status TEXT,
                url TEXT,
                image_url TEXT,
                description TEXT,
                category TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logger.info("数据库表初始化完成")

    def insert_shopee_product(self, product: Dict[str, Any]) -> bool:
        """
        插入或更新虾皮产品
        
        Args:
            product: 产品数据字典
            
        Returns:
            是否成功
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO shopee_products 
                (product_id, title, price, original_price, sales_count, rating, 
                 rating_count, seller_name, seller_id, stock, url, image_url, 
                 description, category, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.get('product_id'),
                product.get('title'),
                product.get('price'),
                product.get('original_price'),
                product.get('sales_count'),
                product.get('rating'),
                product.get('rating_count'),
                product.get('seller_name'),
                product.get('seller_id'),
                product.get('stock'),
                product.get('url'),
                product.get('image_url'),
                product.get('description'),
                product.get('category'),
                datetime.now()
            ))

            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"插入虾皮产品失败: {e}")
            return False
        finally:
            conn.close()

    def insert_amazon_product(self, product: Dict[str, Any]) -> bool:
        """
        插入或更新亚马逊产品
        
        Args:
            product: 产品数据字典
            
        Returns:
            是否成功
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO amazon_products 
                (asin, title, price, original_price, rating, rating_count, 
                 seller_name, stock_status, url, image_url, description, 
                 category, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.get('asin'),
                product.get('title'),
                product.get('price'),
                product.get('original_price'),
                product.get('rating'),
                product.get('rating_count'),
                product.get('seller_name'),
                product.get('stock_status'),
                product.get('url'),
                product.get('image_url'),
                product.get('description'),
                product.get('category'),
                datetime.now()
            ))

            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"插入亚马逊产品失败: {e}")
            return False
        finally:
            conn.close()

    def get_shopee_products(self, limit: int = None) -> List[Dict]:
        """获取虾皮产品"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM shopee_products ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products

    def get_amazon_products(self, limit: int = None) -> List[Dict]:
        """获取亚马逊产品"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM amazon_products ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products

    def get_product_count(self, platform: str) -> int:
        """获取产品数量"""
        conn = self.get_connection()
        cursor = conn.cursor()

        table = "shopee_products" if platform == "shopee" else "amazon_products"
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def export_to_csv(self, platform: str, filename: str):
        """导出数据到 CSV"""
        import pandas as pd

        if platform == "shopee":
            products = self.get_shopee_products()
        else:
            products = self.get_amazon_products()

        if products:
            df = pd.DataFrame(products)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"数据已导出到: {filename}")
        else:
            logger.warning(f"没有 {platform} 数据可导出")

    def clear_old_data(self, platform: str, days: int = 7):
        """清除指定天数前的数据"""
        conn = self.get_connection()
        cursor = conn.cursor()

        table = "shopee_products" if platform == "shopee" else "amazon_products"
        cursor.execute(f"""
            DELETE FROM {table} 
            WHERE crawled_at < datetime('now', '-{days} days')
        """)

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"删除了 {deleted} 条 {days} 天前的 {platform} 数据")
