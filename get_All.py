import os
import json
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import base64
import time
import concurrent.futures

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

chrome_driver_path = r'C:\Users\12703\Desktop\chrome-win64\chrome-win64\chromedriver-win64\chromedriver.exe'
chrome_binary_path = r'C:\Users\12703\Desktop\chrome-win64\chrome-win64\chrome.exe'

output_dir = "编程随想"
os.makedirs(output_dir, exist_ok=True)
logger.info(f"创建输出目录: {output_dir}")

def clean_filename(filename):
    # 移除或替换不允许的字符
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    # 将文件名截断到合适的长度（例如255个字符）
    return filename[:255]

def process_url(title, url, port):
    print('title', title)
    print('url', url)
    print('port', port)
    
    # 清理文件名
    clean_title = clean_filename(title)
    output_file = os.path.join(output_dir, f"{clean_title}.html")
    if os.path.exists(output_file):
        logger.info(f"文件 {output_file} 已存在，跳过处理")
        return

    time.sleep(2)
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

        logger.info("选择目标内容")
        target_content = soup

        if target_content:
            logger.info("目标内容已找到。正在处理...")
            
            # 处理图片
            images = target_content.find_all('img')
            logger.info(f"找到 {len(images)} 张图片")
            for i, img in enumerate(images, 1):
                src = img.get('src')
                if src:
                    logger.info(f"处理第 {i}/{len(images)} 张图片: {src}")
                    try:
                        img_data = requests.get(src).content
                        img['src'] = f"data:image/png;base64,{base64.b64encode(img_data).decode()}"
                        logger.info(f"第 {i} 张图片嵌入成功")
                    except Exception as e:
                        logger.error(f"处理第 {i} 张图片失败: {str(e)}")
            
            # 保存处理后的内容
            logger.info(f"保存处理后的内容到 {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(str(target_content))
            logger.info("内容保存成功")
        else:
            logger.warning("未找到目标内容")

    except Exception as e:
        logger.error(f"处理 URL {url} 时发生错误: {str(e)}")
    finally:
        driver.quit()
        logger.info(f"WebDriver 已关闭 (端口: {port})")

# 读取 articles.json 文件
articles_file = os.path.join(output_dir, "articles.json")
with open(articles_file, 'r', encoding='utf-8') as f:
    articles = json.load(f)

ports = range(9050, 9060)
batch_size = len(ports)

for i in range(0, len(articles), batch_size):
    batch = list(articles.items())[i:i + batch_size]
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as executor:
        futures = [executor.submit(process_url, title, url, port) for (title, url), port in zip(batch, ports)]
        concurrent.futures.wait(futures)

logger.info("所有 URL 处理完成")
