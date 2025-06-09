# jyySlideWeb 项目设计文档

## 📋 项目概述

### 项目简介
jyySlideWeb 是一个基于 Django 的在线幻灯片编辑器，支持 Markdown 语法编写幻灯片内容，实时预览效果，并提供智能布局调整、AI 图片搜索、PPTX 导出等高级功能。

### 核心特性
- 🎯 **实时编辑预览** - 左侧 Markdown 编辑，右侧实时幻灯片预览
- 🤖 **AI 智能功能** - 自动生成幻灯片、智能图片搜索、内容优化
- 🎨 **智能布局调整** - 自动检测内容溢出并调整字体、图片大小
- 🎛️ **手动精确调节** - 可视化调节文字和图片的大小、位置
- 📤 **多格式导出** - 支持导出为 PPTX 格式
- 🔄 **实时协作** - 基于 WebSocket 的实时同步
- 🌐 **公开分享** - 支持幻灯片公开展示

### 技术栈
- **后端**: Django 4.x + Django Channels
- **前端**: HTML5 + CSS3 + JavaScript + Reveal.js
- **数据库**: SQLite (可扩展为 PostgreSQL)
- **实时通信**: WebSocket
- **AI 服务**: Google Gemini API
- **图片服务**: Unsplash API

---

## 🏗️ 系统架构

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面层 (Frontend)                      │
├─────────────────────────────────────────────────────────────┤
│  编辑器界面  │  预览界面  │  调节面板  │  工具栏  │  模态框   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    应用服务层 (Backend)                       │
├─────────────────────────────────────────────────────────────┤
│  Django Views  │  WebSocket  │  AI Service  │  Export API   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Services)                      │
├─────────────────────────────────────────────────────────────┤
│  Markdown转换  │  布局调整  │  图片处理  │  PPTX生成        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据存储层 (Storage)                       │
├─────────────────────────────────────────────────────────────┤
│    SQLite DB    │   Media Files   │   Static Files          │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. 前端组件
- **编辑器 (Editor)**: 基于 textarea 的 Markdown 编辑器
- **预览器 (Preview)**: 基于 Reveal.js 的幻灯片预览
- **调节面板 (Adjustment Panel)**: 可视化样式调节工具
- **工具栏 (Toolbar)**: 功能按钮集合
- **模态框 (Modals)**: 图片搜索、AI 生成等弹窗

#### 2. 后端组件
- **Django Views**: HTTP 请求处理
- **WebSocket Consumers**: 实时通信处理
- **AI Services**: 智能功能服务
- **Export Services**: 文件导出服务
- **Utils**: 工具函数库

---

## 📊 数据模型设计

### 数据库表结构

#### Slide 模型
```python
class Slide(models.Model):
    title = models.CharField(max_length=200, default='未命名')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    lock = models.BooleanField(default=True)      # 编辑锁定状态
    public = models.BooleanField(default=False)   # 公开访问状态
```

#### 字段说明
- `title`: 幻灯片标题
- `content`: Markdown 格式的幻灯片内容
- `created_at`: 创建时间
- `updated_at`: 最后更新时间
- `lock`: 是否锁定编辑 (True=锁定, False=可编辑)
- `public`: 是否公开访问 (True=公开, False=私有)

### 数据流图
```
用户输入 → Markdown内容 → 实时转换 → HTML预览 → 样式调整 → 保存到数据库
    ↓
AI生成 → 内容优化 → 图片搜索 → 自动插入 → 用户确认 → 保存到数据库
    ↓
导出请求 → 读取数据库 → PPTX转换 → 文件下载
```

---

## 🔧 核心功能模块

### 1. 实时编辑系统

#### WebSocket 通信架构
```python
# consumers.py
class SlideConsumer(AsyncWebsocketConsumer):
    async def connect()          # 建立连接
    async def disconnect()       # 断开连接
    async def receive()          # 接收消息
    async def send_preview()     # 发送预览
```

#### 消息类型
- `load`: 加载幻灯片内容
- `preview`: 预览更新请求
- `save`: 保存内容
- `error`: 错误信息

#### 实时同步流程
```
1. 用户输入 Markdown
2. 触发 input 事件
3. 通过 WebSocket 发送到后端
4. 后端转换为 HTML
5. 返回 HTML 到前端
6. 更新预览区域
7. 自动保存到数据库
```

### 2. Markdown 转换系统

#### 转换流程
```python
def convert_markdown_to_html(markdown_content):
    # 1. 创建临时文件
    # 2. 调用转换器
    # 3. 生成 HTML
    # 4. 处理静态资源路径
    # 5. 返回完整 HTML
```

#### 支持的语法
- **基础语法**: 标题、段落、列表、链接、图片
- **扩展语法**: 代码块、数学公式、表格
- **幻灯片语法**: 
  - `---`: 水平幻灯片分隔
  - `----`: 垂直幻灯片分隔
  - `++++`: 渐变幻灯片分隔

### 3. 智能布局调整系统

#### 自动调整算法
```javascript
// auto-resize-optimized.js
function adjustSlideIntelligently(slide) {
    // 1. 检测内容溢出
    // 2. 分析元素类型
    // 3. 应用调整策略
    // 4. 验证调整效果
    // 5. 回滚不良调整
}
```

#### 调整策略
1. **溢出检测**: 只在超过阈值时调整
2. **元素保护**: 保护关键布局元素
3. **优先级**: 图片 → 普通文本 → 次级标题
4. **温和调整**: 小步长、渐进式调整
5. **效果验证**: 检查调整是否改善布局

### 4. 手动调节系统

#### 调节面板组件
```html
<!-- 元素选择 -->
<div class="control-group">
    <div class="control-buttons">
        <div class="control-btn" onclick="selectElementType('text')">文字</div>
        <div class="control-btn" onclick="selectElementType('image')">图片</div>
        <div class="control-btn" onclick="selectElementType('heading')">标题</div>
    </div>
</div>

<!-- 字体大小调节 -->
<div class="control-group" id="fontSizeControl">
    <input type="range" class="control-slider" id="fontSizeSlider">
    <span class="control-value" id="fontSizeValue">16px</span>
</div>

<!-- 图片大小调节 -->
<div class="control-group" id="imageSizeControl">
    <input type="range" class="control-slider" id="imageWidthSlider">
    <input type="range" class="control-slider" id="imageHeightSlider">
</div>
```

#### 样式保存机制
```javascript
function applyAdjustments() {
    // 1. 分析选中元素
    // 2. 生成样式字符串
    // 3. 更新 Markdown 文本
    // 4. 重新渲染预览
    // 5. 保存到数据库
}
```

### 5. AI 智能功能

#### AI 生成幻灯片
```python
def generate_slide_with_ai(topic, style, layout):
    # 1. 构建提示词
    # 2. 调用 Gemini API
    # 3. 解析 AI 响应
    # 4. 格式化为 Markdown
    # 5. 可选添加图片
```

#### 图片智能搜索
```python
def search_unsplash_images(keywords):
    # 1. 关键词提取
    # 2. 调用 Unsplash API
    # 3. 图片筛选和排序
    # 4. 返回图片信息
```

### 6. 导出系统

#### PPTX 导出流程
```python
def markdown_to_pptx(markdown_content, title):
    # 1. 解析幻灯片结构
    # 2. 创建 PowerPoint 对象
    # 3. 逐页添加内容
    # 4. 处理图片和样式
    # 5. 生成二进制文件
```

---

## 🎨 用户界面设计

### 布局结构
```
┌─────────────────────────────────────────────────────────────┐
│                        工具栏                                │
├─────────────────────┬───────────────────────────────────────┤
│                     │                                       │
│    Markdown编辑器    │         幻灯片预览区                   │
│                     │                                       │
│                     │                                       │
│                     │                                       │
│                     │                                       │
│                     │                                       │
└─────────────────────┴───────────────────────────────────────┘
```

### 响应式设计
- **桌面端**: 左右分栏布局 (50%-50%)
- **平板端**: 上下布局或可切换视图
- **移动端**: 单视图切换模式

### 主题样式
- **默认主题**: 简洁白色主题
- **暗色主题**: 护眼暗色模式
- **自定义主题**: 支持用户自定义配色

---

## 🔌 API 接口设计

### HTTP 接口

#### 幻灯片管理
```python
# 获取幻灯片列表
GET /api/slides/
Response: [{"id": 1, "title": "标题", "created_at": "2024-01-01"}]

# 创建幻灯片
POST /api/slides/
Body: {"title": "新幻灯片"}
Response: {"id": 2, "title": "新幻灯片"}

# 获取幻灯片详情
GET /api/slides/{id}/
Response: {"id": 1, "title": "标题", "content": "# 内容"}

# 更新幻灯片
PUT /api/slides/{id}/
Body: {"title": "更新标题", "content": "# 更新内容"}

# 删除幻灯片
DELETE /api/slides/{id}/
```

#### AI 功能
```python
# AI 生成幻灯片
POST /api/ai/generate/
Body: {
    "topic": "主题",
    "style": "academic",
    "layout": "horizontal_vertical"
}
Response: {"content": "# AI生成的内容"}

# 图片搜索
POST /api/images/search/
Body: {"keywords": "关键词"}
Response: {
    "images": [
        {
            "url": "图片URL",
            "alt": "描述",
            "credit": {"name": "作者", "link": "链接"}
        }
    ]
}
```

#### 导出功能
```python
# 导出 PPTX
GET /api/slides/{id}/export/pptx/
Response: Binary file download
```

### WebSocket 接口

#### 消息格式
```json
{
    "action": "preview",
    "markdown": "# 幻灯片内容"
}
```

#### 响应格式
```json
{
    "action": "preview",
    "html": "<html>...</html>"
}
```

---

## 🔒 安全设计

### 数据安全
- **输入验证**: 严格验证用户输入
- **XSS 防护**: HTML 内容转义
- **CSRF 保护**: Django CSRF 中间件
- **SQL 注入防护**: Django ORM 参数化查询

### 访问控制
- **会话管理**: Django 会话框架
- **权限控制**: 基于幻灯片的访问权限
- **公开访问**: 支持无需登录的公开幻灯片

### API 安全
- **速率限制**: 防止 API 滥用
- **输入大小限制**: 防止大文件攻击
- **错误处理**: 不泄露敏感信息

---

## 📈 性能优化

### 前端优化
- **资源压缩**: CSS/JS 文件压缩
- **缓存策略**: 静态资源缓存
- **懒加载**: 图片和组件懒加载
- **防抖处理**: 输入事件防抖

### 后端优化
- **数据库优化**: 索引优化、查询优化
- **缓存机制**: Redis 缓存热点数据
- **异步处理**: WebSocket 异步通信
- **文件处理**: 临时文件清理

### 网络优化
- **CDN 加速**: 静态资源 CDN 分发
- **Gzip 压缩**: HTTP 响应压缩
- **Keep-Alive**: HTTP 连接复用

---

## 🧪 测试策略

### 单元测试
```python
# 测试模型
class SlideModelTest(TestCase):
    def test_slide_creation(self):
        slide = Slide.objects.create(title="测试")
        self.assertEqual(slide.title, "测试")

# 测试视图
class SlideViewTest(TestCase):
    def test_slide_list_view(self):
        response = self.client.get('/slides/')
        self.assertEqual(response.status_code, 200)
```

### 集成测试
- **WebSocket 通信测试**
- **Markdown 转换测试**
- **AI 功能集成测试**
- **导出功能测试**

### 前端测试
- **JavaScript 单元测试**
- **UI 交互测试**
- **跨浏览器兼容性测试**

### 性能测试
- **负载测试**: 并发用户测试
- **压力测试**: 极限负载测试
- **内存泄漏测试**: 长时间运行测试

---

## 🚀 部署架构

### 开发环境
```bash
# 本地开发
python manage.py runserver
# 或使用 Daphne (支持 WebSocket)
daphne jyy_slide_web.asgi:application
```

### 生产环境
```
┌─────────────────────────────────────────────────────────────┐
│                      负载均衡器 (Nginx)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    应用服务器 (Daphne)                        │
├─────────────────────────────────────────────────────────────┤
│  Django App 1  │  Django App 2  │  Django App 3            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据库 (PostgreSQL)                     │
└─────────────────────────────────────────────────────────────┘
```

### Docker 部署
```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["daphne", "jyy_slide_web.asgi:application"]
```

### 环境配置
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

---

## 📋 开发规范

### 代码规范
- **Python**: PEP 8 编码规范
- **JavaScript**: ES6+ 标准
- **HTML/CSS**: W3C 标准
- **注释**: 中英文混合，关键逻辑必须注释

### Git 工作流
```bash
# 功能分支
git checkout -b feature/new-feature
git commit -m "feat: 添加新功能"
git push origin feature/new-feature

# 合并请求
# Code Review → 测试通过 → 合并到主分支
```

### 版本管理
- **语义化版本**: MAJOR.MINOR.PATCH
- **变更日志**: CHANGELOG.md 记录
- **发布标签**: Git 标签管理版本

---

## 🔮 未来规划

### 短期目标 (1-3个月)
- [ ] 用户认证系统
- [ ] 多主题支持
- [ ] 移动端适配优化
- [ ] 性能监控和优化

### 中期目标 (3-6个月)
- [ ] 多人协作编辑
- [ ] 版本历史管理
- [ ] 插件系统
- [ ] 云存储集成

### 长期目标 (6-12个月)
- [ ] 微服务架构重构
- [ ] 国际化支持
- [ ] 企业级功能
- [ ] 开放 API 平台

---

## 📚 技术文档

### 开发文档
- [安装指南](./docs/installation.md)
- [开发指南](./docs/development.md)
- [API 文档](./docs/api.md)
- [部署指南](./docs/deployment.md)

### 用户文档
- [用户手册](./docs/user-guide.md)
- [功能介绍](./docs/features.md)
- [常见问题](./docs/faq.md)
- [更新日志](./CHANGELOG.md)

---

## 🤝 贡献指南

### 如何贡献
1. Fork 项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建 Pull Request
5. 代码审查和合并

### 问题反馈
- [GitHub Issues](https://github.com/xieyumc/jyySlideWeb/issues)
- [讨论区](https://github.com/xieyumc/jyySlideWeb/discussions)

---

## 📄 许可证

本项目采用 [MIT License](./LICENSE.txt) 开源许可证。

---

## 👥 团队信息

### 核心开发者
- **项目负责人**: [xieyumc](https://github.com/xieyumc)
- **技术架构**: Django + WebSocket + AI
- **联系方式**: GitHub Issues

### 致谢
- [Reveal.js](https://revealjs.com/) - 幻灯片展示框架
- [Django](https://www.djangoproject.com/) - Web 开发框架
- [Unsplash](https://unsplash.com/) - 图片资源
- [Google Gemini](https://ai.google.dev/) - AI 服务

---

*最后更新时间: 2024年12月* 