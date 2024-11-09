import hashlib
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import markdown
import re
import logging
from urllib.parse import urlparse, urljoin
from flask import Flask, request, jsonify
from datetime import datetime
import os
from logging.handlers import RotatingFileHandler
import json


# Configure logging (same as before)
def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"medium_converter_{datetime.now().strftime('%Y%m%d')}.log")

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger('MediumConverter')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()


class MediumAuthentication:
    def __init__(self, cookie_file="medium_cookies.txt"):
        self.cookie_file = cookie_file
        self.cookies = self.load_cookies()

    def load_cookies(self):
        """Load Medium cookies from file"""
        try:
            with open(self.cookie_file, 'r') as f:
                cookie_string = f.read().strip()
                cookies = {}
                # Parse cookie string into dictionary
                for cookie in cookie_string.split(';'):
                    if '=' in cookie:
                        name, value = cookie.strip().split('=', 1)
                        cookies[name] = value
                logger.info("Successfully loaded Medium cookies")
                return cookies
        except FileNotFoundError:
            logger.warning(f"Cookie file {self.cookie_file} not found")
            return {}
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            return {}

    def save_cookies(self, cookie_string):
        """Save Medium cookies to file"""
        try:
            with open(self.cookie_file, 'w') as f:
                f.write(cookie_string)
            logger.info("Successfully saved Medium cookies")
            return True
        except Exception as e:
            logger.error(f"Failed to save cookies: {str(e)}")
            return False

    def update_cookies(self, cookie_string):
        """Update cookies from browser cookie string"""
        try:
            # Save the raw cookie string
            self.save_cookies(cookie_string)

            # Parse cookies for requests library
            cookies = {}
            for cookie in cookie_string.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    cookies[name] = value
            self.cookies = cookies
            logger.info("Successfully updated cookies")
            return True
        except Exception as e:
            logger.error(f"Failed to parse cookie string: {str(e)}")
            return False

    def get_cookie_header(self):
        """Get cookie string in header format"""
        try:
            with open(self.cookie_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""


class MediumToMarkdown:
    def __init__(self, image_dir="images"):
        self.auth = MediumAuthentication()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.image_dir = image_dir
        self.ensure_image_dir()

    def ensure_image_dir(self):
        """Ensure the image directory exists"""
        Path(self.image_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Image directory ensured: {self.image_dir}")

    def download_image(self, img_url):
        """Download image and return local path"""
        try:
            # Generate unique filename based on URL hash
            url_hash = hashlib.md5(img_url.encode()).hexdigest()

            # Get file extension from URL or default to .jpg
            parsed_url = urlparse(img_url)
            ext = os.path.splitext(parsed_url.path)[1]
            if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                ext = '.jpg'  # Default extension

            filename = f"{url_hash}{ext}"
            filepath = os.path.join(self.image_dir, filename)

            # If file already exists, return existing path
            if os.path.exists(filepath):
                logger.info(f"Image already exists: {filepath}")
                return filepath

            # Download image
            response = requests.get(
                img_url,
                headers=self.headers,
                cookies=self.auth.cookies,
                stream=True
            )
            response.raise_for_status()

            # Verify it's an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL {img_url} is not an image (content-type: {content_type})")
                return None

            # Save image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Successfully downloaded image: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to download image {img_url}: {str(e)}")
            return None

    def find_all_images(self, article):
        """查找文章中的所有图片"""
        images = []
        
        # 查找所有可能包含图片的容器
        image_containers = [
            # 直接的img标签
            article.find_all('img'),
            # figure中的图片
            article.find_all('figure', class_=lambda x: x and 'image' in x.lower()),
            # Medium特有的图片容器
            article.find_all('div', class_=lambda x: x and 'image' in x.lower()),
            # 带有background-image的div
            article.find_all('div', style=lambda x: x and 'background-image' in str(x))
        ]

        for container_list in image_containers:
            for container in container_list:
                if container.name == 'img':
                    images.append(container)
                else:
                    # 对于figure和div容器，查找内部的img标签
                    img = container.find('img')
                    if img:
                        images.append(img)
                    else:
                        # 处理background-image
                        style = container.get('style', '')
                        url_match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                        if url_match:
                            img_url = url_match.group(1)
                            new_img = BeautifulSoup().new_tag('img', src=img_url)
                            images.append(new_img)

        # 去重
        seen_urls = set()
        unique_images = []
        for img in images:
            src = img.get('src', '') or img.get('data-src', '')
            if src and src not in seen_urls:
                seen_urls.add(src)
                unique_images.append(img)

        return unique_images

    def extract_content(self, html):
        """Extract and convert article content to markdown"""
        logger.info("Starting content extraction")
        soup = BeautifulSoup(html, 'html.parser')

        # Initialize markdown content with metadata
        markdown_content = ""

        # Extract article title
        title = soup.find('h1')
        if title:
            title_text = title.get_text().strip()
            markdown_content += f"# {title_text}\n\n"
            logger.info(f"Extracted title: {title_text}")

        # Find and process the main article content
        article = soup.find('article')
        if not article:
            logger.error("Could not find article content")
            raise Exception("Could not find article content")

        logger.info("Processing article elements")

        # 首先处理所有图片
        images = self.find_all_images(article)
        image_markdowns = {}
        for img in images:
            parent = img.parent
            key = str(parent)
            img_markdown = self.process_image(img)
            if img_markdown:
                image_markdowns[key] = img_markdown

        # 处理文章内容
        for element in article.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'pre', 'blockquote', 'ul', 'ol', 'figure', 'div']):
            # 如果这个元素包含图片，先处理图片
            if str(element) in image_markdowns:
                markdown_content += image_markdowns[str(element)]
                continue

            # Headers
            if element.name in ['h1', 'h2', 'h3', 'h4']:
                level = int(element.name[1])
                text = element.get_text().strip()
                markdown_content += f"{'#' * level} {text}\n\n"

            # Paragraphs
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    if element.find('code'):
                        code = element.find('code').get_text()
                        markdown_content += f"`{code}`\n\n"
                    else:
                        text = text.replace('*', r'\*')
                        markdown_content += f"{text}\n\n"

            # Code blocks
            elif element.name == 'pre':
                code = element.get_text().strip()
                code_element = element.find('code')
                language = code_element.get('class', [''])[0].replace('language-', '') if code_element else ''
                markdown_content += f"```{language}\n{code}\n```\n\n"

            # Blockquotes
            elif element.name == 'blockquote':
                quote = element.get_text().strip()
                markdown_content += f"> {quote}\n\n"

            # Lists
            elif element.name in ['ul', 'ol']:
                for idx, li in enumerate(element.find_all('li', recursive=False)):
                    prefix = '* ' if element.name == 'ul' else f"{idx + 1}. "
                    item_text = li.get_text().strip()
                    markdown_content += f"{prefix}{item_text}\n"
                markdown_content += "\n"

        return markdown_content

    def process_image(self, img_element, caption_element=None):
        """Process an image element and return markdown"""
        try:
            # 获取图片URL
            src = img_element.get('src', '')
            if not src:
                src = img_element.get('data-src', '')
            
            if not src:
                logger.warning("Found image element without source URL")
                return None

            # 确保URL是绝对路径
            if not src.startswith(('http://', 'https://')):
                src = urljoin('https://medium.com', src)

            # 下载图片
            local_path = self.download_image(src)
            if not local_path:
                return None

            # 获取alt文本
            alt_text = img_element.get('alt', '').strip()
            if not alt_text:
                alt_text = "Image"

            # 处理caption
            caption_text = ""
            if caption_element:
                caption_text = caption_element.get_text().strip()
                if caption_text:
                    caption_text = f"\n*{caption_text}*"  # 使用斜体显示caption

            # 创建相对路径
            relative_path = os.path.relpath(local_path, start=os.getcwd())
            relative_path = relative_path.replace('\\', '/')

            # 返回完整的markdown图片语法
            return f"![{alt_text}]({relative_path}){caption_text}\n\n"

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

    def get_image_attributes(self, img_element):
        """获取图片的属性（宽度、高度、对齐方式等）"""
        try:
            width = img_element.get('width', '')
            height = img_element.get('height', '')
            
            # 获取父元素的样式
            parent = img_element.parent
            style = parent.get('style', '') if parent else ''
            
            # 解析对齐方式
            align = 'center'  # Medium默认居中对齐
            if 'text-align: left' in style:
                align = 'left'
            elif 'text-align: right' in style:
                align = 'right'
                
            return {
                'width': width,
                'height': height,
                'align': align
            }
        except Exception as e:
            logger.error(f"Error getting image attributes: {str(e)}")
            return {}

    def clean_markdown(self, content):
        """Clean up the markdown content"""
        logger.info("Cleaning markdown content")

        # 移除多余的空行，但保留必要的间距
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        # 保留Unicode字符，只清理不可打印字符
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        # 修复标题周围的空格
        content = re.sub(r'(\n#{1,6}.*)\n([^\n])', r'\1\n\n\2', content)
        
        # 修复列表格式
        content = re.sub(r'\n\*\s*\n', '\n', content)
        
        # 确保图片和其caption之间有适当的间距
        content = re.sub(r'(!\[.*?\].*?\))(\n\*.*?\*)', r'\1\n\2', content)
        
        # 移除行尾空格但保留换行
        content = '\n'.join(line.rstrip() for line in content.split('\n'))
        
        return content.strip()

    def validate_url(self, url):
        """Validate if the URL is a Medium article"""
        parsed_url = urlparse(url)
        return parsed_url.netloc in ['medium.com', 'towardsdatascience.com', 'betterhumans.pub', "datadriveninvestor.com"]

    def fetch_article(self, url):
        """Fetch the HTML content of the Medium article"""
        try:
            response = requests.get(url, headers=self.headers, cookies=self.auth.cookies)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch article: {str(e)}")
            raise

    def convert(self, url, filename=None):
        """Convert Medium article to markdown"""
        logger.info(f"Starting conversion for URL: {url}")

        # if not self.validate_url(url):
        #     logger.error(f"Invalid URL provided: {url}")
        #     raise ValueError("Not a valid Medium URL")

        try:
            # Fetch the article
            html = self.fetch_article(url)

            # Extract and convert content
            markdown_content = self.extract_content(html)

            # Clean up the markdown
            cleaned_content = self.clean_markdown(markdown_content)

            logger.info("Successfully converted article to markdown")

            # Save markdown to file if filename is provided
            if filename:
                self.save_markdown(cleaned_content, filename)
            return cleaned_content

        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise

    def save_markdown(self, content, filename):
        """Save markdown content to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Successfully saved markdown to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save markdown: {str(e)}")
            return False


# Initialize Flask app
app = Flask(__name__)
converter = MediumToMarkdown()


@app.route('/auth/cookies', methods=['POST'])
def update_cookies():
    """Update Medium authentication cookies"""
    try:
        data = request.get_json()
        if not data or 'cookies' not in data:
            logger.error("No cookies provided in request")
            return jsonify({
                "error": "No cookies provided",
                "status": "error"
            }), 400

        cookie_string = data['cookies']
        if converter.auth.update_cookies(cookie_string):
            return jsonify({
                "message": "Cookies updated successfully",
                "status": "success"
            })
        else:
            return jsonify({
                "error": "Failed to update cookies",
                "status": "error"
            }), 500

    except Exception as e:
        logger.error(f"Cookie update error: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/convert', methods=['POST'])
def convert_article():
    """API endpoint to convert Medium article to markdown"""
    logger.info("Received conversion request")

    try:
        data = request.get_json()
        if not data or 'url' not in data:
            logger.error("No URL provided in request")
            return jsonify({
                "error": "No URL provided",
                "status": "error"
            }), 400

        url = data['url']
        filename = data.get('filename', None)
        logger.info(f"Processing URL: {url}")

        try:
            markdown_content = converter.convert(url, filename)
            logger.info("Successfully converted article")
            return jsonify({
                "markdown": markdown_content,
                "status": "success"
            })
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            return jsonify({
                "error": str(ve),
                "status": "error"
            }), 400
        except Exception as e:
            logger.error(f"Conversion error: {str(e)}")
            return jsonify({
                "error": str(e),
                "status": "error"
            }), 500

    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        return jsonify({
            "error": "Invalid request",
            "status": "error"
        }), 400


if __name__ == '__main__':
    logger.info("Starting Medium to Markdown API service")
    app.run(host='0.0.0.0', port=5050, debug=False)
