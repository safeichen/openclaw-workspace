/**
 * 机票预订页面优化方案
 * 解决用户忘记勾选协议的问题
 */

class FlightBookingOptimizer {
    constructor(options = {}) {
        // 默认配置
        this.config = {
            agreementSelector: '#agreement-checkbox',
            agreementSectionSelector: '.agreement-section',
            submitSelector: '#submit-btn',
            toastContainer: 'body',
            autoCheck: true, // 默认勾选
            highlightDuration: 3000, // 高亮持续时间
            scrollOffset: 100, // 滚动偏移量
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.agreementCheckbox = document.querySelector(this.config.agreementSelector);
        this.agreementSection = document.querySelector(this.config.agreementSectionSelector);
        this.submitBtn = document.querySelector(this.config.submitSelector);
        
        if (!this.agreementCheckbox || !this.submitBtn) {
            console.warn('未找到协议复选框或提交按钮');
            return;
        }
        
        // 设置默认勾选
        if (this.config.autoCheck && this.agreementCheckbox) {
            this.agreementCheckbox.checked = true;
            this.addAutoCheckNotice();
        }
        
        this.bindEvents();
        this.setupToast();
        
        console.log('✅ 机票预订优化器已初始化');
    }
    
    bindEvents() {
        // 提交按钮点击事件
        this.submitBtn.addEventListener('click', (e) => {
            if (!this.validateAgreement()) {
                e.preventDefault();
                this.handleAgreementError();
            }
        });
        
        // 协议勾选状态变化
        if (this.agreementCheckbox) {
            this.agreementCheckbox.addEventListener('change', () => {
                if (this.agreementCheckbox.checked) {
                    this.removeHighlight();
                }
            });
        }
        
        // 表单提交事件（捕获阶段）
        document.addEventListener('submit', (e) => {
            if (e.target.contains(this.submitBtn) && !this.validateAgreement()) {
                e.preventDefault();
                this.handleAgreementError();
            }
        }, true);
    }
    
    validateAgreement() {
        return this.agreementCheckbox ? this.agreementCheckbox.checked : false;
    }
    
    handleAgreementError() {
        // 高亮协议区域
        this.highlightAgreement();
        
        // 滚动到协议位置
        this.scrollToAgreement();
        
        // 显示错误提示
        this.showToast('请先阅读并同意相关协议', 'error');
        
        // 聚焦到协议复选框
        if (this.agreementCheckbox) {
            this.agreementCheckbox.focus();
        }
    }
    
    highlightAgreement() {
        if (!this.agreementSection) return;
        
        this.agreementSection.classList.add('agreement-highlight');
        
        // 添加动画效果
        this.agreementSection.style.transition = 'all 0.3s ease';
        this.agreementSection.style.boxShadow = '0 0 0 3px rgba(245, 158, 11, 0.3)';
        this.agreementSection.style.borderColor = '#f59e0b';
        this.agreementSection.style.backgroundColor = '#fffbeb';
        
        // 自动移除高亮
        setTimeout(() => {
            this.removeHighlight();
        }, this.config.highlightDuration);
    }
    
    removeHighlight() {
        if (!this.agreementSection) return;
        
        this.agreementSection.classList.remove('agreement-highlight');
        this.agreementSection.style.boxShadow = '';
        this.agreementSection.style.borderColor = '';
        this.agreementSection.style.backgroundColor = '';
    }
    
    scrollToAgreement() {
        if (!this.agreementSection) return;
        
        const rect = this.agreementSection.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const targetPosition = rect.top + scrollTop - this.config.scrollOffset;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
    
    setupToast() {
        // 创建Toast容器
        if (!document.getElementById('agreement-toast')) {
            const toastHTML = `
                <div id="agreement-toast" class="agreement-toast">
                    <div class="toast-icon">⚠️</div>
                    <div class="toast-content">
                        <div class="toast-title"></div>
                        <div class="toast-message"></div>
                    </div>
                </div>
            `;
            
            const toastStyle = `
                <style>
                    .agreement-toast {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #ef4444;
                        color: white;
                        padding: 16px 24px;
                        border-radius: 12px;
                        box-shadow: 0 10px 25px rgba(239, 68, 68, 0.3);
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        transform: translateX(150%);
                        transition: transform 0.3s ease;
                        z-index: 10000;
                        max-width: 400px;
                    }
                    
                    .agreement-toast.show {
                        transform: translateX(0);
                    }
                    
                    .agreement-toast.success {
                        background: #10b981;
                        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
                    }
                    
                    .toast-icon {
                        font-size: 20px;
                        flex-shrink: 0;
                    }
                    
                    .toast-content {
                        flex: 1;
                    }
                    
                    .toast-title {
                        font-weight: bold;
                        margin-bottom: 4px;
                    }
                    
                    .toast-message {
                        font-size: 14px;
                        opacity: 0.9;
                    }
                    
                    .agreement-highlight {
                        animation: pulse 2s infinite;
                    }
                    
                    @keyframes pulse {
                        0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
                        70% { box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
                        100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
                    }
                </style>
            `;
            
            document.head.insertAdjacentHTML('beforeend', toastStyle);
            document.body.insertAdjacentHTML('beforeend', toastHTML);
        }
        
        this.toastElement = document.getElementById('agreement-toast');
    }
    
    showToast(message, type = 'error') {
        if (!this.toastElement) return;
        
        const title = type === 'error' ? '请先同意协议' : '操作成功';
        const toast = this.toastElement;
        
        toast.querySelector('.toast-title').textContent = title;
        toast.querySelector('.toast-message').textContent = message;
        
        toast.classList.remove('success');
        if (type === 'success') {
            toast.classList.add('success');
        }
        
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    addAutoCheckNotice() {
        if (!this.agreementSection) return;
        
        const noticeHTML = `
            <div class="auto-check-notice" style="
                background: #dbeafe;
                border: 1px solid #93c5fd;
                border-radius: 8px;
                padding: 12px 16px;
                margin-top: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
                color: #1e40af;
                font-size: 14px;
            ">
                <span style="font-size: 18px;">💡</span>
                <span>为简化您的操作，协议已默认勾选。如不同意，请取消勾选。</span>
            </div>
        `;
        
        // 在协议复选框后添加提示
        const checkboxContainer = this.agreementCheckbox.closest('label, .checkbox-container');
        if (checkboxContainer) {
            checkboxContainer.insertAdjacentHTML('afterend', noticeHTML);
        } else {
            this.agreementCheckbox.insertAdjacentHTML('afterend', noticeHTML);
        }
    }
    
    // 静态方法：快速集成
    static integrate(options = {}) {
        return new FlightBookingOptimizer(options);
    }
}

// 自动初始化（如果页面中有相关元素）
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#agreement-checkbox, [name="agreement"]')) {
            FlightBookingOptimizer.integrate();
        }
    });
} else {
    if (document.querySelector('#agreement-checkbox, [name="agreement"]')) {
        FlightBookingOptimizer.integrate();
    }
}

// 导出供模块化使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlightBookingOptimizer;
}

/**
 * 使用示例：
 * 
 * 1. 快速集成（自动检测）：
 *    <script src="flight-optimization.js"></script>
 * 
 * 2. 手动初始化：
 *    const optimizer = new FlightBookingOptimizer({
 *        agreementSelector: '#terms-checkbox',
 *        submitSelector: '.book-btn',
 *        autoCheck: true
 *    });
 * 
 * 3. 自定义样式：
 *    添加CSS类名：.agreement-highlight 用于高亮样式
 */