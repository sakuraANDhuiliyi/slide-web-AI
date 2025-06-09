/**
 * 自动调整幻灯片内容大小以防止溢出
 */

// 配置参数
const AUTO_RESIZE_CONFIG = {
    // 字体大小调整步长 (px)
    fontSizeStep: 2,
    // 最小字体大小 (px)
    minFontSize: 12,
    // 图片尺寸调整步长 (%)
    imageSizeStep: 5,
    // 图片最小尺寸 (%)
    minImageSize: 30,
    // 最大调整次数
    maxAdjustments: 10,
    // 调整延迟 (ms)
    adjustDelay: 100
};

/**
 * 检测元素是否溢出其容器
 * @param {HTMLElement} element - 要检测的元素
 * @return {boolean} - 是否溢出
 */
function isOverflowing(element) {
    return element.scrollHeight > element.clientHeight || 
           element.scrollWidth > element.clientWidth;
}

/**
 * 获取元素当前字体大小 (px)
 * @param {HTMLElement} element - 目标元素
 * @return {number} - 字体大小
 */
function getCurrentFontSize(element) {
    return parseFloat(window.getComputedStyle(element).fontSize);
}

/**
 * 设置元素字体大小
 * @param {HTMLElement} element - 目标元素
 * @param {number} size - 新的字体大小 (px)
 */
function setFontSize(element, size) {
    element.style.fontSize = size + 'px';
}

/**
 * 获取图片当前宽度百分比
 * @param {HTMLElement} img - 图片元素
 * @return {number} - 宽度百分比
 */
function getCurrentImageWidth(img) {
    const style = window.getComputedStyle(img);
    if (style.width && style.width.includes('%')) {
        return parseFloat(style.width);
    }
    // 如果没有设置百分比，计算相对于父容器的百分比
    const parentWidth = img.parentElement.clientWidth;
    return (img.clientWidth / parentWidth) * 100;
}

/**
 * 设置图片宽度百分比
 * @param {HTMLElement} img - 图片元素
 * @param {number} widthPercent - 宽度百分比
 */
function setImageWidth(img, widthPercent) {
    img.style.width = widthPercent + '%';
    img.style.height = 'auto'; // 保持比例
}

/**
 * 调整文本元素的字体大小
 * @param {HTMLElement} element - 要调整的元素
 * @param {HTMLElement} container - 容器元素
 * @return {Promise<boolean>} - 是否成功调整
 */
async function adjustTextSize(element, container) {
    let adjustments = 0;
    let currentFontSize = getCurrentFontSize(element);
    
    while (isOverflowing(container) && 
           currentFontSize > AUTO_RESIZE_CONFIG.minFontSize && 
           adjustments < AUTO_RESIZE_CONFIG.maxAdjustments) {
        
        currentFontSize -= AUTO_RESIZE_CONFIG.fontSizeStep;
        setFontSize(element, currentFontSize);
        adjustments++;
        
        // 给浏览器时间重新渲染
        if (adjustments % 3 === 0) {
            await new Promise(resolve => setTimeout(resolve, AUTO_RESIZE_CONFIG.adjustDelay));
        }
    }
    
    return !isOverflowing(container);
}

/**
 * 调整图片大小
 * @param {HTMLElement} img - 图片元素
 * @param {HTMLElement} container - 容器元素
 * @return {Promise<boolean>} - 是否成功调整
 */
async function adjustImageSize(img, container) {
    let adjustments = 0;
    let currentWidth = getCurrentImageWidth(img);
    
    while (isOverflowing(container) && 
           currentWidth > AUTO_RESIZE_CONFIG.minImageSize && 
           adjustments < AUTO_RESIZE_CONFIG.maxAdjustments) {
        
        currentWidth -= AUTO_RESIZE_CONFIG.imageSizeStep;
        setImageWidth(img, currentWidth);
        adjustments++;
        
        // 给浏览器时间重新渲染
        if (adjustments % 2 === 0) {
            await new Promise(resolve => setTimeout(resolve, AUTO_RESIZE_CONFIG.adjustDelay));
        }
    }
    
    return !isOverflowing(container);
}

/**
 * 调整单个幻灯片的内容
 * @param {HTMLElement} slide - 幻灯片元素
 */
async function adjustSlideContent(slide) {
    // 跳过已经处理过的幻灯片
    if (slide.dataset.autoResized === 'true') {
        return;
    }
    
    let maxAttempts = 5;
    let attempt = 0;
    
    while (isOverflowing(slide) && attempt < maxAttempts) {
        attempt++;
        let adjusted = false;
        
        // 1. 调整图片大小
        const images = slide.querySelectorAll('img');
        for (const img of images) {
            if (isOverflowing(slide)) {
                if (await adjustImageSize(img, slide)) {
                    adjusted = true;
                    break;
                }
            }
        }
        
        // 2. 如果图片调整后仍然溢出，调整文本大小
        if (isOverflowing(slide)) {
            // 调整段落文本
            const paragraphs = slide.querySelectorAll('p, li');
            for (const p of paragraphs) {
                if (isOverflowing(slide)) {
                    if (await adjustTextSize(p, slide)) {
                        adjusted = true;
                        break;
                    }
                }
            }
            
            // 调整标题
            if (isOverflowing(slide)) {
                const headings = slide.querySelectorAll('h1, h2, h3, h4, h5, h6');
                for (const heading of headings) {
                    if (isOverflowing(slide)) {
                        if (await adjustTextSize(heading, slide)) {
                            adjusted = true;
                            break;
                        }
                    }
                }
            }
            
            // 调整代码块
            if (isOverflowing(slide)) {
                const codeBlocks = slide.querySelectorAll('pre, code');
                for (const code of codeBlocks) {
                    if (isOverflowing(slide)) {
                        if (await adjustTextSize(code, slide)) {
                            adjusted = true;
                            break;
                        }
                    }
                }
            }
        }
        
        // 如果没有进行任何调整，跳出循环避免无限循环
        if (!adjusted) {
            break;
        }
        
        // 等待重新渲染
        await new Promise(resolve => setTimeout(resolve, AUTO_RESIZE_CONFIG.adjustDelay));
    }
    
    // 标记为已处理
    slide.dataset.autoResized = 'true';
}

/**
 * 调整所有可见幻灯片的内容
 */
async function adjustAllSlides() {
    const slides = document.querySelectorAll('.reveal .slides section');
    
    for (const slide of slides) {
        // 只处理当前可见的幻灯片
        const rect = slide.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
            await adjustSlideContent(slide);
        }
    }
}

/**
 * 重置幻灯片的调整状态
 */
function resetSlideAdjustments() {
    const slides = document.querySelectorAll('.reveal .slides section');
    slides.forEach(slide => {
        slide.dataset.autoResized = 'false';
    });
}

/**
 * 初始化自动调整功能
 */
function initAutoResize() {
    // 确保在Reveal.js初始化完成后运行
    if (typeof Reveal !== 'undefined' && Reveal.isReady()) {
        setupAutoResize();
    } else {
        // 等待Reveal.js加载完成
        document.addEventListener('DOMContentLoaded', () => {
            if (typeof Reveal !== 'undefined') {
                Reveal.on('ready', setupAutoResize);
            }
        });
    }
}

/**
 * 设置自动调整事件监听器
 */
function setupAutoResize() {
    // 在幻灯片切换时调整新幻灯片
    Reveal.on('slidechanged', async (event) => {
        await adjustSlideContent(event.currentSlide);
    });
    
    // 在幻灯片更新时重新调整
    document.addEventListener('slideUpdated', async () => {
        resetSlideAdjustments();
        await adjustAllSlides();
    });
    
    // 窗口大小改变时重新调整
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(async () => {
            resetSlideAdjustments();
            await adjustAllSlides();
        }, 500);
    });
    
    // 初始调整当前幻灯片
    setTimeout(async () => {
        const currentSlide = Reveal.getCurrentSlide();
        if (currentSlide) {
            await adjustSlideContent(currentSlide);
        }
    }, 500);
}

// 导出函数供外部使用
window.AutoResize = {
    init: initAutoResize,
    adjustSlide: adjustSlideContent,
    adjustAll: adjustAllSlides,
    reset: resetSlideAdjustments
};

// 自动初始化
initAutoResize(); 