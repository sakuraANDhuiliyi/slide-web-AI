网页实时Markdown转换为Slide幻灯片，包含AI生成PPT，导入导出文件，支持自动/手动调整布局，支持AI自动寻找并插入合适的图片

原项目地址：https://github.com/xieyumc/jyySlideWeb

安装运行参考https://github.com/xieyumc/jyySlideWeb

记得申请Gemini的api和unsplash的api填写在setting.py

本项目对比原项目新增加了：

## 智能布局调整系统

### 自动调整算法
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

### 调整策略
1. **溢出检测**: 只在超过阈值时调整
2. **元素保护**: 保护关键布局元素
3. **优先级**: 图片 → 普通文本 → 次级标题
4. **温和调整**: 小步长、渐进式调整
5. **效果验证**: 检查调整是否改善布局

## 手动调节系统

### 调节面板组件
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

### 样式保存机制
```javascript
function applyAdjustments() {
    // 1. 分析选中元素
    // 2. 生成样式字符串
    // 3. 更新 Markdown 文本
    // 4. 重新渲染预览
    // 5. 保存到数据库
}
```

## AI 智能功能

### AI 生成幻灯片
```python
def generate_slide_with_ai(topic, style, layout):
    # 1. 构建提示词
    # 2. 调用 Gemini API
    # 3. 解析 AI 响应
    # 4. 格式化为 Markdown
    # 5. 可选添加图片
```

### 图片智能搜索
```python
def search_unsplash_images(keywords):
    # 1. 关键词提取
    # 2. 调用 Unsplash API
    # 3. 图片筛选和排序
    # 4. 返回图片信息
```

## 📤 导入导出功能

### 文档导入

#### **📥 多格式文档导入**
- **功能描述**: 导入现有文档生成幻灯片
- **访问路径**: `/import_document/`
- **支持格式**:
  - **Word文档** (.docx)
    - 段落结构解析
    - 标题层级识别
    - 图片自动提取
    - 表格转换支持
  
  - **PDF文档** (.pdf)
    - 文本内容提取
    - 页面结构分析
    - 图片提取处理
    - 格式保持优化
  
  - **Markdown文件** (.md)
    - 直接导入支持
    - 语法完全兼容
    - 图片路径处理
    - 元数据解析

#### **🔄 导入处理流程**
- **文档解析**: 智能识别文档结构
- **内容转换**: 自动转换为Markdown格式
- **图片处理**: 提取并保存图片资源
- **结构优化**: 自动生成幻灯片分页

## 导出系统

### PPTX 导出流程
```python
def markdown_to_pptx(markdown_content, title):
    # 1. 解析幻灯片结构
    # 2. 创建 PowerPoint 对象
    # 3. 逐页添加内容
    # 4. 处理图片和样式
    # 5. 生成二进制文件
```

---
