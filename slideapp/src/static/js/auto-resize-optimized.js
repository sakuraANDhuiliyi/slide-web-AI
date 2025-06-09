/**
 * 优化版自动调整幻灯片内容 - 保持布局美感的智能调整
 */

(function() {
    'use strict';
    
    // 优化的配置参数
    const CONFIG = {
        // 溢出阈值 - 只有超过这个阈值才开始调整
        overflowThreshold: 20, // px
        
        // 调整策略
        fontSizeStep: 1,        // 更小的字体调整步长
        minFontSize: 16,        // 提高最小字体大小保持可读性
        imageSizeStep: 5,       // 更小的图片调整步长  
        minImageSize: 60,       // 提高图片最小尺寸保持美观
        maxAdjustments: 5,      // 减少最大调整次数
        
        // 布局保护
        preserveRatio: true,    // 保持元素比例
        gentleMode: true,       // 温和模式
        
        // 检测延迟
        detectionDelay: 300
    };

    /**
     * 更精确的溢出检测 - 考虑阈值
     */
    function isSignificantlyOverflowing(element) {
        const heightOverflow = element.scrollHeight - element.clientHeight;
        const widthOverflow = element.scrollWidth - element.clientWidth;
        
        return heightOverflow > CONFIG.overflowThreshold || 
               widthOverflow > CONFIG.overflowThreshold;
    }

    /**
     * 检查元素是否为关键布局元素
     */
    function isLayoutCritical(element) {
        const criticalClasses = ['middle', 'center', 'author-block', 'title'];
        const classList = element.className.toLowerCase();
        
        return criticalClasses.some(cls => classList.includes(cls)) ||
               element.tagName.toLowerCase() === 'h1';
    }

    /**
     * 获取元素的原始样式值
     */
    function getOriginalStyles(element) {
        if (!element.dataset.originalStyles) {
            const computed = window.getComputedStyle(element);
            element.dataset.originalStyles = JSON.stringify({
                fontSize: computed.fontSize,
                width: computed.width,
                height: computed.height,
                lineHeight: computed.lineHeight
            });
        }
        return JSON.parse(element.dataset.originalStyles);
    }

    /**
     * 计算最优字体大小 - 基于内容长度和容器大小
     */
    function calculateOptimalFontSize(element, container) {
        const original = getOriginalStyles(element);
        const originalSize = parseFloat(original.fontSize);
        const contentLength = element.textContent.length;
        const containerArea = container.clientWidth * container.clientHeight;
        
        // 基于内容密度计算建议字体大小
        const density = contentLength / containerArea * 10000;
        let optimalSize = originalSize;
        
        if (density > 0.8) {
            optimalSize = Math.max(originalSize * 0.9, CONFIG.minFontSize);
        }
        
        return optimalSize;
    }

    /**
     * 温和的字体调整
     */
    function adjustTextSizeGently(element, container) {
        if (isLayoutCritical(element)) {
            return false; // 保护关键布局元素
        }
        
        const currentSize = parseFloat(window.getComputedStyle(element).fontSize);
        const optimalSize = calculateOptimalFontSize(element, container);
        
        if (currentSize > optimalSize && currentSize > CONFIG.minFontSize) {
            const newSize = Math.max(
                currentSize - CONFIG.fontSizeStep,
                optimalSize,
                CONFIG.minFontSize
            );
            
            element.style.fontSize = newSize + 'px';
            element.style.lineHeight = '1.3'; // 保持合适的行距
            
            return true;
        }
        
        return false;
    }

    /**
     * 智能图片调整 - 保持比例和美观
     */
    function adjustImageSizeIntelligently(img, container) {
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        const imgWidth = img.clientWidth;
        const imgHeight = img.clientHeight;
        
        // 检查图片是否真的需要调整
        const widthRatio = imgWidth / containerWidth;
        const heightRatio = imgHeight / containerHeight;
        
        if (widthRatio < 0.8 && heightRatio < 0.7) {
            return false; // 图片尺寸合理，不需要调整
        }
        
        // 温和调整
        let newWidth = Math.max(
            imgWidth * 0.95,
            containerWidth * CONFIG.minImageSize / 100
        );
        
        img.style.width = (newWidth / containerWidth * 100) + '%';
        img.style.height = 'auto';
        img.style.maxWidth = '90%'; // 确保不会太大
        
        return true;
    }

    /**
     * 检查调整效果是否改善了布局
     */
    function isAdjustmentEffective(slide, beforeState) {
        const afterOverflow = slide.scrollHeight - slide.clientHeight;
        const beforeOverflow = beforeState.scrollHeight - beforeState.clientHeight;
        
        // 如果调整后反而更糟，则回滚
        return afterOverflow < beforeOverflow - 10;
    }

    /**
     * 回滚不良的调整
     */
    function rollbackAdjustments(slide) {
        const elements = slide.querySelectorAll('*[style]');
        elements.forEach(el => {
            if (el.dataset.originalStyles) {
                const original = JSON.parse(el.dataset.originalStyles);
                if (original.fontSize) el.style.fontSize = original.fontSize;
                if (original.width && el.tagName.toLowerCase() === 'img') {
                    el.style.width = original.width;
                    el.style.height = original.height;
                }
            }
        });
    }

    /**
     * 智能调整单个幻灯片
     */
    function adjustSlideIntelligently(slide) {
        // 跳过已经处理过的幻灯片
        if (slide.dataset.smartAdjusted === 'true') {
            return;
        }
        
        // 记录调整前状态
        const beforeState = {
            scrollHeight: slide.scrollHeight,
            clientHeight: slide.clientHeight,
            scrollWidth: slide.scrollWidth,
            clientWidth: slide.clientWidth
        };
        
        // 只在真正需要时才调整
        if (!isSignificantlyOverflowing(slide)) {
            slide.dataset.smartAdjusted = 'true';
            return;
        }
        
        let adjustmentMade = false;
        let attempts = 0;
        
        while (isSignificantlyOverflowing(slide) && attempts < CONFIG.maxAdjustments) {
            attempts++;
            let stepAdjustment = false;
            
            // 策略1: 优先调整非关键图片
            const images = slide.querySelectorAll('img');
            for (const img of images) {
                if (!isLayoutCritical(img.parentElement)) {
                    if (adjustImageSizeIntelligently(img, slide)) {
                        stepAdjustment = true;
                        break; // 每次只调整一个元素
                    }
                }
            }
            
            // 策略2: 如果图片调整不够，温和调整文本
            if (!stepAdjustment && isSignificantlyOverflowing(slide)) {
                const textElements = slide.querySelectorAll('p, li, span');
                for (const el of textElements) {
                    if (adjustTextSizeGently(el, slide)) {
                        stepAdjustment = true;
                        break;
                    }
                }
            }
            
            // 策略3: 最后才考虑调整标题（除了h1）
            if (!stepAdjustment && isSignificantlyOverflowing(slide)) {
                const headings = slide.querySelectorAll('h2, h3, h4, h5, h6');
                for (const heading of headings) {
                    if (adjustTextSizeGently(heading, slide)) {
                        stepAdjustment = true;
                        break;
                    }
                }
            }
            
            if (stepAdjustment) {
                adjustmentMade = true;
                
                // 检查调整效果
                setTimeout(() => {
                    if (!isAdjustmentEffective(slide, beforeState)) {
                        console.log('调整效果不佳，回滚操作');
                        rollbackAdjustments(slide);
                    }
                }, 100);
            } else {
                break; // 无法进一步调整
            }
        }
        
        // 标记为已处理
        slide.dataset.smartAdjusted = 'true';
        
        if (adjustmentMade) {
            console.log(`幻灯片已智能调整，尝试次数: ${attempts}`);
        }
    }

    /**
     * 重置所有调整
     */
    function resetAllAdjustments() {
        const slides = document.querySelectorAll('.reveal .slides section');
        slides.forEach(slide => {
            slide.dataset.smartAdjusted = 'false';
            rollbackAdjustments(slide);
        });
    }

    /**
     * 批量处理所有幻灯片
     */
    function processAllSlides() {
        const slides = document.querySelectorAll('.reveal .slides section');
        
        slides.forEach((slide, index) => {
            // 只处理可见或即将可见的幻灯片
            const rect = slide.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                setTimeout(() => {
                    adjustSlideIntelligently(slide);
                }, index * 50); // 错开处理时间避免性能问题
            }
        });
    }

    /**
     * 设置智能调整系统
     */
    function setupIntelligentAdjustment() {
        if (typeof Reveal !== 'undefined') {
            // 幻灯片切换时的智能调整
            Reveal.on('slidechanged', (event) => {
                setTimeout(() => {
                    adjustSlideIntelligently(event.currentSlide);
                }, CONFIG.detectionDelay);
            });
            
            // 内容更新时的处理
            document.addEventListener('slideUpdated', () => {
                setTimeout(() => {
                    resetAllAdjustments();
                    processAllSlides();
                }, CONFIG.detectionDelay);
            });
        }
        
        // 窗口大小变化时的响应
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                resetAllAdjustments();
                processAllSlides();
            }, 500);
        });
    }

    /**
     * 初始化智能调整系统
     */
    function initIntelligentAdjustment() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(setupIntelligentAdjustment, 200);
            });
        } else {
            setTimeout(setupIntelligentAdjustment, 200);
        }
        
        // Reveal.js 准备就绪时
        if (typeof Reveal !== 'undefined') {
            if (Reveal.isReady && Reveal.isReady()) {
                setupIntelligentAdjustment();
                setTimeout(() => {
                    const currentSlide = Reveal.getCurrentSlide();
                    if (currentSlide) {
                        adjustSlideIntelligently(currentSlide);
                    }
                }, 500);
            } else {
                Reveal.on('ready', () => {
                    setupIntelligentAdjustment();
                    setTimeout(() => {
                        const currentSlide = Reveal.getCurrentSlide();
                        if (currentSlide) {
                            adjustSlideIntelligently(currentSlide);
                        }
                    }, 500);
                });
            }
        }
    }

    // 导出到全局
    window.AutoResize = {
        init: initIntelligentAdjustment,
        adjustSlide: adjustSlideIntelligently,
        adjustAll: processAllSlides,
        reset: resetAllAdjustments,
        config: CONFIG
    };

    // 自动初始化
    initIntelligentAdjustment();

})(); 