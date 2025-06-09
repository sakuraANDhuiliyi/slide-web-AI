from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import os
import uuid
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import os
import uuid
from django.conf import settings
from imghdr import what
import google.generativeai as genai
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Slide
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
import re
import requests
from urllib.parse import urlparse
from .src.util.image_search import extract_keywords_with_ai, search_unsplash_images
from .utils.pptx_exporter import markdown_to_pptx
from .src.util.slide_processor import process_slides_with_images
from .src.util.document_processor import process_uploaded_document

# 设置Gemini API密钥，从环境变量或设置中获取
def get_gemini_api_key():
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        # 如果环境变量中没有，尝试从Django设置中获取
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
    return api_key

def download_remote_image(image_url, alt_text='image'):
    """
    下载远程图片到本地media目录
    
    Args:
        image_url (str): 远程图片URL
        alt_text (str): 图片描述
        
    Returns:
        str: 本地图片URL
    """
    try:
        # 如果URL已经是本地URL，直接返回
        if image_url.startswith('/'):
            return image_url
            
        # 生成唯一的文件名
        file_ext = os.path.splitext(urlparse(image_url).path)[-1]
        if not file_ext:
            file_ext = '.jpg'  # 默认扩展名
        filename = f"{alt_text.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}{file_ext}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'ai_images')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        
        # 下载图片（禁用SSL验证）
        response = requests.get(image_url, stream=True, verify=False, timeout=10)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    
            # 返回本地URL
            return f"{settings.MEDIA_URL}ai_images/{filename}"
    except Exception as e:
        print(f"下载图片失败: {str(e)}")
    
    # 如果下载失败，返回默认图片
    return "/static/img/auto-title.jpg"

@login_required
def ai_generate_slide(request):
    """处理AI生成幻灯片的请求"""
    if request.method == 'POST':
        # 获取表单数据
        title = request.POST.get('title', '未命名')
        content_requirements = request.POST.get('content_requirements', '')
        slides_count = request.POST.get('slides_count', '5')
        style = request.POST.get('style', 'academic')
        layout = request.POST.get('layout', 'horizontal_vertical')
        auto_insert_images = request.POST.get('auto_insert_images', 'on') == 'on'
        
        try:
            # 设置API密钥
            api_key = get_gemini_api_key()
            if not api_key:
                return render(request, 'ai_generate.html', {
                    'error': 'Gemini API密钥未配置，请联系管理员。'
                })
            
            # 每次请求重新配置API客户端，避免会话问题
            genai.configure(api_key=api_key)
            
            # 创建生成模型
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # 根据布局选择构建不同的提示信息
            layout_instructions = ""
            if layout == "horizontal_vertical":
                layout_instructions = """
                4. 幻灯片布局规则：
                   - 使用 "---" (三个减号的单独行) 来划分水平幻灯片（不同章节）
                   - 使用 "----" (四个减号的单独行) 来划分垂直幻灯片（同一章节内的不同内容）
                5. 请严格遵循这种结构：
                   
                   # 第一章节
                   内容
                   
                   ---
                   
                   # 第二章节
                   
                   ----
                   
                   ## 第二章节的第一个子页
                   内容
                   
                   ----
                   
                   ## 第二章节的第二个子页
                   内容
                
                注意：
                - 幻灯片内容应精简、重点突出
                - 每个分隔符必须独占一行，前后都有空行
                - 总共生成{slides_count}个左右的章节，每个章节可包含1-3个垂直幻灯片
                - 必须是纯Markdown格式，不要加额外的HTML或其他标记
                """
            elif layout == "horizontal_only":
                layout_instructions = """
                4. 幻灯片布局规则：
                   - 使用 "---" (三个减号的单独行) 来划分幻灯片
                5. 请严格遵循这种结构：
                   
                   # 第一个幻灯片
                   内容
                   
                   ---
                   
                   # 第二个幻灯片
                   内容
                   
                   ---
                   
                   # 第三个幻灯片
                   内容
                
                注意：
                - 幻灯片内容应精简、重点突出
                - 每个分隔符必须独占一行，前后都有空行
                - 总共生成{slides_count}张幻灯片
                - 必须是纯Markdown格式，不要加额外的HTML或其他标记
                """
            else:  # with_animation
                layout_instructions = """
                4. 幻灯片布局规则：
                   - 使用 "---" (三个减号的单独行) 来划分水平幻灯片（不同章节）
                   - 使用 "----" (四个减号的单独行) 来划分垂直幻灯片（同一章节内的不同内容）
                   - 使用 "++++" (四个加号的单独行) 来创建渐变幻灯片（展示内容的变化过程）
                5. 请严格遵循这种结构：
                   
                   # 第一章节
                   内容
                   
                   ---
                   
                   # 第二章节
                   
                   ----
                   
                   ## 第二章节的第一个子页
                   内容
                   
                   ----
                   
                   ## 第二章节的渐变演示
                   初始内容
                   
                   ++++
                   
                   ## 第二章节的渐变演示
                   初始内容（保持不变）
                   新增的内容（展示变化）
                
                注意：
                - 幻灯片内容应精简、重点突出
                - 每个分隔符必须独占一行，前后都有空行
                - 总共生成{slides_count}个左右的章节，适当使用垂直和渐变效果
                - 渐变效果适合用于展示步骤变化、代码演进等场景
                - 必须是纯Markdown格式，不要加额外的HTML或其他标记
                """
            
            # 构建提示信息
            prompt = f"""
            请为我生成一个Markdown格式的幻灯片内容，遵循以下要求：
            
            - 主题: {title}
            - 风格: {style}
            - 幻灯片数量: {slides_count}
            - 要求: {content_requirements}
            
            请使用以下Markdown语法格式生成幻灯片:
            
            1. 使用 # 后跟文字表示章节标题幻灯片
            2. 使用 ## 后跟文字表示普通幻灯片的标题
            3. 正文内容直接使用Markdown语法
            {layout_instructions}
            """
            
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            response = None
            
            while retry_count < max_retries:
                try:
                    # 生成内容
                    response = model.generate_content(prompt)
                    break
                except Exception as e:
                    retry_count += 1
                    print(f"API调用失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                    if retry_count >= max_retries:
                        raise
                    # 短暂延迟后重试
                    import time
                    time.sleep(1)
            
            if not response:
                raise Exception("无法从AI服务获取响应")
                
            markdown_content = response.text
            
            # 如果勾选了自动插入图片，使用AI提取关键词并搜索图片
            if auto_insert_images and getattr(settings, 'AUTO_INSERT_IMAGES', True):
                markdown_content = process_slides_with_images(markdown_content)
            
            # 创建新的幻灯片
            slide = Slide.objects.create(
                title=title,
                content=markdown_content,
                lock=True
            )
            
            # 重定向到编辑页面
            return redirect('edit_slide', slide_id=slide.id)
            
        except Exception as e:
            import traceback
            error_detail = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"生成幻灯片出错详情: {error_detail}")
            
            # 处理API请求或其他错误
            return render(request, 'ai_generate.html', {
                'error': f'生成幻灯片时出错: {str(e)}',
                'title': title,
                'content_requirements': content_requirements,
                'slides_count': slides_count,
                'style': style,
                'layout': layout
            })
    
    # GET请求时显示表单页面
    return render(request, 'ai_generate.html')

def process_slides_with_images(markdown_content):
    """
    处理幻灯片内容，为每个幻灯片添加相关图片
    
    Args:
        markdown_content (str): 原始Markdown内容
        
    Returns:
        str: 添加图片后的Markdown内容
    """
    # 先保存原始内容作为备份
    original_content = markdown_content
    
    try:
        # 处理水平幻灯片（章节）、垂直幻灯片（节）和渐变幻灯片
        slides_structure = []
        
        # 先按水平分隔符分割
        h_slides = re.split(r'\n\s*---\s*\n', markdown_content)
        
        for h_idx, h_slide in enumerate(h_slides):
            # 检查水平幻灯片是否包含垂直分隔符
            if '\n----\n' in h_slide:
                # 按垂直分隔符分割
                v_slides = re.split(r'\n\s*----\s*\n', h_slide)
                
                for v_idx, v_slide in enumerate(v_slides):
                    # 检查是否包含渐变幻灯片分隔符
                    if '\n++++\n' in v_slide:
                        # 按渐变幻灯片分隔符分割
                        a_slides = re.split(r'\n\s*\+\+\+\+\s*\n', v_slide)
                        
                        for a_idx, a_slide in enumerate(a_slides):
                            slides_structure.append({
                                'content': a_slide.strip(),
                                'h_idx': h_idx,
                                'v_idx': v_idx,
                                'a_idx': a_idx,
                                'type': 'animate',
                                'is_vertical': v_idx > 0,
                                'is_animate': a_idx > 0
                            })
                    else:
                        slides_structure.append({
                            'content': v_slide.strip(),
                            'h_idx': h_idx,
                            'v_idx': v_idx,
                            'a_idx': 0,
                            'type': 'vertical',
                            'is_vertical': v_idx > 0,
                            'is_animate': False
                        })
            else:
                # 没有垂直分隔符，检查是否有渐变分隔符
                if '\n++++\n' in h_slide:
                    # 按渐变幻灯片分隔符分割
                    a_slides = re.split(r'\n\s*\+\+\+\+\s*\n', h_slide)
                    
                    for a_idx, a_slide in enumerate(a_slides):
                        slides_structure.append({
                            'content': a_slide.strip(),
                            'h_idx': h_idx,
                            'v_idx': 0,
                            'a_idx': a_idx,
                            'type': 'animate_horizontal',
                            'is_vertical': False,
                            'is_animate': a_idx > 0
                        })
                else:
                    # 普通水平幻灯片
                    slides_structure.append({
                        'content': h_slide.strip(),
                        'h_idx': h_idx,
                        'v_idx': 0,
                        'a_idx': 0,
                        'type': 'horizontal',
                        'is_vertical': False,
                        'is_animate': False
                    })
        
        # 处理每个幻灯片，添加图片
        # 渐变幻灯片（animate）不添加图片，以保持专注于内容变化
        for slide in slides_structure:
            # 跳过渐变幻灯片
            if slide['is_animate']:
                continue
                
            # 如果幻灯片已经包含图片，不再添加
            if '![' in slide['content']:
                continue
                
            # 提取关键词
            keywords = extract_keywords_with_ai(slide['content'])
            if not keywords:
                continue
                
            # 搜索图片
            images = search_unsplash_images(keywords, per_page=1)
            if not images:
                continue
                
            # 获取图片信息
            image = images[0]
            
            # 将远程图片下载到本地
            local_image_url = download_remote_image(image['url'], image['alt'])
            
            # 在幻灯片末尾添加图片（确保有足够的空行）
            # 准备Markdown格式的图片，带有感谢Unsplash的注释
            image_markdown = f"\n\n![{image['alt']}]({local_image_url})\n*Photo by [{image['credit']['name']}]({image['credit']['link']}) on Unsplash*"
            
            # 将图片添加到幻灯片末尾
            if not slide['content'].endswith('\n\n'):
                if slide['content'].endswith('\n'):
                    slide['content'] += '\n' + image_markdown
                else:
                    slide['content'] += '\n\n' + image_markdown
            else:
                slide['content'] += image_markdown
        
        # 重新组合幻灯片内容
        result = ''
        current_h_idx = -1
        current_v_idx = -1
        current_a_idx = -1
        
        for i, slide in enumerate(slides_structure):
            if slide['h_idx'] != current_h_idx:
                # 新的水平幻灯片（章节）
                if current_h_idx != -1:
                    result += '\n\n---\n\n'
                current_h_idx = slide['h_idx']
                current_v_idx = slide['v_idx']
                current_a_idx = slide['a_idx']
                result += slide['content']
            elif slide['v_idx'] != current_v_idx:
                # 同一章节的垂直幻灯片
                result += '\n\n----\n\n' + slide['content']
                current_v_idx = slide['v_idx']
                current_a_idx = slide['a_idx']
            else:
                # 渐变幻灯片
                result += '\n\n++++\n\n' + slide['content']
                current_a_idx = slide['a_idx']
        
        return result
    except Exception as e:
        print(f"处理幻灯片图片时发生错误: {str(e)}")
        # 发生错误时返回原始内容
        return original_content

@login_required
def upload_image(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image and image.content_type.startswith('image/'):
            # 生成唯一的文件名，防止冲突
            ext = os.path.splitext(image.name)[1]
            filename = uuid.uuid4().hex + ext
            filepath = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

            # 确保上传目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # 保存文件
            with open(filepath, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # 返回图片的访问 URL
            url = settings.MEDIA_URL + 'uploads/' + filename
            return JsonResponse({'url': url})
        else:
            return JsonResponse({'error': '无效的文件'}, status=400)
    else:
        return JsonResponse({'error': '不支持的请求方法'}, status=405)

@login_required
def add_image_to_slide(request):
    """通过关键词搜索并添加图片到幻灯片"""
    if request.method == 'POST':
        keywords = request.POST.get('keywords', '')
        if not keywords:
            return JsonResponse({'error': '关键词不能为空'}, status=400)
            
        images = search_unsplash_images(keywords, per_page=3)
        if not images:
            return JsonResponse({'error': '未找到相关图片'}, status=404)
            
        # 处理图片，下载到本地
        local_images = []
        for image in images:
            local_url = download_remote_image(image['url'], image['alt'])
            local_image = {
                'url': local_url,
                'alt': image['alt'],
                'credit': image['credit']
            }
            local_images.append(local_image)
            
        return JsonResponse({'images': local_images})
    else:
        return JsonResponse({'error': '不支持的请求方法'}, status=405)



# slideapp/views.py
@login_required
def index(request):
    # 按照创建时间排序的幻灯片
    slides = Slide.objects.all().order_by('-created_at')  # 按照创建时间降序排序
    # 获取公开的幻灯片
    public_slides = Slide.objects.filter(public=True).order_by('-created_at')
    return render(request, 'index.html', {'slides': slides, 'public_slides': public_slides})

@login_required
def create_slide(request):
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 默认内容文件的路径
    default_content_path = os.path.join(current_dir, 'default_content.md')

    # 读取默认内容
    with open(default_content_path, 'r', encoding='utf-8') as f:
        default_content = f.read()

    # 创建新的幻灯片，并设置默认内容
    slide = Slide.objects.create(
        title='未命名',
        content=default_content,
        lock=True
    )

    return redirect('edit_slide', slide_id=slide.id)

@login_required
def edit_slide(request, slide_id):
    slide = Slide.objects.get(id=slide_id)
    return render(request, 'edit_slide.html', {'slide': slide})

@login_required
@require_http_methods(["GET", "POST"])
def delete_slide(request, slide_id):
    slide = get_object_or_404(Slide, id=slide_id)
    slide.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def toggle_lock(request, slide_id):
    slide = get_object_or_404(Slide, id=slide_id)
    # 切换锁定状态
    slide.lock = not slide.lock
    slide.save()
    return JsonResponse({'status': 'success', 'lock': slide.lock})

@login_required
@require_POST
def toggle_public(request, slide_id):
    slide = get_object_or_404(Slide, id=slide_id)
    # 切换公开状态
    slide.public = not slide.public
    slide.save()
    return JsonResponse({'success': True, 'public': slide.public})


def public_slides(request):
    slides = Slide.objects.filter(public=True).order_by('-created_at')
    return render(request, 'public_slides.html', {'slides': slides})


from django.shortcuts import render, get_object_or_404
from .models import Slide
import tempfile
import os
from .src.converter import converter
from django.conf import settings
import traceback


def public_edit_slide(request, slide_id):
    slide = get_object_or_404(Slide, id=slide_id, public=True)

    # 转换Markdown为HTML
    slide_html = convert_markdown_to_html(slide.content)

    return render(request, 'public_edit_slide.html', {'slide': slide, 'slide_html': slide_html})


def convert_markdown_to_html(markdown_content):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_md_file_path = os.path.join(temp_dir, 'temp.md')
            with open(temp_md_file_path, 'w', encoding='utf-8') as temp_md_file:
                temp_md_file.write(markdown_content)

            # 调用转换器
            converter(temp_md_file_path)

            output_html_path = os.path.join(temp_dir, 'dist', 'index.html')
            with open(output_html_path, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()

            html_content = html_content.replace('./static/', '/static/')
            html_content = html_content.replace('./img/', '/static/img/')

            return html_content
    except Exception as e:
        error_message = ''.join(traceback.format_exception_only(type(e), e))
        print(f"转换失败: {error_message}")
        return f"<p>转换失败: {error_message}</p>"

@login_required
def export_to_pptx(request, slide_id):
    """
    将幻灯片导出为PPTX格式
    """
    try:
        # 获取幻灯片
        slide = get_object_or_404(Slide, id=slide_id)
        
        # 检查访问权限：登录用户可以访问任何幻灯片，匿名用户只能访问公开幻灯片
        if request.user.is_anonymous and slide.lock:
            return JsonResponse({'error': '无权访问此幻灯片'}, status=403)
        
        # 转换为PPTX
        pptx_data = markdown_to_pptx(slide.content, title=slide.title)
        
        # 设置响应头，使浏览器下载文件
        response = HttpResponse(
            pptx_data.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        response['Content-Disposition'] = f'attachment; filename="{slide.title}.pptx"'
        
        return response
    except Exception as e:
        # 出错时返回JSON错误信息
        return JsonResponse({'error': f'导出幻灯片失败: {str(e)}'}, status=500)

@login_required
def import_document(request):
    """处理文档导入，提取内容并生成幻灯片"""
    if request.method == 'POST':
        # 获取表单数据
        title = request.POST.get('title', '未命名')
        slides_count = request.POST.get('slides_count', '5')
        layout = request.POST.get('layout', 'horizontal_vertical')
        auto_insert_images = request.POST.get('auto_insert_images', 'on') == 'on'
        
        # 获取上传文件
        uploaded_file = request.FILES.get('document_file')
        
        if not uploaded_file:
            return render(request, 'import_document.html', {
                'error': '请上传文件'
            })
        
        # 验证文件类型
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        allowed_extensions = ['.docx', '.doc', '.pdf', '.txt', '.md']
        
        if file_extension not in allowed_extensions:
            return render(request, 'import_document.html', {
                'error': f'不支持的文件类型，请上传以下格式: {", ".join(allowed_extensions)}'
            })
        
        # 输出处理开始日志
        print(f"开始处理文档: {uploaded_file.name}, 大小: {uploaded_file.size} 字节")
        
        try:
            # 处理上传的文档
            print(f"[进度] 1/5 - 开始提取文档内容...")
            markdown_content, error = process_uploaded_document(
                uploaded_file, 
                title, 
                int(slides_count),
                layout
            )
            
            if error or not markdown_content:
                return render(request, 'import_document.html', {
                    'error': error or '无法处理上传的文档，请尝试其他文件'
                })
            
            # 如果勾选了自动插入图片，添加图片
            if auto_insert_images and getattr(settings, 'AUTO_INSERT_IMAGES', True):
                print(f"[进度] 4/5 - 开始添加相关图片...")
                markdown_content = process_slides_with_images(markdown_content)
            
            print(f"[进度] 5/5 - 完成幻灯片生成，创建数据库记录...")
            # 创建新的幻灯片
            slide = Slide.objects.create(
                title=title,
                content=markdown_content,
                lock=True
            )
            
            print(f"文档处理完成: 已创建幻灯片 (ID: {slide.id})")
            
            # 重定向到编辑页面
            return redirect('edit_slide', slide_id=slide.id)
            
        except Exception as e:
            import traceback
            error_detail = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"导入文档出错详情: {error_detail}")
            
            return render(request, 'import_document.html', {
                'error': f'导入文档时出错: {str(e)}',
                'title': title
            })
    
    # GET请求时显示表单页面
    return render(request, 'import_document.html')