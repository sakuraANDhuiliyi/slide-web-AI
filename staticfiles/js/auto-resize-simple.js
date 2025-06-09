/**
 * 简化版自动调整幻灯片内容大小以防止溢出
 */

(function() {
    'use strict';
    
    // 配置参数
    const CONFIG = {
        fontSizeStep: 2,
        minFontSize: 14,
        imageSizeStep: 10,
        minImageSize: 40,
        maxAdjustments: 8
    };

    /**
     * 检测元素是否溢出其容器
     */
    function isOverflowing(element) {
        return element.scrollHeight > element.clientHeight || 
               element.scrollWidth > element.clientWidth;
    }

    /**
     * 获取元素当前字体大小 (px)
     */
    function getCurrentFontSize(element) {
        return parseFloat(window.getComputedStyle(element).fontSize);
    }

    /**
     * 设置元素字体大小
     */
    function setFontSize(element, size) {
        element.style.fontSize = size + 'px';
        element.style.lineHeight = '1.2';
    }

    /**
     * 获取图片当前宽度百分比
     */
    function getCurrentImageWidth(img) {
        const style = window.getComputedStyle(img);
        if (style.width && style.width.includes('%')) {
            return parseFloat(style.width);
        }
        const parentWidth = img.parentElement.clientWidth;
        return parentWidth > 0 ? (img.clientWidth / parentWidth) * 100 : 100;
    }

    /**
     * 设置图片宽度百分比
     */
    function setImageWidth(img, widthPercent) {
        img.style.width = widthPercent + '%';
        img.style.height = 'auto';
        img.style.maxWidth = widthPercent + '%';
    }

    /**
     * 调整文本元素的字体大小
     */
    function adjustTextSize(element, container) {
        let adjustments = 0;
        let currentFontSize = getCurrentFontSize(element);
        
        while (isOverflowing(container) && 
               currentFontSize > CONFIG.minFontSize && 
               adjustments < CONFIG.maxAdjustments) {
            
            currentFontSize -= CONFIG.fontSizeStep;
            setFontSize(element, currentFontSize);
            adjustments++;
        }
        
        return !isOverflowing(container);
    }

    /**
     * 调整图片大小
     */
    function adjustImageSize(img, container) {
        let adjustments = 0;
        let currentWidth = getCurrentImageWidth(img);
        
        while (isOverflowing(container) && 
               currentWidth > CONFIG.minImageSize && 
               adjustments < CONFIG.maxAdjustments) {
            
            currentWidth -= CONFIG.imageSizeStep;
            setImageWidth(img, currentWidth);
            adjustments++;
        }
        
        return !isOverflowing(container);
    }

    /**
     * 调整单个幻灯片的内容
     */
    function adjustSlideContent(slide) {
        // 跳过已经处理过的幻灯片
        if (slide.dataset.autoResized === 'true') {
            return;
        }
        
        let maxAttempts = 3;
        let attempt = 0;
        
        while (isOverflowing(slide) && attempt < maxAttempts) {
            attempt++;
            let adjusted = false;
            
            // 1. 首先调整图片大小
            const images = slide.querySelectorAll('img');
            for (let i = 0; i < images.length && isOverflowing(slide); i++) {
                if (adjustImageSize(images[i], slide)) {
                    adjusted = true;
                }
            }
            
            // 2. 如果仍然溢出，调整文本大小
            if (isOverflowing(slide)) {
                // 调整段落和列表项
                const textElements = slide.querySelectorAll('p, li');
                for (let i = 0; i < textElements.length && isOverflowing(slide); i++) {
                    if (adjustTextSize(textElements[i], slide)) {
                        adjusted = true;
                    }
                }
                
                // 调整标题
                if (isOverflowing(slide)) {
                    const headings = slide.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    for (let i = 0; i < headings.length && isOverflowing(slide); i++) {
                        if (adjustTextSize(headings[i], slide)) {
                            adjusted = true;
                        }
                    }
                }
                
                // 调整代码块
                if (isOverflowing(slide)) {
                    const codeBlocks = slide.querySelectorAll('pre, code');
                    for (let i = 0; i < codeBlocks.length && isOverflowing(slide); i++) {
                        if (adjustTextSize(codeBlocks[i], slide)) {
                            adjusted = true;
                        }
                    }
                }
            }
            
            // 如果没有进行任何调整，跳出循环
            if (!adjusted) {
                break;
            }
        }
        
        // 标记为已处理
        slide.dataset.autoResized = 'true';
    }

    /**
     * 调整所有幻灯片的内容
     */
    function adjustAllSlides() {
        const slides = document.querySelectorAll('.reveal .slides section');
        
        slides.forEach(function(slide) {
            // 只处理可见的幻灯片
            const rect = slide.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                adjustSlideContent(slide);
            }
        });
    }

    /**
     * 重置幻灯片的调整状态
     */
    function resetSlideAdjustments() {
        const slides = document.querySelectorAll('.reveal .slides section');
        slides.forEach(function(slide) {
            slide.dataset.autoResized = 'false';
            // 移除内联样式，恢复原始状态
            const elements = slide.querySelectorAll('*[style]');
            elements.forEach(function(el) {
                if (el.style.fontSize) el.style.fontSize = '';
                if (el.style.width && el.tagName.toLowerCase() === 'img') {
                    el.style.width = '';
                    el.style.maxWidth = '';
                }
            });
        });
    }

    /**
     * 设置自动调整事件监听器
     */
    function setupAutoResize() {
        // 在幻灯片切换时调整新幻灯片
        if (typeof Reveal !== 'undefined') {
            Reveal.on('slidechanged', function(event) {
                setTimeout(function() {
                    adjustSlideContent(event.currentSlide);
                }, 200);
            });
        }
        
        // 在幻灯片更新时重新调整
        document.addEventListener('slideUpdated', function() {
            setTimeout(function() {
                resetSlideAdjustments();
                adjustAllSlides();
            }, 300);
        });
        
        // 窗口大小改变时重新调整
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                resetSlideAdjustments();
                adjustAllSlides();
            }, 500);
        });
    }

    /**
     * 初始化自动调整功能
     */
    function initAutoResize() {
        // 确保在DOM加载完成后运行
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(setupAutoResize, 100);
            });
        } else {
            setTimeout(setupAutoResize, 100);
        }
        
        // 如果Reveal已经准备好，立即设置
        if (typeof Reveal !== 'undefined' && Reveal.isReady && Reveal.isReady()) {
            setupAutoResize();
            setTimeout(function() {
                const currentSlide = Reveal.getCurrentSlide();
                if (currentSlide) {
                    adjustSlideContent(currentSlide);
                }
            }, 500);
        } else if (typeof Reveal !== 'undefined') {
            Reveal.on('ready', function() {
                setupAutoResize();
                setTimeout(function() {
                    const currentSlide = Reveal.getCurrentSlide();
                    if (currentSlide) {
                        adjustSlideContent(currentSlide);
                    }
                }, 500);
            });
        }
    }

    // 导出到全局对象
    window.AutoResize = {
        init: initAutoResize,
        adjustSlide: adjustSlideContent,
        adjustAll: adjustAllSlides,
        reset: resetSlideAdjustments
    };

    // 自动初始化
    initAutoResize();

})(); 