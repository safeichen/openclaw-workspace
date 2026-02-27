(-2px);
        }
    `;
    document.head.appendChild(style);
    
    // 绑定关闭事件
    modal.querySelector('.modal-close').addEventListener('click', closeNewsDetail);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeNewsDetail();
    });
    
    // 加载完整内容
    setTimeout(() => {
        loadFullContent(news.id, modal);
    }, 1000);
}

// 关闭资讯详情
function closeNewsDetail() {
    const modal = document.querySelector('.news-modal');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => modal.remove(), 300);
    }
}

// 加载完整内容
async function loadFullContent(newsId, modal) {
    try {
        const content = await fetchNewsContent(newsId);
        const contentElement = modal.querySelector('.content-placeholder');
        if (contentElement) {
            contentElement.innerHTML = `
                <div class="full-content">
                    ${content || '<p>暂无详细内容</p>'}
                </div>
            `;
        }
    } catch (error) {
        console.error('加载完整内容失败:', error);
        const contentElement = modal.querySelector('.content-placeholder');
        if (contentElement) {
            contentElement.innerHTML = `
                <p><i class="fas fa-exclamation-triangle"></i> 加载失败: ${error.message}</p>
                <button class="btn-refresh" onclick="retryLoadContent('${newsId}')">
                    <i class="fas fa-redo"></i> 重试
                </button>
            `;
        }
    }
}

// 分享资讯
function shareNews(title) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: '看看这个AI资讯',
            url: window.location.href
        });
    } else {
        // 复制到剪贴板
        navigator.clipboard.writeText(`${title} - ${window.location.href}`)
            .then(() => alert('链接已复制到剪贴板'));
    }
}

// 收藏资讯
function saveNews(newsId) {
    let savedNews = JSON.parse(localStorage.getItem('savedAINews') || '[]');
    if (!savedNews.includes(newsId)) {
        savedNews.push(newsId);
        localStorage.setItem('savedAINews', JSON.stringify(savedNews));
        alert('已收藏到本地');
    } else {
        alert('已收藏过此资讯');
    }
}

// 打开原文链接
function openSource(url) {
    if (url) {
        window.open(url, '_blank');
    } else {
        alert('暂无原文链接');
    }
}

// 模拟数据（实际应该调用API）
async function fetchAINews(category = 'all', timeRange = 'today', sortBy = 'recent') {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // 模拟数据
    const mockNews = [
        {
            id: '1',
            title: 'OpenAI发布新一代多模态模型，实现文本图像视频统一理解',
            excerpt: 'OpenAI最新研究突破，推出能够同时处理文本、图像和视频的统一模型架构，在多项基准测试中刷新记录。',
            category: 'research',
            source: 'OpenAI Blog',
            date: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2小时前
            url: 'https://openai.com/blog'
        },
        {
            id: '2',
            title: '谷歌DeepMind推出AlphaFold 3，蛋白质结构预测准确率再提升',
            excerpt: 'AlphaFold 3在蛋白质结构预测方面取得重大进展，准确率相比上一代提升15%，有望加速药物研发进程。',
            category: 'research',
            source: 'Nature',
            date: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5小时前
            url: 'https://www.nature.com'
        },
        {
            id: '3',
            title: '微软将Copilot全面集成Office套件，AI办公时代来临',
            excerpt: '微软宣布将Copilot AI助手深度集成到所有Office应用中，大幅提升办公效率和创造力。',
            category: 'industry',
            source: 'Microsoft News',
            date: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8小时前
            url: 'https://news.microsoft.com'
        },
        {
            id: '4',
            title: 'AI芯片初创公司获5亿美元融资，专注边缘计算场景',
            excerpt: '专注于边缘AI计算的芯片公司完成新一轮融资，计划推出面向物联网设备的专用AI处理器。',
            category: 'startup',
            source: 'TechCrunch',
            date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1天前
            url: 'https://techcrunch.com'
        },
        {
            id: '5',
            title: '欧盟通过AI法案，建立全球最严格AI监管框架',
            excerpt: '欧洲议会正式通过AI法案，对高风险AI系统实施严格监管，为全球AI治理提供参考。',
            category: 'ethics',
            source: 'EU Parliament',
            date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2天前
            url: 'https://www.europarl.europa.eu'
        },
        {
            id: '6',
            title: 'GitHub Copilot企业版发布，支持私有代码库训练',
            excerpt: 'GitHub推出Copilot企业版本，支持在私有代码库上进行定制化训练，提升代码生成准确性。',
            category: 'tools',
            source: 'GitHub Blog',
            date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3天前
            url: 'https://github.blog'
        },
        {
            id: '7',
            title: 'NeurIPS 2026论文提交量创新高，中国学者贡献显著',
            excerpt: 'NeurIPS 2026会议论文提交数量同比增长30%，中国研究机构在多模态学习领域表现突出。',
            category: 'events',
            source: 'NeurIPS',
            date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(), // 4天前
            url: 'https://neurips.cc'
        },
        {
            id: '8',
            title: 'AI在医疗影像诊断准确率首次超越人类专家',
            excerpt: '最新研究显示，AI系统在多种医疗影像诊断任务中的准确率已达到98.7%，超越人类专家平均水平。',
            category: 'research',
            source: 'The Lancet',
            date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5天前
            url: 'https://www.thelancet.com'
        }
    ];
    
    // 根据筛选条件过滤
    let filteredNews = mockNews;
    
    if (category !== 'all') {
        filteredNews = filteredNews.filter(news => news.category === category);
    }
    
    if (timeRange === 'week') {
        const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
        filteredNews = filteredNews.filter(news => new Date(news.date) >= weekAgo);
    } else if (timeRange === 'month') {
        const monthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
        filteredNews = filteredNews.filter(news => new Date(news.date) >= monthAgo);
    }
    
    // 排序
    if (sortBy === 'recent') {
        filteredNews.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sortBy === 'relevant') {
        // 模拟相关性排序（基于标题长度和日期）
        filteredNews.sort((a, b) => {
            const scoreA = a.title.length + (new Date(a.date).getTime() / 1000000);
            const scoreB = b.title.length + (new Date(b.date).getTime() / 1000000);
            return scoreB - scoreA;
        });
    }
    
    return filteredNews;
}

// 模拟获取资讯内容
async function fetchNewsContent(newsId) {
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const contentMap = {
        '1': `
            <h4>技术突破详情</h4>
            <p>OpenAI的最新模型采用统一的Transformer架构，能够同时处理文本、图像、音频和视频输入，实现了真正的多模态理解能力。</p>
            
            <h4>关键特性</h4>
            <ul>
                <li>统一的编码器-解码器架构</li>
                <li>支持8种模态的输入输出</li>
                <li>在MMLU基准测试中达到92.3%准确率</li>
                <li>推理速度比上一代提升40%</li>
            </ul>
            
            <h4>应用场景</h4>
            <p>该技术可应用于智能助手、内容创作、教育、医疗诊断等多个领域，预计将在未来6个月内推出API服务。</p>
        `,
        '2': `
            <h4>研究进展</h4>
            <p>AlphaFold 3在蛋白质结构预测的准确性方面取得重大突破，特别是在膜蛋白和蛋白质复合物的预测上表现优异。</p>
            
            <h4>技术改进</h4>
            <ul>
                <li>引入新的注意力机制</li>
                <li>改进的训练数据增强策略</li>
                <li>更高效的推理算法</li>
                <li>支持更大规模的蛋白质预测</li>
            </ul>
            
            <h4>科学意义</h4>
            <p>这一进展将加速新药研发进程，帮助科学家更好地理解疾病机制，推动精准医疗发展。</p>
        `
    };
    
    return contentMap[newsId] || `
        <p>本文详细介绍了AI领域的最新进展和技术突破。完整内容正在整理中，请稍后查看或访问原文链接获取更多信息。</p>
        <p>AI技术正在快速发展，每天都有新的研究和应用出现。关注我们的网站，获取最新的AI资讯和深度分析。</p>
    `;
}

// 全局函数供HTML调用
window.retryLoadContent = function(newsId) {
    const modal = document.querySelector('.news-modal');
    if (modal) {
        loadFullContent(newsId, modal);
    }
};