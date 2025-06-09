# 图片调节功能测试

这个页面专门用来测试手动调节功能中的图片样式更新。

---

# 测试图片

## 标准Markdown图片

![测试图片1](https://via.placeholder.com/400x300/FF5722/FFFFFF?text=图片1)

这是一张使用标准Markdown语法的图片，应该可以调节大小和位置。

----

## 另一张图片

![示例图片](https://via.placeholder.com/300x200/2196F3/FFFFFF?text=示例图片)

这是第二张图片，用来测试多图片环境下的选择和调节。

---

# HTML格式图片

## 已有样式的图片

<img alt="HTML图片" src="https://via.placeholder.com/350x250/4CAF50/FFFFFF?text=HTML图片" style="width: 70%; margin: 10px auto;">

这是一张已经有样式的HTML图片，测试样式更新功能。

----

## 复杂图片

<img alt="复杂图片" src="https://via.placeholder.com/500x300/9C27B0/FFFFFF?text=复杂图片" style="width: 80%; height: auto; border-radius: 10px;">

这张图片有多个样式属性，测试样式替换功能。

---

# 测试说明

## 测试步骤

1. 点击"手动调节"按钮
2. 选择上面的任意一张图片
3. 使用滑块调节图片大小
4. 点击"预览代码"查看生成的HTML
5. 点击"应用"将样式写入Markdown
6. 检查左侧编辑器是否正确更新

## 预期结果

- ✅ 图片选择正确高亮
- ✅ 滑块反映当前图片大小
- ✅ 实时预览显示调节效果
- ✅ 代码预览显示正确HTML
- ✅ 应用后左侧Markdown正确更新

## 常见问题

如果遇到问题，请：

1. 打开浏览器开发者工具查看控制台日志
2. 点击"显示详情"查看选中元素信息
3. 检查图片的alt和src属性是否匹配

---

# 更多测试案例

## 相对路径图片

![本地图片](/static/img/favicon.png)

## 无alt属性图片

<img src="https://via.placeholder.com/200x150/607D8B/FFFFFF?text=无Alt">

## 特殊字符图片

![特殊图片！@#$%](https://via.placeholder.com/250x200/FF9800/FFFFFF?text=特殊字符)

---

# 调试信息

测试时请打开浏览器控制台，查看以下调试信息：

- 图片选择日志
- 样式分析结果
- Markdown更新过程
- 错误信息（如果有）

**开始测试！** 🧪 