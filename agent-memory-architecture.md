# Agent记忆架构设计文档

基于最新AI研究（2026年4月）的现代化Agent记忆系统设计

## 1. 概述

### 1.1 设计背景
随着AI代理能力的不断提升，记忆系统成为决定代理智能水平的关键因素。本文档基于最新的AI研究进展（特别是TREX系统、Skelebones绑定系统和代理记忆研究），设计了一个分层、可扩展的Agent记忆架构。

### 1.2 设计原则
- **分层存储**: 模拟人类记忆的多层次结构
- **混合数据库**: 充分利用不同数据库的优势
- **智能检索**: 基于语义的跨记忆类型检索
- **动态优化**: 根据使用模式自动调整
- **可扩展性**: 支持大规模部署和多代理协作

## 2. 架构概览

```
┌─────────────────────────────────────────────────────┐
│                   Agent Memory System                │
├─────────────────────────────────────────────────────┤
│                 Memory Orchestrator                  │
├─────────┬─────────┬─────────┬─────────┬─────────┤
│Working  │Episodic │Semantic │Procedural│External │
│Memory   │Memory   │Memory   │Memory   │Memory   │
├─────────┼─────────┼─────────┼─────────┼─────────┤
│Redis    │MySQL    │Elastic- │MySQL    │Vector   │
│(短期)   │(事件)   │Search   │(技能)   │DB       │
│         │         │(知识)   │         │(文档)   │
└─────────┴─────────┴─────────┴─────────┴─────────┘
```

## 3. 分层记忆设计

### 3.1 工作记忆 (Working Memory)

#### 存储介质
- **主存储**: Redis 7.x Cluster
- **备份**: 可选MySQL（用于持久化重要工作状态）

#### 特点
- 高速访问（<10ms延迟）
- 临时存储（TTL: 1-24小时）
- 容量有限（默认1000项）

#### 存储内容
```yaml
working_memory_content:
  session_context:
    - 当前对话状态
    - 用户意图识别
    - 任务执行进度
  short_term_state:
    - 推理中间结果
    - 临时变量
    - 上下文窗口
  immediate_cache:
    - 最近使用的工具结果
    - 高频查询缓存
```

#### 数据结构
```python
# Redis数据结构设计
working_memory_schema = {
    "session:{session_id}": {
        "type": "hash",
        "fields": ["context", "state", "timestamp", "ttl"]
    },
    "cache:{query_hash}": {
        "type": "string",
        "value": "cached_result",
        "ttl": 3600
    },
    "queue:{task_id}": {
        "type": "list",
        "items": ["task_step_1", "task_step_2"]
    }
}
```

### 3.2 情景记忆 (Episodic Memory)

#### 存储介质
- **主存储**: MySQL 8.x（支持JSON）
- **缓存**: Redis（热点数据）
- **归档**: 对象存储（历史数据）

#### 表结构设计
```sql
-- 情景记忆主表
CREATE TABLE episodic_memory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    agent_id VARCHAR(64) NOT NULL,
    
    -- 事件类型
    event_type ENUM(
        'conversation',     -- 对话事件
        'task_execution',   -- 任务执行
        'decision_making',  -- 决策过程
        'tool_usage',       -- 工具使用
        'error_occurrence',  -- 错误发生
        'learning_event'    -- 学习事件
    ) NOT NULL,
    
    -- 事件内容
    content JSON NOT NULL,
    
    -- 时间信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 向量化表示（用于语义检索）
    embedding_vector BLOB,
    
    -- 元数据
    metadata JSON,
    
    -- 索引
    INDEX idx_session (session_id),
    INDEX idx_user (user_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at),
    INDEX idx_composite (user_id, event_type, created_at)
);

-- 事件关系表（用于构建记忆图谱）
CREATE TABLE episodic_relationships (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    source_event_id BIGINT NOT NULL,
    target_event_id BIGINT NOT NULL,
    relationship_type ENUM(
        'causes',           -- 导致
        'follows',          -- 跟随
        'contradicts',      -- 矛盾
        'supports',         -- 支持
        'learns_from'       -- 学习自
    ) NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (source_event_id) REFERENCES episodic_memory(id),
    FOREIGN KEY (target_event_id) REFERENCES episodic_memory(id),
    INDEX idx_relationship (source_event_id, relationship_type)
);
```

#### 压缩策略
```python
class EpisodicMemoryCompressor:
    """基于Skelebones思想的记忆压缩"""
    
    def compress_events(self, events: List[Event]) -> CompressedEpisode:
        """
        将连续事件压缩为关键记忆点
        
        压缩策略：
        1. 提取决策关键帧
        2. 移除冗余信息
        3. 生成记忆摘要
        4. 构建时间线图谱
        """
        pass
    
    def generate_summary(self, episode: Episode) -> str:
        """生成事件摘要（类似人类记忆的概括）"""
        pass
```

### 3.3 语义记忆 (Semantic Memory)

#### 存储介质
- **主存储**: Elasticsearch 8.x
- **关系存储**: MySQL（用于结构化知识）
- **图数据库**: Neo4j（可选，用于复杂关系）

#### Elasticsearch索引设计
```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "ik_smart_cn": {
          "type": "custom",
          "tokenizer": "ik_smart"
        },
        "ik_max_word_cn": {
          "type": "custom",
          "tokenizer": "ik_max_word"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "concept": {
        "type": "keyword",
        "fields": {
          "text": {"type": "text", "analyzer": "ik_smart_cn"}
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ik_max_word_cn",
        "fields": {
          "keyword": {"type": "keyword"}
        }
      },
      "category": {
        "type": "keyword"
      },
      "confidence": {
        "type": "float",
        "index": false
      },
      "source": {
        "type": "keyword"
      },
      "created_at": {
        "type": "date"
      },
      "updated_at": {
        "type": "date"
      },
      "relationships": {
        "type": "nested",
        "properties": {
          "type": {"type": "keyword"},
          "target": {"type": "keyword"},
          "strength": {"type": "float"}
        }
      },
      "embeddings": {
        "type": "dense_vector",
        "dims": 768,
        "index": true,
        "similarity": "cosine"
      },
      "metadata": {
        "type": "object",
        "enabled": true
      }
    }
  }
}
```

#### 知识图谱构建
```python
class KnowledgeGraphBuilder:
    """基于语义记忆构建知识图谱"""
    
    def extract_concepts(self, text: str) -> List[Concept]:
        """从文本中提取概念"""
        pass
    
    def identify_relationships(self, concepts: List[Concept]) -> List[Relationship]:
        """识别概念间关系"""
        pass
    
    def update_graph(self, new_knowledge: Knowledge):
        """增量更新知识图谱"""
        pass
```

### 3.4 程序记忆 (Procedural Memory)

#### 存储介质
- **主存储**: MySQL 8.x
- **缓存**: Redis（高频技能）
- **版本控制**: Git（代码类技能）

#### 表结构设计
```sql
-- 技能定义表
CREATE TABLE skills (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    skill_name VARCHAR(128) NOT NULL UNIQUE,
    skill_type ENUM(
        'tool_usage',       -- 工具使用
        'workflow',         -- 工作流程
        'problem_solving',  -- 问题解决
        'communication',    -- 沟通技巧
        'reasoning',        -- 推理方法
        'learning'          -- 学习策略
    ) NOT NULL,
    
    -- 技能定义
    definition TEXT,
    steps JSON NOT NULL,
    prerequisites JSON,
    
    -- 性能指标
    success_rate FLOAT DEFAULT 0.0,
    avg_execution_time INT DEFAULT 0,
    total_executions INT DEFAULT 0,
    last_success_at DATETIME,
    last_failure_at DATETIME,
    
    -- 元数据
    created_by VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_skill_type (skill_type),
    INDEX idx_success_rate (success_rate),
    INDEX idx_updated_at (updated_at)
);

-- 技能执行记录表
CREATE TABLE skill_executions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    skill_id BIGINT NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    
    -- 执行上下文
    input_parameters JSON,
    execution_context JSON,
    
    -- 执行结果
    status ENUM('success', 'failure', 'partial', 'timeout') NOT NULL,
    output_result JSON,
    error_message TEXT,
    
    -- 性能数据
    start_time DATETIME,
    end_time DATETIME,
    execution_time_ms INT,
    
    -- 学习数据
    lessons_learned TEXT,
    improvements_suggested TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    INDEX idx_skill_session (skill_id, session_id),
    INDEX idx_status_time (status, created_at)
);

-- 技能改进历史
CREATE TABLE skill_improvements (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    skill_id BIGINT NOT NULL,
    version INT NOT NULL,
    
    -- 改进内容
    change_description TEXT NOT NULL,
    change_type ENUM('optimization', 'bug_fix', 'enhancement', 'refactor') NOT NULL,
    changes_applied JSON NOT NULL,
    
    -- 效果评估
    before_metrics JSON,
    after_metrics JSON,
    improvement_percentage FLOAT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    UNIQUE KEY uk_skill_version (skill_id, version)
);
```

#### 技能优化算法
```python
class SkillOptimizer:
    """基于执行记录的技能优化"""
    
    def analyze_performance(self, skill_id: int) -> PerformanceReport:
        """分析技能执行性能"""
        pass
    
    def suggest_improvements(self, skill: Skill) -> List[Improvement]:
        """基于模式识别提出改进建议"""
        pass
    
    def auto_optimize(self, skill: Skill) -> OptimizedSkill:
        """自动优化技能执行步骤"""
        pass
```

### 3.5 外部记忆 (External Memory)

#### 存储介质
- **向量数据库**: Qdrant 1.7.x / Pinecone / Milvus
- **文档存储**: 对象存储（S3/MinIO）
- **索引**: Elasticsearch（元数据索引）

#### 向量化策略
```python
class VectorizationStrategy:
    """多模态向量化策略"""
    
    def __init__(self):
        # 文本编码器
        self.text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 代码编码器（可选）
        self.code_encoder = CodeBERT()
        
        # 多模态编码器（可选）
        self.multimodal_encoder = CLIPModel()
    
    def encode_text(self, text: str) -> List[float]:
        """文本向量化"""
        return self.text_encoder.encode(text)
    
    def encode_document(self, document: Document) -> DocumentVector:
        """文档向量化（分块+聚合）"""
        pass
    
    def encode_multimodal(self, content: MultiModalContent) -> List[float]:
        """多模态内容向量化"""
        pass
```

#### Qdrant集合配置
```python
qdrant_collection_config = {
    "vectors": {
        "size": 768,  # BERT向量维度
        "distance": "Cosine"
    },
    "shard_number": 3,
    "replication_factor": 2,
    "write_consistency_factor": 1,
    "on_disk_payload": True,
    "hnsw_config": {
        "m": 16,
        "ef_construct": 200,
        "full_scan_threshold": 10000
    },
    "optimizers_config": {
        "default_segment_number": 3,
        "max_segment_size": None,
        "memmap_threshold": 50000,
        "indexing_threshold": 20000,
        "flush_interval_sec": 5
    }
}
```

## 4. 记忆协调器 (Memory Orchestrator)

### 4.1 核心架构
```python
class MemoryOrchestrator:
    """统一记忆管理协调器"""
    
    def __init__(self, config: MemoryConfig):
        # 初始化各层记忆
        self.working_memory = RedisMemory(config.redis)
        self.episodic_memory = MySQLMemory(config.mysql)
        self.semantic_memory = ElasticsearchMemory(config.elasticsearch)
        self.procedural_memory = MySQLMemory(config.mysql)
        self.external_memory = VectorDBMemory(config.vectordb)
        
        # 协调器组件
        self.retriever = HybridRetriever(self)
        self.consolidator = MemoryConsolidator(self)
        self.evolver = MemoryEvolver(self)
        
        # 缓存和监控
        self.cache = LRUCache(maxsize=1000)
        self.metrics = MemoryMetricsCollector()
    
    async def store(self, 
                   memory_type: MemoryType,
                   content: Union[dict, str, bytes],
                   metadata: dict = None,
                   priority: Priority = Priority.NORMAL) -> MemoryRecord:
        """
        统一存储接口
        
        参数:
            memory_type: 记忆类型
            content: 存储内容
            metadata: 元数据
            priority: 存储优先级
            
        返回:
            MemoryRecord: 存储记录
        """
        # 1. 验证和预处理
        validated_content = self._validate_content(content)
        enriched_metadata = self._enrich_metadata(metadata)
        
        # 2. 选择存储策略
        storage_strategy = self._select_storage_strategy(
            memory_type, validated_content, priority
        )
        
        # 3. 执行存储
        record = await storage_strategy.store(
            validated_content, enriched_metadata
        )
        
        # 4. 更新索引和缓存
        await self._update_indices(record)
        
        # 5. 记录指标
        self.metrics.record_store(record)
        
        return record
    
    async def retrieve(self,
                      query: str,
                      memory_types: List[MemoryType] = None,
                      filters: dict = None,
                      limit: int = 10,
                      similarity_threshold: float = 0.7) -> List[MemoryRecord]:
        """
        智能检索：跨记忆类型联合查询
        
        参数:
            query: 查询文本
            memory_types: 要检索的记忆类型（None表示全部）
            filters: 过滤条件
            limit: 返回结果数量
            similarity_threshold: 相似度阈值
            
        返回:
            List[MemoryRecord]: 检索结果
        """
        # 1. 查询解析和优化
        parsed_query = self._parse_query(query)
        
        # 2. 并行检索各记忆层
        tasks = []
        target_types = memory_types or list(MemoryType)
        
        for mem_type in target_types:
            task = self._retrieve_from_memory(
                mem_type, parsed_query, filters, limit * 2
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # 3. 结果合并和重排序
        all_results = []
        for mem_results in results:
            all_results.extend(mem_results)
        
        # 4. 重排序（基于相关性、新鲜度、重要性）
        reranked = await self._rerank_results(
            all_results, parsed_query, similarity_threshold
        )
        
        # 5. 多样性采样（避免结果同质化）
        final_results = self._diversity_sampling(reranked, limit)
        
        # 6. 记录检索指标
        self.metrics.record_retrieve(
            query, len(final_results), len(all_results)
        )
        
        return final_results
    
    async def consolidate(self, 
                         session_id: str = None,
                         force: bool = False) -> ConsolidationReport:
        """
        记忆巩固：将工作记忆转移到长期记忆
        
        参数:
            session_id: 会话ID（None表示所有会话）
            force: 是否强制巩固
            
        返回:
            ConsolidationReport: 巩固报告
        """
        return await self.consolidator.consolidate(session_id, force)
    
    async def forget(self,
                    criteria: dict,
                    memory_types: List[MemoryType] = None) -> ForgetReport:
        """
        选择性遗忘：清理过时/低价值记忆
        
        参数:
            criteria: 遗忘标准
            memory_types: 要清理的记忆类型
            
        返回:
            ForgetReport: 遗忘报告
        """
        return await self.evolver.forget(criteria, memory_types)
    
    async def evolve(self) -> EvolutionReport:
        """
        记忆进化：优化记忆结构和内容
        """
        return await self.evolver.evolve()
```

### 4.2 混合检索器 (Hybrid Retriever)

```python
class HybridRetriever:
    """混合检索器：结合关键词、向量和语义检索"""
    
    def __init__(self, orchestrator: MemoryOrchestrator):
        self.orchestrator = orchestrator
        
        # 检索器组件
        self.keyword_retriever = KeywordRetriever()
        self.vector_retriever = VectorRetriever()
        self.semantic_retriever = SemanticRetriever()
        
        # 重排序器
        self.reranker = CrossEncoderReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        # 融合策略
        self.fusion_strategy = ReciprocalRankFusion()
    
    async def retrieve(self,
                      query: str,
                      memory_types: List[MemoryType],
                      filters: dict = None,
                      k: int = 10) -> List[MemoryRecord]:
        """
        混合检索主流程
        """
        # 1. 多路并行检索
        keyword_results = await self.keyword_retriever.retrieve(
            query, memory_types, filters, k * 3
        )
        
        vector_results = await self.vector_retriever.retrieve(
            query, memory_types, filters, k * 3
        )
        
        semantic_results = await self.semantic_retriever.retrieve(
            query, memory_types, filters, k * 3
        )
        
        # 2. 结果融合
        fused_results = self.fusion_strategy.fuse([
            keyword_results,
            vector_results,
            semantic_results
        ])
        
        # 3. 重排序
        reranked = await self.reranker.rerank(query, fused_results)
        
        # 4. 多样性采样
        final_results = self._apply_diversity_sampling(reranked, k)
        
        return final_results
    
    def _apply_diversity_sampling(self, 
                                 results: List[MemoryRecord],
                                 k: int) -> List[MemoryRecord]:
        """
        多样性采样：确保结果覆盖不同方面
        """
        if len(results) <= k:
            return results
        
        # 基于内容聚类
        clusters = self._cluster_results(results, k // 2)
        
        # 从每个聚类中选取代表性结果
        sampled = []
        for cluster in clusters:
            # 选取聚类中心或最高分结果
            representative = self._select_representative(cluster)
            sampled.append(representative)
            
            if len(sampled) >= k:
                break
        
        # 如果还不够，补充高分结果
        if len(sampled) < k:
            remaining = [r for r in results if r not in sampled]
            remaining.sort(key=lambda x: x.score, reverse=True)
            sampled.extend(remaining[:k - len(sampled)])
        
        return sampled
```

### 4.3 记忆巩固器 (Memory Consolidator)

```python
class MemoryConsolidator:
    """记忆巩固器：将短期记忆转移到长期记忆"""
    
    def __init__(self, orchestrator: MemoryOrchestrator):
        self.orchestrator = orchestrator
        
        # 巩固策略
        self.consolidation_policies = {
            MemoryType.WORKING: WorkingMemoryConsolidationPolicy(),
            MemoryType.EPISODIC: EpisodicMemoryConsolidationPolicy(),
            MemoryType.SEMANTIC: SemanticMemoryConsolidationPolicy()
        }
    
    async def consolidate(self,
                         session_id: str = None,
                         force: bool = False) -> ConsolidationReport:
        """
        执行记忆巩固
        """
        report = ConsolidationReport()
        
        # 1. 收集需要巩固的记忆
        memories_to_consolidate = await self._collect_memories(
            session_id, force
        )
        
        # 2. 按类型分组处理
        for memory_type, memories in memories_to_consolidate.items():
            if not memories:
                continue
            
            policy = self.consolidation_policies.get(memory_type)
            if not policy:
                continue
            
            # 3. 应用巩固策略
            consolidated = await policy.consolidate(memories)
            
            # 4. 更新报告
            report.add_consolidation(memory_type, len(memories), len(consolidated))
            
            # 5. 触发后续处理
            await self._post_consolidation_processing(consolidated)
        
        return report
    
    async def _collect_memories(self,
                               session_id: str,
                               force: bool) -> Dict[MemoryType, List[MemoryRecord]]:
        """
        收集需要巩固的记忆
        """
        memories = {}
        
        # 工作记忆：基于TTL和重要性
        if force or self._should_consolidate_working_memory():
            working_memories = await self.orchestrator.working_memory.get_expiring()
            memories[MemoryType.WORKING] = working_memories
        
        # 情景记忆：基于事件完整性和时间
        if force or self._should_consolidate_episodic_memory():
            episodic_memories = await self._get_complete_episodes(session_id)
            memories[MemoryType.EPISODIC] = episodic_memories
        
        return memories
```

### 4.4 记忆进化器 (Memory Evolver)

```python
class MemoryEvolver:
    """记忆进化器：优化和清理记忆"""
    
    def __init__(self, orchestrator: MemoryOrchestrator):
        self.orchestrator = orchestrator
        
        # 进化策略
        self.evolution_strategies = {
            'compression': MemoryCompressionStrategy(),
            'pruning': MemoryPruningStrategy(),
            'reorganization': MemoryReorganizationStrategy(),
            'generalization': MemoryGeneralizationStrategy()
        }
    
    async def evolve(self) -> EvolutionReport:
        """
        执行记忆进化
        """
        report = EvolutionReport()
        
        # 1. 分析记忆状态
        memory_analysis = await self._analyze_memory_state()
        
        # 2. 确定进化策略
        strategies = self._select_evolution_strategies(memory_analysis)
        
        # 3. 执行进化
        for strategy_name in strategies:
            strategy = self.evolution_strategies[strategy_name]
            
            evolution_result = await strategy.evolve(
                self.orchestrator, memory_analysis
            )
            
            report.add_evolution(strategy_name, evolution_result)
        
        # 4. 验证进化效果
        verification = await self._verify_evolution(report)
        report.verification = verification
        
        return report
    
    async def forget(self,
                    criteria: dict,
                    memory_types: List[MemoryType] = None) -> ForgetReport:
        """
        选择性遗忘
        """
        report = ForgetReport()
        
        target_types = memory_types or list(MemoryType)
        
        for memory_type in target_types:
            # 根据标准选择要遗忘的记忆
            memories_to_forget = await self._select_memories_to_forget(
                memory_type, criteria
            )
            
            if not memories_to_forget:
                continue
            
            # 执行遗忘
            forgotten_count = await self._execute_forgetting(
                memory_type, memories_to_forget
            )
            
            # 更新报告
            report.add_forgotten(memory_type, len(memories_to_forget), forgotten_count)
        
        return report
```

## 5. 基于最新研究的创新特性

### 5.1 动态记忆压缩（基于Skelebones思想）

```python
class DynamicMemoryCompression:
    """动态记忆压缩系统"""
    
    def compress_episodic_memory(self, 
                                events: List[Event]) -> CompressedMemory:
        """
        将连续事件压缩为关键记忆点
        
        算法步骤：
        1. 事件聚类：将相关事件分组
        2. 关键帧提取：识别重要决策点
        3. 冗余消除：移除重复信息
        4. 摘要生成：创建记忆摘要
        5. 关系重建：保持事件间关系
        """
        
        # 1. 事件聚类（基于时间和语义）
        clusters = self._cluster_events(events)
        
        # 2. 提取每个聚类的关键帧
        keyframes = []
        for cluster in clusters:
            keyframe = self._extract_keyframe(cluster)
            if keyframe:
                keyframes.append(keyframe)
        
        # 3. 构建压缩记忆结构
        compressed = CompressedMemory(
            keyframes=keyframes,
            timeline=self._build_timeline(keyframes),
            summary=self._generate_summary(keyframes),
            metadata={
                'compression_ratio': len(keyframes) / len(events),
                'original_event_count': len(events),
                'compressed_event_count': len(keyframes)
            }
        )
        
        return compressed
    
    def _extract_keyframe(self, cluster: List[Event]) -> Optional[Keyframe]:
        """
        从事件聚类中提取关键帧
        
        关键帧选择标准：
        1. 决策点：导致状态改变的事件
        2. 转折点：任务方向改变
        3. 学习点：获得新知识
        4. 错误点：发生错误并纠正
        """
        # 计算每个事件的重要性分数
        scored_events = []
        for event in cluster:
            score = self._calculate_event_importance(event, cluster)
            scored_events.append((event, score))
        
        # 选择最高分事件作为关键帧
        if not scored_events:
            return None
        
        best_event, best_score = max(scored_events, key=lambda x: x[1])
        
        # 只保留重要性足够高的事件
        if best_score < self.importance_threshold:
            return None
        
        return Keyframe(
            event=best_event,
            importance=best_score,
            context_events=[e for e, _ in scored_events if e != best_event],
            compression_notes=self._generate_compression_notes(cluster)
        )
```

### 5.2 多代理记忆共享（基于TREX系统）

```python
class MultiAgentMemorySharing:
    """多代理记忆共享系统"""
    
    def __init__(self, agent_count: int):
        self.agents = [AgentMemory(i) for i in range(agent_count)]
        self.shared_memory = SharedMemorySpace()
        self.consensus_engine = ConsensusEngine()
        
    async def share_context(self,
                           agent_id: int,
                           context: AgentContext,
                           priority: SharingPriority = SharingPriority.NORMAL):
        """
        代理间上下文共享
        """
        # 1. 准备共享内容
        shareable_content = self._prepare_for_sharing(context)
        
        # 2. 选择共享策略
        strategy = self._select_sharing_strategy(
            agent_id, shareable_content, priority
        )
        
        # 3. 执行共享
        sharing_result = await strategy.share(
            agent_id, shareable_content, self.agents
        )
        
        # 4. 更新共享记忆空间
        await self.shared_memory.update(
            agent_id, shareable_content, sharing_result
        )
        
        # 5. 触发共识形成（如果需要）
        if sharing_result.requires_consensus:
            await self._form_consensus(sharing_result)
        
        return sharing_result
    
    async def form_consensus(self, 
                            conflicting_memories: List[AgentMemory]) -> Consensus:
        """
        形成记忆共识
        
        基于TREX系统的多代理协作思想：
        1. 冲突检测：识别不一致的记忆
        2. 证据收集：收集支持证据
        3. 权重分配：基于代理可信度
        4. 共识达成：多数决或加权平均
        5. 记忆更新：同步所有代理
        """
        
        # 1. 分析冲突
        conflicts = self._analyze_conflicts(conflicting_memories)
        
        # 2. 收集证据
        evidence = await self._collect_evidence(conflicts)
        
        # 3. 计算代理权重
        agent_weights = self._calculate_agent_weights(conflicting_memories, evidence)
        
        # 4. 达成共识
        consensus = self.consensus_engine.reach_consensus(
            conflicts, evidence, agent_weights
        )
        
        # 5. 应用共识
        await self._apply_consensus(consensus, conflicting_memories)
        
        return consensus
```

### 5.3 记忆进化机制

```python
class MemoryEvolutionMechanism:
    """记忆进化机制"""
    
    def evolve_semantic_memory(self):
        """
        语义记忆进化
        
        进化方向：
        1. 概念细化：从模糊到精确
        2. 关系发现：发现新的概念关联
        3. 知识修正：纠正错误知识
        4. 抽象提升：从具体到抽象
        """
        
        # 1. 分析当前知识状态
        knowledge_analysis = self._analyze_knowledge_state()
        
        # 2. 识别进化机会
        evolution_opportunities = self._identify_evolution_opportunities(
            knowledge_analysis
        )
        
        # 3. 执行进化操作
        for opportunity in evolution_opportunities:
            if opportunity.type == EvolutionType.CONCEPT_REFINEMENT:
                await self._refine_concept(opportunity)
            elif opportunity.type == EvolutionType.RELATION_DISCOVERY:
                await self._discover_relation(opportunity)
            elif opportunity.type == EvolutionType.KNOWLEDGE_CORRECTION:
                await self._correct_knowledge(opportunity)
            elif opportunity.type == EvolutionType.ABSTRACTION:
                await self._abstract_knowledge(opportunity)
        
        # 4. 验证进化效果
        verification = await self._verify_evolution()
        
        return EvolutionResult(
            opportunities_processed=len(evolution_opportunities),
            verification=verification,
            timestamp=datetime.now()
        )
    
    def _identify_evolution_opportunities(self, 
                                        analysis: KnowledgeAnalysis) -> List[EvolutionOpportunity]:
        """
        识别进化机会
        
        识别标准：
        1. 概念模糊性：定义不清晰的概念
        2. 关系稀疏性：孤立的概念节点
        3. 证据冲突：相互矛盾的证据
        4. 模式重复：频繁出现的相似模式
        """
        opportunities = []
        
        # 模糊概念识别
        vague_concepts = self._find_vague_concepts(analysis.concepts)
        for concept in vague_concepts:
            opportunities.append(
                EvolutionOpportunity(
                    type=EvolutionType.CONCEPT_REFINEMENT,
                    target=concept,
                    confidence=concept.vagueness_score,
                    description=f"概念'{concept.name}'定义模糊，需要细化"
                )
            )
        
        # 稀疏关系识别
        sparse_relations = self._find_sparse_relations(analysis.relations)
        for relation in sparse_relations:
            opportunities.append(
                EvolutionOpportunity(
                    type=EvolutionType.RELATION_DISCOVERY,
                    target=relation,
                    confidence=relation.sparsity_score,
                    description=f"关系'{relation.type}'连接稀疏，可能缺失关联"
                )
            )
        
        # 按置信度排序
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        
        return opportunities
```

## 6. RAG增强检索系统

### 6.1 增强型RAG架构

```python
class EnhancedRAGSystem:
    """增强型RAG系统"""
    
    def __init__(self, memory_orchestrator: MemoryOrchestrator):
        self.orchestrator = memory_orchestrator
        
        # 检索组件
        self.retriever = HybridRetriever(memory_orchestrator)
        self.reranker = CrossEncoderReranker()
        self.query_understanding = QueryUnderstandingModule()
        
        # 生成组件
        self.generator = LLMGenerator()
        self.citation_generator = CitationGenerator()
        
        # 优化组件
        self.feedback_loop = FeedbackLoop()
        self.quality_assessor = QualityAssessor()
    
    async def answer_query(self,
                          query: str,
                          context: dict = None,
                          options: RAGOptions = None) -> RAGResponse:
        """
        增强RAG问答流程
        """
        # 1. 查询理解和重写
        understood_query = await self.query_understanding.understand(query, context)
        rewritten_queries = self._rewrite_query(understood_query)
        
        # 2. 多路检索
        all_results = []
        for rq in rewritten_queries:
            results = await self.retriever.retrieve(
                query=rq.query,
                memory_types=rq.memory_types,
                filters=rq.filters,
                k=options.retrieval_k if options else 20
            )
            all_results.extend(results)
        
        # 3. 结果去重和重排序
        deduplicated = self._deduplicate_results(all_results)
        reranked = await self.reranker.rerank(understood_query, deduplicated)
        
        # 4. 上下文构建
        context = self._build_context(reranked, options.context_limit if options else 4000)
        
        # 5. 生成回答
        answer = await self.generator.generate(
            query=understood_query,
            context=context,
            options=options.generation_options if options else None
        )
        
        # 6. 生成引用
        citations = await self.citation_generator.generate(
            answer, reranked, options.citation_style if options else "default"
        )
        
        # 7. 质量评估
        quality = await self.quality_assessor.assess(
            query=understood_query,
            answer=answer,
            context=context,
            citations=citations
        )
        
        # 8. 反馈收集和学习
        if options and options.enable_feedback:
            await self.feedback_loop.record_interaction(
                query=query,
                understood_query=understood_query,
                retrieved_results=reranked,
                answer=answer,
                quality=quality
            )
        
        return RAGResponse(
            answer=answer,
            citations=citations,
            quality=quality,
            retrieved_context=context,
            metadata={
                'query_understanding': understood_query,
                'retrieval_count': len(reranked),
                'generation_model': self.generator.model_name
            }
        )
    
    async def _rewrite_query(self, understood_query: UnderstoodQuery) -> List[RewrittenQuery]:
        """
        查询重写策略
        
        重写类型：
        1. 关键词扩展：添加同义词和相关术语
        2. 问题分解：将复杂问题分解为子问题
        3. 时间范围调整：根据查询调整时间范围
        4. 记忆类型定向：针对特定记忆类型优化
        """
        rewritten = []
        
        # 基础重写（原查询）
        rewritten.append(RewrittenQuery(
            query=understood_query.original_text,
            memory_types=[MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.EXTERNAL],
            filters=understood_query.filters
        ))
        
        # 关键词扩展
        if understood_query.requires_keyword_expansion:
            expanded = self._expand_keywords(understood_query)
            rewritten.append(RewrittenQuery(
                query=expanded,
                memory_types=[MemoryType.SEMANTIC, MemoryType.EXTERNAL],
                filters=understood_query.filters
            ))
        
        # 问题分解（针对复杂查询）
        if understood_query.is_complex:
            sub_queries = self._decompose_query(understood_query)
            for sub_q in sub_queries:
                rewritten.append(RewrittenQuery(
                    query=sub_q,
                    memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL],
                    filters=understood_query.filters
                ))
        
        return rewritten
```

### 6.2 查询理解模块

```python
class QueryUnderstandingModule:
    """查询理解模块"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.temporal_parser = TemporalParser()
    
    async def understand(self, 
                        query: str, 
                        context: dict = None) -> UnderstoodQuery:
        """
        深度查询理解
        """
        # 1. 基础分析
        intent = await self.intent_classifier.classify(query)
        entities = await self.entity_extractor.extract(query)
        sentiment = await self.sentiment_analyzer.analyze(query)
        
        # 2. 时间分析
        temporal_info = await self.temporal_parser.parse(query)
        
        # 3. 上下文整合
        if context:
            query = self._integrate_context(query, context)
        
        # 4. 构建理解结果
        understood = UnderstoodQuery(
            original_text=query,
            intent=intent,
            entities=entities,
            sentiment=sentiment,
            temporal_info=temporal_info,
            
            # 派生属性
            is_complex=self._is_complex_query(intent, entities),
            requires_keyword_expansion=self._requires_expansion(intent, entities),
            memory_type_preferences=self._determine_memory_preferences(intent),
            filters=self._build_filters(entities, temporal_info)
        )
        
        return understood
    
    def _determine_memory_preferences(self, intent: QueryIntent) -> List[MemoryType]:
        """
        根据查询意图确定记忆类型偏好
        """
        preferences = []
        
        if intent.type == IntentType.FACT_LOOKUP:
            preferences.extend([MemoryType.SEMANTIC, MemoryType.EXTERNAL])
        
        elif intent.type == IntentType.PROCEDURAL:
            preferences.extend([MemoryType.PROCEDURAL, MemoryType.EPISODIC])
        
        elif intent.type == IntentType.CONVERSATIONAL:
            preferences.extend([MemoryType.EPISODIC, MemoryType.WORKING])
        
        elif intent.type == IntentType.ANALYTICAL:
            preferences.extend([MemoryType.SEMANTIC, MemoryType.EXTERNAL, MemoryType.EPISODIC])
        
        # 确保至少有一种记忆类型
        if not preferences:
            preferences = list(MemoryType)
        
        return preferences
```

## 7. 监控和优化系统

### 7.1 监控指标定义

```python
@dataclass
class MemoryMetrics:
    """记忆系统监控指标"""
    
    # 检索指标
    retrieval_latency: Dict[str, float]  # p50, p95, p99
    retrieval_hit_rate: Dict[MemoryType, float]
    retrieval_recall: Dict[str, float]
    
    # 存储指标
    storage_utilization: Dict[MemoryType, float]
    storage_latency: Dict[MemoryType, float]
    compression_ratio: Dict[MemoryType, float]
    
    # 质量指标
    answer_quality: float
    citation_accuracy: float
    user_satisfaction: float
    
    # 系统指标
    memory_consolidation_frequency: int
    memory_evolution_count: int
    error_rate: float
    
    @classmethod
    def from_monitoring_data(cls, data: Dict) -> 'MemoryMetrics':
        """从监控数据构建指标"""
        return cls(
            retrieval_latency=data.get('retrieval_latency', {}),
            retrieval_hit_rate=data.get('retrieval_hit_rate', {}),
            retrieval_recall=data.get('retrieval_recall', {}),
            storage_utilization=data.get('storage_utilization', {}),
            storage_latency=data.get('storage_latency', {}),
            compression_ratio=data.get('compression_ratio', {}),
            answer_quality=data.get('answer_quality', 0.0),
            citation_accuracy=data.get('citation_accuracy', 0.0),
            user_satisfaction=data.get('user_satisfaction', 0.0),
            memory_consolidation_frequency=data.get('memory_consolidation_frequency', 0),
            memory_evolution_count=data.get('memory_evolution_count', 0),
            error_rate=data.get('error_rate', 0.0)
        )
```

### 7.2 监控收集器

```python
class MemoryMetricsCollector:
    """记忆指标收集器"""
    
    def __init__(self):
        self.metrics_store = MetricsStore()
        self.alert_manager = AlertManager()
        
        # 监控配置
        self.thresholds = {
            'retrieval_latency_p95': 500,  # ms
            'retrieval_hit_rate': 0.7,     # 70%
            'storage_utilization': 0.8,    # 80%
            'error_rate': 0.05,            # 5%
            'answer_quality': 0.6          # 60%
        }
    
    def record_store(self, record: MemoryRecord):
        """记录存储操作"""
        self.metrics_store.record_metric(
            metric_type='store',
            memory_type=record.memory_type,
            latency=record.store_latency,
            size=record.size,
            timestamp=record.timestamp
        )
        
        # 检查阈值
        self._check_thresholds('store_latency', record.store_latency)
    
    def record_retrieve(self, 
                       query: str, 
                       returned_count: int, 
                       total_count: int):
        """记录检索操作"""
        recall = returned_count / total_count if total_count > 0 else 0
        
        self.metrics_store.record_metric(
            metric_type='retrieve',
            query_length=len(query),
            returned_count=returned_count,
            total_count=total_count,
            recall=recall,
            timestamp=datetime.now()
        )
        
        # 检查阈值
        self._check_thresholds('retrieval_recall', recall)
    
    def _check_thresholds(self, metric_name: str, value: float):
        """检查指标是否超过阈值"""
        threshold = self.thresholds.get(metric_name)
        if threshold and value > threshold:
            self.alert_manager.trigger_alert(
                alert_type='threshold_exceeded',
                metric=metric_name,
                value=value,
                threshold=threshold,
                timestamp=datetime.now()
            )
    
    async def generate_report(self, 
                             time_range: TimeRange = None) -> MetricsReport:
        """生成监控报告"""
        if not time_range:
            time_range = TimeRange(
                start=datetime.now() - timedelta(hours=24),
                end=datetime.now()
            )
        
        # 收集指标数据
        metrics_data = await self.metrics_store.query_metrics(time_range)
        
        # 计算聚合指标
        aggregated = self._aggregate_metrics(metrics_data)
        
        # 生成报告
        report = MetricsReport(
            time_range=time_range,
            metrics=MemoryMetrics.from_monitoring_data(aggregated),
            trends=self._calculate_trends(metrics_data),
            recommendations=self._generate_recommendations(aggregated),
            alerts=self.alert_manager.get_alerts(time_range)
        )
        
        return report
```

### 7.3 优化策略

```python
class MemoryOptimizationStrategy:
    """记忆优化策略"""
    
    def __init__(self, metrics_collector: MemoryMetricsCollector):
        self.metrics_collector = metrics_collector
        self.optimization_history = []
    
    async def optimize(self) -> OptimizationResult:
        """执行优化"""
        # 1. 分析当前性能
        report = await self.metrics_collector.generate_report()
        
        # 2. 识别优化机会
        opportunities = self._identify_optimization_opportunities(report)
        
        # 3. 优先级排序
        prioritized = self._prioritize_opportunities(opportunities)
        
        # 4. 执行优化
        results = []
        for opportunity in prioritized[:5]:  # 每次最多执行5个优化
            try:
                result = await self._execute_optimization(opportunity)
                results.append(result)
                
                # 记录优化历史
                self.optimization_history.append({
                    'timestamp': datetime.now(),
                    'opportunity': opportunity,
                    'result': result
                })
                
            except Exception as e:
                results.append(OptimizationResult(
                    success=False,
                    opportunity=opportunity,
                    error=str(e)
                ))
        
        # 5. 评估优化效果
        overall_result = self._evaluate_optimization_results(results)
        
        return overall_result
    
    def _identify_optimization_opportunities(self, 
                                           report: MetricsReport) -> List[OptimizationOpportunity]:
        """识别优化机会"""
        opportunities = []
        
        # 基于延迟的优化
        for memory_type, latency in report.metrics.retrieval_latency.items():
            if latency > 300:  # 超过300ms
                opportunities.append(
                    OptimizationOpportunity(
                        type=OptimizationType.LATENCY,
                        memory_type=memory_type,
                        severity='high' if latency > 500 else 'medium',
                        description=f"{memory_type}检索延迟过高: {latency}ms",
                        suggested_action=f"优化{memory_type}索引或增加缓存"
                    )
                )
        
        # 基于命中率的优化
        for memory_type, hit_rate in report.metrics.retrieval_hit_rate.items():
            if hit_rate < 0.6:  # 低于60%
                opportunities.append(
                    OptimizationOpportunity(
                        type=OptimizationType.HIT_RATE,
                        memory_type=memory_type,
                        severity='high' if hit_rate < 0.4 else 'medium',
                        description=f"{memory_type}命中率过低: {hit_rate*100:.1f}%",
                        suggested_action=f"优化{memory_type}查询策略或增加数据覆盖"
                    )
                )
        
        # 基于存储利用率的优化
        for memory_type, utilization in report.metrics.storage_utilization.items():
            if utilization > 0.8:  # 超过80%
                opportunities.append(
                    OptimizationOpportunity(
                        type=OptimizationType.STORAGE,
                        memory_type=memory_type,
                        severity='high' if utilization > 0.9 else 'medium',
                        description=f"{memory_type}存储利用率过高: {utilization*100:.1f}%",
                        suggested_action=f"清理{memory_type}过期数据或扩容存储"
                    )
                )
        
        return opportunities
```

## 8. 部署架构

### 8.1 基础设施要求

```yaml
# infrastructure.yaml
infrastructure:
  # 数据库层
  databases:
    redis:
      version: "7.2"
      mode: "cluster"
      nodes: 3
      memory_per_node: "4GB"
      persistence: "aof-every-sec"
    
    mysql:
      version: "8.0"
      engine: "InnoDB"
      storage: "100GB"
      backup: "daily"
      read_replicas: 2
    
    elasticsearch:
      version: "8.12"
      nodes: 3
      memory_per_node: "8GB"
      storage_per_node: "100GB"
    
    qdrant:
      version: "1.7.0"
      nodes: 3
      memory_per_node: "16GB"
      storage_per_node: "200GB"
  
  # 应用层
  application:
    memory_orchestrator:
      replicas: 3
      resources:
        cpu: "2"
        memory: "4Gi"
      
    rag_service:
      replicas: 2
      resources:
        cpu: "4"
        memory: "8Gi"
      
    monitoring:
      prometheus:
        enabled: true
        retention: "30d"
      
      grafana:
        enabled: true
        dashboards:
          - memory_metrics
          - retrieval_performance
          - storage_utilization
  
  # 网络层
  networking:
    service_mesh: "istio"
    load_balancer: "nginx"
    internal_tls: true
    
  # 安全层
  security:
    encryption:
      at_rest: true
      in_transit: true
      
    access_control:
      rbac: true
      audit_logging: true
      
    backup:
      frequency: "daily"
      retention: "30d"
      encryption: true
```

### 8.2 容量规划

```python
@dataclass
class CapacityPlanning:
    """容量规划计算"""
    
    # 用户规模假设
    active_users: int = 1000
    daily_conversations_per_user: int = 10
    avg_conversation_length: int = 10  # 消息数
    
    # 存储需求计算
    def calculate_storage_requirements(self) -> Dict[str, StorageRequirement]:
        """计算各层存储需求"""
        
        # 每日数据量估算
        daily_messages = self.active_users * self.daily_conversations_per_user * self.avg_conversation_length
        daily_storage_mb = daily_messages * 2  # 假设每条消息2KB
        
        requirements = {}
        
        # 工作记忆
        requirements['working_memory'] = StorageRequirement(
            daily_growth_mb=daily_storage_mb * 0.1,  # 10%进入工作记忆
            retention_days=1,
            estimated_size_mb=daily_storage_mb * 0.1 * 2,  # 2天容量
            recommended_config={
                'redis_memory': '4GB',
                'maxmemory_policy': 'allkeys-lru'
            }
        )
        
        # 情景记忆
        requirements['episodic_memory'] = StorageRequirement(
            daily_growth_mb=daily_storage_mb * 0.3,  # 30%进入情景记忆
            retention_days=365,
            estimated_size_mb=daily_storage_mb * 0.3 * 365 / 1024,  # 转换为GB
            recommended_config={
                'mysql_storage': '100GB',
                'partitioning': 'monthly',
                'archive_after_days': 90
            }
        )
        
        # 语义记忆
        requirements['semantic_memory'] = StorageRequirement(
            daily_growth_mb=100,  # 假设每日新增100MB知识
            retention_days=365,
            estimated_size_mb=100 * 365 / 1024,  # 转换为GB
            recommended_config={
                'elasticsearch_storage': '50GB',
                'shards': 3,
                'replicas': 1
            }
        )
        
        # 外部记忆
        requirements['external_memory'] = StorageRequirement(
            daily_growth_mb=500,  # 假设每日新增500MB文档
            retention_days=180,
            estimated_size_mb=500 * 180 / 1024,  # 转换为GB
            recommended_config={
                'qdrant_storage': '200GB',
                'vector_dimension': 768,
                'hnsw_m': 16
            }
        )
        
        return requirements
    
    def calculate_performance_requirements(self) -> PerformanceRequirement:
        """计算性能需求"""
        # 峰值QPS估算
        peak_concurrent_users = self.active_users * 0.1  # 10%并发
        avg_requests_per_minute = 5  # 每分钟5个请求
        
        peak_qps = (peak_concurrent_users * avg_requests_per_minute) / 60
        
        return PerformanceRequirement(
            peak_qps=peak_qps,
            p95_latency_ms=500,
            availability=0.999,  # 99.9%
            error_rate=0.01,     # 1%
            recommended_scaling={
                'min_replicas': 2,
                'max_replicas': 10,
                'target_cpu_utilization': 70,
                'target_memory_utilization': 80
            }
        )
```

现在让我完成文档的最后部分：

<｜DSML｜function_calls>
<｜DSML｜invoke name="write">
<｜DSML｜parameter name="path" string="true">/root/.openclaw/workspace/agent-memory-architecture-summary.md