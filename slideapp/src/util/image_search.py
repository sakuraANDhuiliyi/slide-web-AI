import requests
import os
import json
import google.generativeai as genai
import warnings
import urllib3
from django.conf import settings

# 禁用SSL验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 强制禁用SSL验证，解决证书问题
old_merge_environment_settings = requests.Session.merge_environment_settings

def override_merge_environment_settings(self, url, proxies, stream, verify, cert):
    settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
    settings['verify'] = False
    return settings

requests.Session.merge_environment_settings = override_merge_environment_settings

def extract_keywords_with_ai(text):
    """
    使用AI从幻灯片内容中提取关键词
    
    Args:
        text (str): 幻灯片内容文本
    
    Returns:
        str: 关键词，用于图片搜索
    """
    try:
        # 获取API密钥
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if not api_key:
            api_key = getattr(settings, 'GEMINI_API_KEY', '')
        
        if not api_key:
            return None
        
        genai.configure(api_key=api_key)
        # 确保每次都创建新实例
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        从以下幻灯片内容中提取最关键、最能代表内容核心的1-2个关键词，这些关键词将用于搜索与幻灯片内容相关的图片。
        关键词应该具有视觉表现力，适合通过图片来表达。
        请直接返回关键词，不要添加任何额外的文字或解释。
        如果有多个关键词，请用英文逗号分隔。

        幻灯片内容:
        {text}
        """
        
        response = model.generate_content(prompt)
        keywords = response.text.strip()
        
        return keywords
    except Exception as e:
        print(f"提取关键词失败: {str(e)}")
        # 返回默认关键词，确保至少有一些图片可用
        return "presentation slide"

def search_unsplash_images(query, per_page=3):
    """
    搜索Unsplash图片
    
    Args:
        query (str): 搜索关键词
        per_page (int): 每页返回的图片数量
        
    Returns:
        list: 图片URL列表
    """
    try:
        access_key = os.environ.get('UNSPLASH_ACCESS_KEY', '')
        if not access_key:
            access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '')
        
        if not access_key:
            return use_fallback_images()
        
        # 使用本地图片作为备选
        try:
            url = f"https://api.unsplash.com/search/photos"
            headers = {
                "Authorization": f"Client-ID {access_key}"
            }
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape"
            }
            
            # 禁用SSL验证，解决SSL错误问题
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=5)
            data = response.json()
            
            if "results" in data and len(data["results"]) > 0:
                images = []
                for photo in data["results"]:
                    images.append({
                        "url": photo["urls"]["regular"],
                        "alt": photo.get("alt_description", query),
                        "credit": {
                            "name": photo["user"]["name"],
                            "link": f"https://unsplash.com/@{photo['user']['username']}?utm_source=jyyslideapp&utm_medium=referral"
                        }
                    })
                return images
        except Exception as e:
            print(f"Unsplash API调用失败: {str(e)}")
        
        return use_fallback_images()
    except Exception as e:
        print(f"搜索图片失败: {str(e)}")
        return use_fallback_images()

def use_fallback_images():
    """返回本地默认图片作为备选"""
    # 如果本地有图片，使用本地图片
    static_img_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'img')
    if os.path.exists(static_img_dir):
        images = []
        img_files = [f for f in os.listdir(static_img_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        
        # 如果有图片文件
        if img_files:
            selected_img = img_files[0]  # 默认选第一个
            img_url = f"/static/img/{selected_img}"
            images.append({
                "url": img_url,
                "alt": "Default image",
                "credit": {
                    "name": "Local Image",
                    "link": "#"
                }
            })
            return images
    
    # 如果本地也没有图片，返回一个免费的在线图片
    return [{
        "url": "https://placehold.co/800x450?text=Slide+Image",
        "alt": "Placeholder image",
        "credit": {
            "name": "Placeholder",
            "link": "#"
        }
    }] 