// AI Daily Insights 主JavaScript文件
// 处理首页数据加载和交互

document.addEventListener('DOMContentLoaded', function() {
    // 初始化
    initTheme();
    loadHomepageData();
    setupEventListeners();
});

// 初始化主题
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.querySelector('i').className = 'fas fa-sun';
        }
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 主题切换
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            const icon = this.querySelector('i');
            const isDark = document.body.classList.contains('dark-theme');
            
            if (isDark) {
                icon.className = 'fas fa-sun';
                localStorage.setItem('theme', 'dark');
            } else {
                icon.className = 'fas fa-moon';
                localStorage.setItem('theme', 'light');
            }
        });
    }
}

// 设置标签切换
function setupTabSwitchers() {
    // 资讯标签切换
    const newsTabs = document.querySelectorAll('.news-column .tab-btn');
    newsTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.dataset.category;
            
            // 更新活跃标签
            newsTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // 过滤资讯
            filterNewsByCategory(category);
        });
    });
    
    // 论文标签切换
    const paperTabs = document.querySelectorAll('.papers-column .tab-btn');
    paperTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.dataset.category;
            
            // 更新活跃标签
            paperTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // 过滤论文
            filterPapersByCategory(category);
        });
    });
}

// 按分类过滤资讯
function filterNewsByCategory(category) {
    const newsItems = document.querySelectorAll('.news-item');
    
    newsItems.forEach(item => {
        if (category === 'all' || item.dataset.category === category) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// 按分类过滤论文
function filterPapersByCategory(category) {
    const paperItems = document.querySelectorAll('.paper-item');
    
    paperItems.forEach(item => {
        if (category === 'all' || item.dataset.category === category) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// 加载首页数据
async function loadHomepageData() {
    try {
        // 加载统计数据
        await loadStats();
        
        // 加载资讯列表
        await loadNewsList();
        
        // 加载论文列表
        await loadPapersList();
        
        // 设置标签切换事件
        setupTabSwitchers();
        
        console.log('首页数据加载完成');
    } catch (error) {
        console.error('加载数据时出错:', error);
        showError('加载数据时出错，请刷新页面重试');
    }
}

// 加载统计数据
async function loadStats() {
    try {
        const response = await fetch('data/stats.json');
        if (!response.ok) throw new Error('统计数据加载失败');
        
        const stats = await response.json();
        
        // 更新最后更新时间
        const lastUpdateTime = document.getElementById('last-update-time');
        if (lastUpdateTime) {
            const lastUpdated = new Date(stats.last_updated);
            lastUpdateTime.textContent = formatTimeAgo(lastUpdated);
        }
        
        // 更新数据总量
        const totalNews = document.getElementById('total-news');
        const totalPapers = document.getElementById('total-papers');
        
        if (totalNews) totalNews.textContent = stats.total_news || '0';
        if (totalPapers) totalPapers.textContent = stats.total_papers || '0';
    } catch (error) {
        console.warn('无法加载统计数据，使用默认值:', error);
        // 使用默认值
        const lastUpdateTime = document.getElementById('last-update-time');
        if (lastUpdateTime) lastUpdateTime.textContent = '刚刚';
    }
}

// 加载资讯列表
async function loadNewsList() {
    const container = document.getElementById('news-list');
    if (!container) return;
    
    try {
        const response = await fetch('data/news.json');
        if (!response.ok) throw new Error('资讯数据加载失败');
        
        const data = await response.json();
        
        // 获取最新的5条资讯
        const news = data.news.slice(0, 5);
        
        if (news.length === 0) {
            container.innerHTML = '<p class="no-data">暂无AI资讯</p>';
            return;
        }
        
        // 生成HTML
        container.innerHTML = news.map(item => `
            <div class="news-item" data-category="${item.category}">
                <h3 class="news-title">${item.title}</h3>
                <div class="news-meta">
                    <span><i class="far fa-clock"></i> ${formatTimeAgo(new Date(item.date))}</span>
                    <span><i class="fas fa-tag"></i> ${getCategoryLabel(item.category)}</span>
                    <span><i class="fas fa-source"></i> ${item.source}</span>
                </div>
                <p class="news-summary">${item.summary}</p>
                <a href="${item.url}" target="_blank" class="read-more">
                    阅读全文 <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        `).join('');
        
        container.classList.remove('loading');
        
        // 更新资讯总数
        const totalNews = document.getElementById('total-news');
        if (totalNews) {
            totalNews.textContent = data.total || news.length;
        }
    } catch (error) {
        console.error('加载资讯列表失败:', error);
        container.innerHTML = '<p class="error">加载资讯列表失败</p>';
        container.classList.remove('loading');
    }
}

// 加载论文列表
async function loadPapersList() {
    const container = document.getElementById('papers-list');
    if (!container) return;
    
    try {
        const response = await fetch('data/papers.json');
        if (!response.ok) throw new Error('论文数据加载失败');
        
        const data = await response.json();
        
        // 获取最新的5篇论文
        const papers = data.papers.slice(0, 5);
        
        if (papers.length === 0) {
            container.innerHTML = '<p class="no-data">暂无AI论文</p>';
            return;
        }
        
        // 生成HTML
        container.innerHTML = papers.map(paper => `
            <div class="paper-item" data-category="${paper.category}">
                <h3 class="paper-title">${paper.title}</h3>
                <div class="paper-meta">
                    <span><i class="far fa-clock"></i> ${formatTimeAgo(new Date(paper.date))}</span>
                    <span><i class="fas fa-tag"></i> ${getPaperCategoryLabel(paper.category)}</span>
                    <span><i class="fas fa-user"></i> ${paper.authors[0]}${paper.authors.length > 1 ? ' 等' : ''}</span>
                </div>
                <p class="paper-abstract">${paper.abstract.substring(0, 120)}...</p>
                <a href="${paper.url}" target="_blank" class="read-more">
                    查看论文 <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        `).join('');
        
        container.classList.remove('loading');
        
        // 更新论文总数
        const totalPapers = document.getElementById('total-papers');
        if (totalPapers) {
            totalPapers.textContent = data.total || papers.length;
        }
    } catch (error) {
        console.error('加载论文列表失败:', error);
        container.innerHTML = '<p class="error">加载论文列表失败</p>';
        container.classList.remove('loading');
    }
}

// 加载最新论文
async function loadLatestPapers() {
    const container = document.getElementById('latest-papers');
    if (!container) return;
    
    try {
        const response = await fetch('data/papers.json');
        if (!response.ok) throw new Error('论文数据加载失败');
        
        const data = await response.json();
        
        // 获取最新的3篇论文
        const latest = data.papers.slice(0, 3);
        
        if (latest.length === 0) {
            container.innerHTML = '<p class="no-data">暂无最新论文</p>';
            return;
        }
        
        // 生成HTML
        container.innerHTML = latest.map(paper => `
            <div class="paper-item">
                <span class="category ${paper.category}">${getPaperCategoryLabel(paper.category)}</span>
                <h3 class="paper-title">${paper.title}</h3>
                <p class="paper-authors">${paper.authors.join(', ')}</p>
                <div class="paper-meta">
                    <span><i class="far fa-clock"></i> ${formatTimeAgo(new Date(paper.date))}</span>
                    <span><i class="fas fa-source"></i> ${paper.source}</span>
                </div>
                <p class="paper-abstract">${paper.abstract.substring(0, 150)}...</p>
                <a href="${paper.url}" target="_blank" class="read-more">
                    查看论文 <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        `).join('');
        
        container.classList.remove('loading');
    } catch (error) {
        console.error('加载最新论文失败:', error);
        container.innerHTML = '<p class="error">加载最新论文失败</p>';
        container.classList.remove('loading');
    }
}

// 加载热门话题
async function loadTrendingNews() {
    const container = document.getElementById('trending-news');
    if (!container) return;
    
    try {
        const response = await fetch('data/news.json');
        if (!response.ok) throw new Error('资讯数据加载失败');
        
        const data = await response.json();
        
        // 获取热门资讯（按时间排序，最新的在前面）
        const trending = data.news
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .slice(0, 4);
        
        if (trending.length === 0) {
            container.innerHTML = '<p class="no-data">暂无热门话题</p>';
            return;
        }
        
        // 生成HTML
        container.innerHTML = trending.map(item => `
            <div class="news-item">
                <h4 class="news-title">${item.title}</h4>
                <div class="news-meta">
                    <span>${formatTimeAgo(new Date(item.date))}</span>
                    <span>${item.source}</span>
                </div>
            </div>
        `).join('');
        
        container.classList.remove('loading');
    } catch (error) {
        console.error('加载热门话题失败:', error);
        container.innerHTML = '<p class="error">加载热门话题失败</p>';
        container.classList.remove('loading');
    }
}

// 工具函数：格式化时间
function formatTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    
    return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric'
    });
}

// 工具函数：获取分类标签
function getCategoryLabel(category) {
    const labels = {
        'research': '研究动态',
        'industry': '行业新闻',
        'product': '产品发布',
        'policy': '政策法规',
        'tools': '工具更新',
        'trend': '趋势分析'
    };
    return labels[category] || category;
}

// 工具函数：获取论文分类标签
function getPaperCategoryLabel(category) {
    const labels = {
        'nlp': '自然语言处理',
        'cv': '计算机视觉',
        'rl': '强化学习',
        'multiagent': '多智能体',
        'evaluation': '评估方法'
    };
    return labels[category] || category;
}

// 工具函数：显示错误信息
function showError(message) {
    // 可以在页面顶部显示错误提示
    console.error(message);
}

// 导出函数供其他页面使用
window.AIDailyInsights = {
    initTheme,
    formatTimeAgo,
    getCategoryLabel,
    getPaperCategoryLabel
};