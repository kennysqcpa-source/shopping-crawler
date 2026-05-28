"""
购物平台爬虫主程序
"""

import logging
import argparse
import sys
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 确保日志目录存在
Path('logs').mkdir(exist_ok=True)

logger = logging.getLogger(__name__)

# 导入配置和模块
from config import KEYWORDS, PAGES, DB_PATH
from database import DatabaseManager
from scrapers.shopee_crawler import ShopeeeCrawler
from scrapers.amazon_crawler import AmazonCrawler


def init_db():
    """初始化数据库"""
    db = DatabaseManager(DB_PATH)
    logger.info(f"数据库已初始化: {DB_PATH}")
    return db


def crawl_shopee(keyword: str, pages: int, db: DatabaseManager):
    """
    爬取虾皮数据
    
    Args:
        keyword: 搜索关键字
        pages: 页数
        db: 数据库管理器
    """
    logger.info("=" * 60)
    logger.info(f"开始爬取虾皮数据 - 关键字: {keyword}, 页数: {pages}")
    logger.info("=" * 60)
    
    try:
        crawler = ShopeeeCrawler()
        products = crawler.search_products(keyword, pages)
        
        if products:
            count = 0
            for product in products:
                if db.insert_shopee_product(product):
                    count += 1
            
            logger.info(f"成功保存 {count}/{len(products)} 个虾皮产品到数据库")
        else:
            logger.warning("未获取到虾皮产品")
            
    except Exception as e:
        logger.error(f"爬取虾皮数据失败: {e}", exc_info=True)


def crawl_amazon(keyword: str, pages: int, db: DatabaseManager):
    """
    爬取亚马逊数据
    
    Args:
        keyword: 搜索关键字
        pages: 页数
        db: 数据库管理器
    """
    logger.info("=" * 60)
    logger.info(f"开始爬取亚马逊数据 - 关键字: {keyword}, 页数: {pages}")
    logger.info("=" * 60)
    
    try:
        crawler = AmazonCrawler()
        products = crawler.search_products(keyword, pages)
        
        if products:
            count = 0
            for product in products:
                if db.insert_amazon_product(product):
                    count += 1
            
            logger.info(f"成功保存 {count}/{len(products)} 个亚马逊产品到数据库")
        else:
            logger.warning("未获取到亚马逊产品")
            
    except Exception as e:
        logger.error(f"爬取亚马逊数据失败: {e}", exc_info=True)


def show_statistics(db: DatabaseManager):
    """显示统计信息"""
    logger.info("=" * 60)
    logger.info("数据统计")
    logger.info("=" * 60)
    
    shopee_count = db.get_product_count('shopee')
    amazon_count = db.get_product_count('amazon')
    
    logger.info(f"虾皮产品数量: {shopee_count}")
    logger.info(f"亚马逊产品数量: {amazon_count}")
    logger.info(f"总产品数量: {shopee_count + amazon_count}")


def export_data(platform: str, db: DatabaseManager, filename: str = None):
    """
    导出数据到 CSV
    
    Args:
        platform: 平台名称 (shopee/amazon)
        db: 数据库管理器
        filename: 文件名（可选）
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"export_{platform}_{timestamp}.csv"
    
    db.export_to_csv(platform, filename)
    logger.info(f"数据已导出到: {filename}")


def show_data(db: DatabaseManager, platform: str = 'all', limit: int = 10):
    """显示数据库中的产品"""
    logger.info("=" * 60)
    logger.info(f"显示数据 (最多 {limit} 条)")
    logger.info("=" * 60)
    
    if platform in ['shopee', 'all']:
        shopee_products = db.get_shopee_products(limit)
        if shopee_products:
            logger.info(f"\n虾皮产品 ({len(shopee_products)} 条):")
            for i, p in enumerate(shopee_products, 1):
                logger.info(f"  {i}. {p['title'][:50]} - ¥{p['price']}")
        else:
            logger.info("虾皮：无数据")
    
    if platform in ['amazon', 'all']:
        amazon_products = db.get_amazon_products(limit)
        if amazon_products:
            logger.info(f"\n亚马逊产品 ({len(amazon_products)} 条):")
            for i, p in enumerate(amazon_products, 1):
                logger.info(f"  {i}. {p['title'][:50]} - ${p['price']}")
        else:
            logger.info("亚马逊：无数据")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='购物平台爬虫 - 爬取虾皮和亚马逊产品数据'
    )
    
    parser.add_argument(
        '--platform',
        choices=['shopee', 'amazon', 'all'],
        default='all',
        help='指定爬取的平台 (默认: all)'
    )
    
    parser.add_argument(
        '--keyword',
        type=str,
        default=None,
        help='指定搜索关键字 (默认: 配置文件中的关键字)'
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=PAGES,
        help=f'指定爬取页数 (默认: {PAGES})'
    )
    
    parser.add_argument(
        '--show-data',
        action='store_true',
        help='显示数据库中的产品'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        nargs='?',
        const='all',
        help='导出数据到 CSV (指定平台: shopee/amazon/all)'
    )
    
    parser.add_argument(
        '--clean-old-data',
        type=int,
        metavar='DAYS',
        help='清除指定天数前的数据'
    )
    
    args = parser.parse_args()
    
    # 初始化数据库
    db = init_db()
    
    # 处理导出数据
    if args.export:
        if args.export == 'all':
            export_data('shopee', db)
            export_data('amazon', db)
        elif args.export in ['shopee', 'amazon']:
            export_data(args.export, db)
        return
    
    # 处理清除旧数据
    if args.clean_old_data:
        logger.info(f"删除 {args.clean_old_data} 天前的虾皮数据...")
        db.clear_old_data('shopee', args.clean_old_data)
        logger.info(f"删除 {args.clean_old_data} 天前的亚马逊数据...")
        db.clear_old_data('amazon', args.clean_old_data)
        return
    
    # 处理显示数据
    if args.show_data:
        show_data(db, args.platform, limit=20)
        show_statistics(db)
        return
    
    # 使用指定的关键字或配置文件中的关键字
    keywords = [args.keyword] if args.keyword else KEYWORDS
    
    logger.info(f"开始爬虫任务 - 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 爬取数据
    for keyword in keywords:
        if args.platform in ['shopee', 'all']:
            crawl_shopee(keyword, args.pages, db)
        
        if args.platform in ['amazon', 'all']:
            crawl_amazon(keyword, args.pages, db)
    
    # 显示统计信息
    show_statistics(db)
    
    logger.info(f"爬虫任务完成 - 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("用户中断了爬虫任务")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        sys.exit(1)
