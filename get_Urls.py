import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

chrome_driver_path = r'C:\Users\12703\Desktop\chrome-win64\chrome-win64\chromedriver-win64\chromedriver.exe'
chrome_binary_path = r'C:\Users\12703\Desktop\chrome-win64\chrome-win64\chrome.exe'

output_dir = "./"
os.makedirs(output_dir, exist_ok=True)
logger.info(f"创建输出目录: {output_dir}")

def extract_articles(url, port):
    logger.info(f"处理 URL: {url} 使用端口: {port}")
    
    options = Options()
    options.binary_location = chrome_binary_path
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

    try:
        logger.info(f"访问URL: {url}")
        start_time = time.time()
        driver.get(url)
        logger.info(f"页面加载耗时 {time.time() - start_time:.2f} 秒")

        logger.info("获取页面源代码")
        page_source = driver.page_source

        logger.info("使用 BeautifulSoup 解析页面源代码")
        soup = BeautifulSoup(page_source, 'html.parser')

        logger.info("提取文章标题和链接")
        articles = {}
        post_divs = soup.find_all('div', class_='post hentry uncustomized-post-template')
        
        for post in post_divs:
            title_element = post.find('h1', class_='post-title entry-title')
            if title_element and title_element.a:
                title = title_element.a.text.strip()
                link = title_element.a['href']
                articles[title] = link
                logger.info(f"提取文章: {title}")

        return articles

    except Exception as e:
        logger.error(f"处理 URL {url} 时发生错误: {str(e)}")
        return {}
    finally:
        driver.quit()
        logger.info(f"WebDriver 已关闭 (端口: {port})")

# 要处理的 URL
url = "https://program-think.blogspot.com/"

# 使用端口 9050
port = 9050

# 提取文章信息
articles = extract_articles(url, port)

# 保存到 JSON 文件
output_file = os.path.join(output_dir, "articles.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=4)

logger.info(f"文章信息已保存到 {output_file}")
logger.info(f"共提取 {len(articles)} 篇文章")
