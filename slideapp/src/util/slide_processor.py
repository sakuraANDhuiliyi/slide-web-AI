import re
import os
import uuid
import requests
from urllib.parse import urlparse
from django.conf import settings
from .image_search import extract_keywords_with_ai, search_unsplash_images

def process_slides_with_images(markdown_content):
    """
    处理幻灯片内容，为每个章节添加相关图片
    
    Args:
        markdown_content (str): 原始Markdown内容
    
    Returns:
        str: 添加了图片的Markdown内容
    """
    try:
        # 使用更精确的正则表达式，分割幻灯片内容为章节
        # 匹配 --- 或 ---- 作为分隔符，确保前后有空行
        sections = re.split(r'(?:\r?\n|\r){1,2}(?:---|----|\+\+\+\+)(?:\r?\n|\r){1,2}', markdown_content)
        
        # 如果分割失败，尝试备用方法
        if len(sections) <= 1:
            # 尝试其他可能的分隔符模式
            sections = re.split(r'(?:\r?\n|\r)?(?:---|----|\+\+\+\+)(?:\r?\n|\r)?', markdown_content)
            
            # 如果仍然分割失败，尝试最宽松的匹配
            if len(sections) <= 1:
                sections = re.split(r'---|----|\+\+\+\+', markdown_content)
        
        processed_sections = []
        
        for section in sections:
            # 跳过空白章节
            if not section.strip():
                continue
                
            # 提取章节的关键词
            keywords = extract_keywords_with_ai(section)
            
            if keywords:
                # 搜索相关图片
                images = search_unsplash_images(keywords)
                
                if images and len(images) > 0:
                    # 选择第一张图片
                    image = images[0]
                    
                    # 尝试下载并本地化图片
                    local_image_path = None
                    try:
                        local_image_path = download_and_save_image(image['url'])
                    except Exception as e:
                        print(f"下载图片失败: {str(e)}")
                    
                    # 构建图片Markdown代码
                    if local_image_path:
                        # 使用本地路径
                        img_markdown = f"\n\n![{image['alt']}]({local_image_path})\n\n"
                    else:
                        # 使用原始URL
                        img_markdown = f"\n\n![{image['alt']}]({image['url']})\n\n"
                    
                    # 添加图片引用和图片
                    section = f"{section}\n\n{img_markdown}"
                    
                    # 添加图片来源信息
                    section += f"<small>Photo by [{image['credit']['name']}]({image['credit']['link']})</small>\n"
            
            processed_sections.append(section)
        
        # 重新组合内容，使用正确的分隔符
        result = ""
        for i, section in enumerate(processed_sections):
            if i > 0:
                result += "\n\n---\n\n"
            result += section
        
        return result
    except Exception as e:
        print(f"处理幻灯片内容出错: {str(e)}")
        # 出错时返回原始内容，确保不会丢失用户数据
        return markdown_content

def download_and_save_image(url):
    """
    下载并保存图片到本地
    
    Args:
        url (str): 图片URL
    
    Returns:
        str: 本地图片路径
    """
    try:
        # 解析URL，获取文件名
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)
        
        # 如果文件名不包含扩展名，添加.jpg
        if not file_name or '.' not in file_name:
            file_name = f"{uuid.uuid4()}.jpg"
        
        # 确保文件名唯一
        file_name = f"{uuid.uuid4()}_{file_name}"
        
        # 构建保存路径
        media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
        slides_dir = os.path.join(media_root, 'slides')
        
        # 确保目录存在
        os.makedirs(slides_dir, exist_ok=True)
        
        # 完整的保存路径
        save_path = os.path.join(slides_dir, file_name)
        
        # 下载图片
        response = requests.get(url, stream=True, verify=False, timeout=10)
        response.raise_for_status()
        
        # 保存图片
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 返回相对于MEDIA_URL的路径
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        return f"{media_url}slides/{file_name}"
    except Exception as e:
        print(f"下载并保存图片失败: {str(e)}")
        return None 