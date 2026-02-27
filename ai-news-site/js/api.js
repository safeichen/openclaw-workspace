// AI资讯网站API接口管理

// 使用相对路径，自动匹配当前网站的主机和端口
const API_BASE_URL = '';

// API配置
const API_CONFIG = {
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// API状态
let apiStatus = {
    connected: false,
    lastCheck: null,
    errorCount: 0
};

// 初始化API连接
async function initAPIConnection() {
    try {
        console.log('正在连接AI资讯API服务器...');
        
        // 检查API状态
        const status = await checkAPIStatus();
        
        if (status.online) {
            apiStatus.connected = true;
            apiStatus.lastCheck = new Date();
            console.log('API连接成功:', status);
            
            // 更新UI状态
            updateAPIStatusUI(true);
            
            // 开始定期检查
            startAPIMonitoring();
            
            return true;
        } else {
            throw new Error('API服务器离线');
        }
    } catch (error) {
        console.error('API连接失败:', error);
        apiStatus.connected = false;
        apiStatus.errorCount++;
        
        // 更新UI状态
        updateAPIStatusUI(false, error.message);
        
        // 重试机制
        if (apiStatus.errorCount < 3) {
            setTimeout(initAPIConnection, 5000);
        }
        
        return false;
    }
}

// 检查API状态
async function checkAPIStatus() {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/status`, {
            method: 'GET',
            headers: API_CONFIG.headers
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return {
            online: true,
            ...data
        };
    } catch (error) {
        return {
            online: false,
            error: error.message,
            timestamp: new Date().toISOString()
        };
    }
}

// 带超时的fetch
async function fetchWithTimeout(url, options = {}) {
    const { timeout = API_CONFIG.timeout } = options;
    
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
}

// 更新API状态UI
function updateAPIStatusUI(connected, errorMessage = '') {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.server-status span:last-child');
    
    if (connected) {
        statusDot.className = 'status-dot active';
        statusText.textContent = '服务器在线';
        statusText.style.color = '#10b981';
    } else {
        statusDot.className = 'status-dot';
        statusDot.style.background = '#ef4444';
        statusText.textContent = errorMessage || '服务器离线';
        statusText.style.color = '#ef4444';
        
        // 显示错误提示
        showAPIErrorToast(errorMessage);
    }
}

// 显示API错误提示
function showAPIErrorToast(message) {
    // 移除现有提示
    const existingToast = document.querySelector('.api-error-toast');
    if (existingToast) existingToast.remove();
    
    // 创建新提示
    const toast = document.createElement('div');
    toast.className = 'api-error-toast';
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-exclamation-triangle"></i>
            <span>API连接错误: ${message}</span>
            <button class="toast-close"><i class="fas fa-times"></i></button>
        </div>
    `;
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .api-error-toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(239, 68, 68, 0.95);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--border-radius);
            z-index: 3000;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
            box-shadow: var(--shadow-lg);
            backdrop-filter: blur(10px);
        }
        
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .toast-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .toast-close {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 0.25rem;
            margin-left: auto;
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        
        .toast-close:hover {
            opacity: 1;
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(toast);
    
    // 绑定关闭事件
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    });
    
    // 5秒后自动关闭
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

// 开始API监控
function startAPIMonitoring() {
    // 每30秒检查一次API状态
    setInterval(async () => {
        const status = await checkAPIStatus();
        
        if (status.online !== apiStatus.connected) {
            apiStatus.connected = status.online;
            apiStatus.lastCheck = new Date();
            
            updateAPIStatusUI(status.online, status.online ? '' : '连接中断');
            
            if (status.online) {
                console.log('API重新连接成功');
                // 重新加载数据
                if (typeof loadAINews === 'function') {
                    loadAINews();
                }
            }
        }
    }, 30000);
}

// 获取AI资讯API
async function fetchAINews(category = 'all', timeRange = 'today', sortBy = 'recent') {
    try {
        // 构建查询参数
        const params = new URLSearchParams();
        if (category !== 'all') params.append('category', category);
        if (timeRange !== 'today') params.append('timeRange', timeRange);
        if (sortBy !== 'recent') params.append('sortBy', sortBy);
        
        const url = `${API_BASE_URL}/api/ai-news${params.toString() ? '?' + params.toString() : ''}`;
        
        const response = await fetchWithTimeout(url, {
            method: 'GET',
            headers: API_CONFIG.headers
        });
        
        if (!response.ok) {
            throw new Error(`API请求失败: HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // 转换API响应格式
        return data.news || data || [];
        
    } catch (error) {
        console.error('获取AI资讯失败:', error);
        
        // 如果API失败，使用模拟数据
        return getMockAINews(category, timeRange, sortBy);
    }
}

// 获取资讯内容API
async function fetchNewsContent(newsId) {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/api/ai-news/${newsId}/content`, {
            method: 'GET',
            headers: API_CONFIG.headers
        });
        
        if (!response.ok) {
            throw new Error(`API请求失败: HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data.content || '';
        
    } catch (error) {
        console.error('获取资讯内容失败:', error);
        return '无法加载详细内容，请稍后重试。';
    }
}

// 搜索AI资讯API
async function searchAINews(query, category = 'all') {
    try {
        const params = new URLSearchParams({ q: query });
        if (category !== 'all') params.append('category', category);
        
        const response = await fetchWithTimeout(`${API_BASE_URL}/api/ai-news/search?${params.toString()}`, {
            method: 'GET',
            headers: API_CONFIG.headers
        });
        
        if (!response.ok) {
            throw new Error(`API请求失败: HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data.results || [];
        
    } catch (error) {
        console.error('搜索AI资讯失败:', error);
        return [];
    }
}

// 获取趋势数据API
async function fetchAITrends() {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/api/ai-trends`, {
            method: 'GET',
            headers: API_CONFIG.headers
        });
        
        if (!response.ok) {
            throw new Error(`API请求失败: HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data.trends || {};
        
    } catch (error) {
        console.error('获取趋势数据失败:', error);
        return getMockTrends();
    }
}

// 获取系统统计API
async function fetchSystemStats() {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/api/system/stats`, {
            method: 'GET',
            headers: API_CONFIG.headers
        });
        
        if (!response.ok) {
            throw new Error(`API请求失败: HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data.stats || {};
        
    } catch (error) {
        console.error('获取系统统计失败:', error);
        return {
            totalNews: 0,
            lastUpdate: new Date().toISOString(),
            sourceCount: 0,
            categories: []
        };
    }
}

// 模拟数据（API不可用时使用）
function getMockAINews(category = 'all', timeRange = 'today', sortBy = 'recent') {
    // 这里可以复用main.js中的模拟数据
    // 为了简洁，我们直接调用main.js中的函数（如果可用）
    if (typeof window.fetchAINews === 'function') {
        return window.fetchAINews(category, timeRange, sortBy);
    }
    
    // 备用模拟数据
    return [
        {
            id: 'mock-1',
            title: 'AI资讯API正在连接中...',
            excerpt: '正在从服务器获取最新AI资讯，请稍候。',
            category: 'system',
            source: '本地缓存',
            date: new Date().toISOString(),
            url: '#'
        }
    ];
}

function getMockTrends() {
    return {
        hotTopics: [
            { rank: 1, text: 'API连接中', count: 0 },
            { rank: 2, text: '数据加载', count: 0 },
            { rank: 3, text: '系统初始化', count: 0 }
        ],
        researchOrgs: [],
        geoDistribution: []
    };
}

// 导出API函数
window.AINewsAPI = {
    init: initAPIConnection,
    getNews: fetchAINews,
    getContent: fetchNewsContent,
    search: searchAINews,
    getTrends: fetchAITrends,
    getStats: fetchSystemStats,
    checkStatus: checkAPIStatus,
    
    // 状态信息
    get status() {
        return { ...apiStatus };
    },
    
    // 配置信息
    config: API_CONFIG
};

// 页面加载时初始化API
document.addEventListener('DOMContentLoaded', async () => {
    console.log('初始化AI资讯API...');
    
    // 延迟初始化，让页面先加载
    setTimeout(async () => {
        const connected = await initAPIConnection();
        
        if (connected) {
            console.log('API初始化完成');
            
            // 如果main.js已经加载了数据，可以重新用真实API数据替换
            if (typeof window.loadAINews === 'function') {
                // 稍后重新加载真实数据
                setTimeout(() => {
                    window.loadAINews();
                }, 2000);
            }
        }
    }, 1000);
});

// 全局搜索函数
window.searchAINews = async function() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const query = searchInput.value.trim();
    if (!query) {
        alert('请输入搜索关键词');
        return;
    }
    
    const category = document.getElementById('categorySelect').value;
    const results = await searchAINews(query, category);
    
    // 显示搜索结果
    displaySearchResults(results, query);
};

// 显示搜索结果
function displaySearchResults(results, query) {
    const newsGrid = document.getElementById('newsGrid');
    if (!newsGrid) return;
    
    if (results.length === 0) {
        newsGrid.innerHTML = `
            <div class="news-placeholder">
                <div class="placeholder-content">
                    <i class="fas fa-search"></i>
                    <p>未找到关于"${query}"的AI资讯</p>
                    <button class="btn-refresh" onclick="loadAINews()">
                        <i class="fas fa-redo"></i> 返回全部资讯
                    </button>
                </div>
            </div>
        `;
        return;
    }
    
    // 清空现有内容
    newsGrid.innerHTML = '';
    
    // 显示搜索结果标题
    const searchHeader = document.createElement('div');
    searchHeader.className = 'search-header';
    searchHeader.innerHTML = `
        <h3><i class="fas fa-search"></i> 搜索结果: "${query}"</h3>
        <p>找到 ${results.length} 条相关资讯</p>
        <button class="btn-refresh" onclick="loadAINews()">
            <i class="fas fa-arrow-left"></i> 返回全部资讯
        </button>
    `;
    newsGrid.appendChild(searchHeader);
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .search-header {
            grid-column: 1 / -1;
            background: var(--dark-card);
            padding: 2rem;
            border-radius: var(--border-radius);
            margin-bottom: 1.5rem;
            text-align: center;
            border: 2px solid var(--primary-color);
        }
        
        .search-header h3 {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
            color: var(--primary-color);
        }
        
        .search-header p {
            color: var(--dark-muted);
            margin-bottom: 1.5rem;
        }
    `;
    document.head.appendChild(style);
    
    // 渲染结果
    results.forEach((news, index) => {
        const newsCard = createNewsCard(news, index);
        newsGrid.appendChild(newsCard);
    });
    
    updateNewsStats(results.length);
}