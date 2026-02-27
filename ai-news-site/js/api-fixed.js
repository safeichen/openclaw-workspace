// AI资讯网站API接口管理 - 修复版（使用模拟数据）

// 使用相对路径
const API_BASE_URL = '';

// 模拟数据
const MOCK_DATA = {
    news: [
        {
            'id': 1,
            'title': 'DeepSeek发布最新代码模型',
            'summary': 'DeepSeek-Coder在多项编程基准测试中刷新记录，支持128K上下文，代码生成准确率提升15%。',
            'source': 'AI新闻',
            'time': '2小时前',
            'category': '技术突破',
            'url': '#',
            'icon': 'fas fa-code'
        },
        {
            'id': 2,
            'title': 'OpenAI推出GPT-4.5预览版',
            'summary': '在多模态理解和推理能力上有显著提升，新增视频理解功能，推理速度提升30%。',
            'source': '科技媒体',
            'time': '5小时前',
            'category': '产品发布',
            'url': '#',
            'icon': 'fas fa-robot'
        },
        {
            'id': 3,
            'title': '中国AI芯片取得新突破',
            'summary': '自主研发的AI芯片在能效比上超越国际同类产品，算力密度达到国际领先水平。',
            'source': '产业新闻',
            'time': '1天前',
            'category': '硬件进展',
            'url': '#',
            'icon': 'fas fa-microchip'
        },
        {
            'id': 4,
            'title': 'AI辅助编程工具普及率上升',
            'summary': '调查显示超过60%的开发者日常使用AI编程助手，生产效率平均提升40%。',
            'source': '行业报告',
            'time': '2天前',
            'category': '应用趋势',
            'url': '#',
            'icon': 'fas fa-laptop-code'
        },
        {
            'id': 5,
            'title': '伦理AI框架发布',
            'summary': '国际组织推出新的AI伦理评估标准，涵盖透明度、公平性、隐私保护等核心原则。',
            'source': '政策动态',
            'time': '3天前',
            'category': '伦理规范',
            'url': '#',
            'icon': 'fas fa-balance-scale'
        },
        {
            'id': 6,
            'title': 'AI在医疗诊断中的应用',
            'summary': '新研究显示AI辅助诊断准确率超过资深医生，在早期癌症检测中表现突出。',
            'source': '学术研究',
            'time': '4天前',
            'category': '行业应用',
            'url': '#',
            'icon': 'fas fa-heartbeat'
        }
    ],
    trends: {
        '热门话题': ['大语言模型', '多模态AI', 'AI芯片', '自动驾驶', 'AI医疗', '生成式AI'],
        '技术趋势': ['Agent智能体', '具身智能', 'AI生成视频', '强化学习', '联邦学习', '神经符号AI']
    },
    stats: {
        'total_news': 156,
        'today_news': 12,
        'hot_topics': 8,
        'last_updated': new Date().toLocaleString('zh-CN')
    }
};

// API状态
let apiStatus = {
    connected: true,  // 直接设置为已连接
    lastCheck: new Date(),
    errorCount: 0
};

// 初始化API连接
async function initAPIConnection() {
    console.log('使用模拟数据模式...');
    
    apiStatus.connected = true;
    apiStatus.lastCheck = new Date();
    
    // 更新UI状态
    updateAPIStatusUI(true);
    
    // 立即加载数据
    setTimeout(() => {
        loadAIData();
    }, 500);
    
    return true;
}

// 检查API状态（模拟）
async function checkAPIStatus() {
    return {
        online: true,
        service: 'AI资讯聚合站（模拟模式）',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    };
}

// 获取AI资讯数据（模拟）
async function fetchAINews() {
    return new Promise((resolve) => {
        // 模拟网络延迟
        setTimeout(() => {
            resolve({
                success: true,
                data: MOCK_DATA.news,
                trends: MOCK_DATA.trends,
                stats: MOCK_DATA.stats,
                timestamp: new Date().toISOString(),
                message: '使用模拟数据'
            });
        }, 300);
    });
}

// 更新API状态UI
function updateAPIStatusUI(connected) {
    const statusElement = document.getElementById('api-status');
    if (statusElement) {
        if (connected) {
            statusElement.innerHTML = '<i class="fas fa-check-circle"></i> API已连接（模拟模式）';
            statusElement.className = 'api-status connected';
        } else {
            statusElement.innerHTML = '<i class="fas fa-times-circle"></i> API连接失败';
            statusElement.className = 'api-status disconnected';
        }
    }
}

// 开始API监控
function startAPIMonitoring() {
    // 每30秒检查一次
    setInterval(async () => {
        try {
            const status = await checkAPIStatus();
            if (status.online) {
                apiStatus.connected = true;
                apiStatus.lastCheck = new Date();
                updateAPIStatusUI(true);
            } else {
                apiStatus.connected = false;
                apiStatus.errorCount++;
                updateAPIStatusUI(false);
            }
        } catch (error) {
            console.warn('API监控检查失败:', error);
            apiStatus.connected = false;
            apiStatus.errorCount++;
            updateAPIStatusUI(false);
        }
    }, 30000);
}

// 显示错误消息
function showError(message) {
    console.error('API错误:', message);
    
    // 可以在这里添加错误提示UI
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
        `;
        errorContainer.style.display = 'block';
        
        // 5秒后自动隐藏
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    }
}

// 导出函数
window.AI_API = {
    init: initAPIConnection,
    fetchNews: fetchAINews,
    checkStatus: checkAPIStatus,
    getStatus: () => apiStatus
};

console.log('AI资讯API模块已加载（模拟模式）');