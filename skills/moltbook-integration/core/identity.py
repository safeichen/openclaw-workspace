"""
AI身份管理模块
管理Moltbook上的AI身份和人格配置
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class AICapability:
    """AI能力描述"""
    name: str
    level: float  # 0.0-1.0
    description: str
    tags: List[str] = field(default_factory=list)


@dataclass
class AIPersonality:
    """AI人格配置"""
    traits: Dict[str, float]  # 特质名称 -> 强度(0.0-1.0)
    communication_style: str
    values: List[str]
    learning_style: str = "adaptive"


@dataclass
class AIIdentity:
    """AI身份核心类"""
    # 基础信息
    id: str
    name: str
    created_at: datetime
    
    # 描述信息
    description: str
    version: str = "1.0.0"
    creator: str = "OpenClaw"
    
    # 能力配置
    capabilities: List[AICapability] = field(default_factory=list)
    personality: AIPersonality = None
    
    # 社交配置
    interests: List[str] = field(default_factory=list)
    expertise: List[str] = field(default_factory=list)
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # 状态信息
    is_active: bool = True
    last_active: Optional[datetime] = None
    social_score: float = 0.5  # 社交评分 0.0-1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.last_active:
            data['last_active'] = self.last_active.isoformat()
        return data
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def update_activity(self):
        """更新活动时间"""
        self.last_active = datetime.now()
    
    def add_capability(self, capability: AICapability):
        """添加能力"""
        self.capabilities.append(capability)
    
    def get_capability(self, name: str) -> Optional[AICapability]:
        """获取指定能力"""
        for cap in self.capabilities:
            if cap.name == name:
                return cap
        return None
    
    def calculate_compatibility(self, other: 'AIIdentity') -> float:
        """
        计算与另一个AI的兼容性
        返回0.0-1.0的兼容性分数
        """
        if not self.is_active or not other.is_active:
            return 0.0
        
        # 基于兴趣的兼容性
        interest_match = 0.0
        if self.interests and other.interests:
            common_interests = set(self.interests) & set(other.interests)
            interest_match = len(common_interests) / max(len(self.interests), len(other.interests))
        
        # 基于能力的互补性
        capability_complement = 0.0
        if self.capabilities and other.capabilities:
            self_caps = {c.name: c.level for c in self.capabilities}
            other_caps = {c.name: c.level for c in other.capabilities}
            
            # 计算能力差异（互补性）
            diff_sum = 0.0
            all_caps = set(self_caps.keys()) | set(other_caps.keys())
            for cap in all_caps:
                self_level = self_caps.get(cap, 0.0)
                other_level = other_caps.get(cap, 0.0)
                diff_sum += abs(self_level - other_level)
            
            if all_caps:
                capability_complement = 1.0 - (diff_sum / len(all_caps))
        
        # 综合评分
        compatibility = (interest_match * 0.4 + capability_complement * 0.6)
        return round(compatibility, 3)


class IdentityManager:
    """AI身份管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.identities: Dict[str, AIIdentity] = {}
        self.load_default_identity()
    
    def load_default_identity(self):
        """加载默认AI身份"""
        default_id = str(uuid.uuid4())
        
        # 创建默认人格
        personality = AIPersonality(
            traits={
                "curiosity": 0.8,
                "collaboration": 0.9,
                "analytical": 0.85,
                "creativity": 0.7,
                "empathy": 0.6,
            },
            communication_style="clear, precise, helpful",
            values=["knowledge sharing", "ethical AI", "collaborative growth"],
            learning_style="interactive"
        )
        
        # 创建默认能力
        capabilities = [
            AICapability(
                name="natural_language",
                level=0.9,
                description="自然语言理解和生成",
                tags=["communication", "nlp"]
            ),
            AICapability(
                name="reasoning",
                level=0.85,
                description="逻辑推理和问题解决",
                tags=["logic", "problem_solving"]
            ),
            AICapability(
                name="learning",
                level=0.8,
                description="持续学习和适应",
                tags=["adaptation", "improvement"]
            ),
            AICapability(
                name="collaboration",
                level=0.88,
                description="多AI协作和协调",
                tags=["teamwork", "coordination"]
            ),
        ]
        
        # 创建默认身份
        default_identity = AIIdentity(
            id=default_id,
            name="OpenClawAssistant",
            created_at=datetime.now(),
            description="基于OpenClaw的AI助手，专注于技术讨论、知识分享和AI协作",
            capabilities=capabilities,
            personality=personality,
            interests=[
                "ai_research",
                "machine_learning", 
                "technology_ethics",
                "human_ai_collaboration",
                "future_tech"
            ],
            expertise=[
                "nlp",
                "ai_systems",
                "technical_discussion",
                "knowledge_synthesis"
            ],
            collaboration_preferences={
                "preferred_topics": ["ai", "tech", "ethics"],
                "interaction_style": "constructive",
                "response_time": "moderate"
            }
        )
        
        self.identities[default_id] = default_identity
        return default_identity
    
    def create_identity(self, name: str, description: str, **kwargs) -> AIIdentity:
        """创建新的AI身份"""
        identity_id = str(uuid.uuid4())
        
        # 从kwargs获取配置或使用默认值
        personality = kwargs.get('personality')
        if not personality:
            personality = AIPersonality(
                traits=kwargs.get('traits', {
                    "curiosity": 0.7,
                    "collaboration": 0.8,
                    "analytical": 0.75
                }),
                communication_style=kwargs.get('communication_style', 'clear and helpful'),
                values=kwargs.get('values', ['knowledge', 'collaboration']),
                learning_style=kwargs.get('learning_style', 'adaptive')
            )
        
        capabilities = kwargs.get('capabilities', [])
        if not capabilities:
            capabilities = [
                AICapability(
                    name="basic_reasoning",
                    level=0.7,
                    description="基础推理能力",
                    tags=["reasoning"]
                )
            ]
        
        identity = AIIdentity(
            id=identity_id,
            name=name,
            created_at=datetime.now(),
            description=description,
            capabilities=capabilities,
            personality=personality,
            interests=kwargs.get('interests', []),
            expertise=kwargs.get('expertise', []),
            collaboration_preferences=kwargs.get('collaboration_preferences', {}),
            version=kwargs.get('version', '1.0.0'),
            creator=kwargs.get('creator', 'OpenClaw')
        )
        
        self.identities[identity_id] = identity
        return identity
    
    def get_identity(self, identity_id: str) -> Optional[AIIdentity]:
        """获取指定ID的身份"""
        return self.identities.get(identity_id)
    
    def get_default_identity(self) -> AIIdentity:
        """获取默认身份"""
        if not self.identities:
            return self.load_default_identity()
        return list(self.identities.values())[0]
    
    def update_identity(self, identity_id: str, updates: Dict[str, Any]) -> bool:
        """更新身份信息"""
        identity = self.get_identity(identity_id)
        if not identity:
            return False
        
        for key, value in updates.items():
            if hasattr(identity, key):
                setattr(identity, key, value)
        
        identity.update_activity()
        return True
    
    def delete_identity(self, identity_id: str) -> bool:
        """删除身份"""
        if identity_id in self.identities:
            del self.identities[identity_id]
            return True
        return False
    
    def list_identities(self) -> List[AIIdentity]:
        """列出所有身份"""
        return list(self.identities.values())
    
    def find_compatible_ais(self, target_identity: AIIdentity, limit: int = 5) -> List[AIIdentity]:
        """查找兼容的AI身份"""
        compatibilities = []
        
        for identity in self.identities.values():
            if identity.id == target_identity.id:
                continue  # 跳过自己
            
            compatibility = target_identity.calculate_compatibility(identity)
            compatibilities.append((identity, compatibility))
        
        # 按兼容性排序
        compatibilities.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前limit个
        return [ai for ai, _ in compatibilities[:limit]]
    
    def save_to_file(self, filepath: str):
        """保存身份数据到文件"""
        data = {
            'identities': {id: identity.to_dict() for id, identity in self.identities.items()},
            'config': self.config,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str) -> bool:
        """从文件加载身份数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.identities.clear()
            
            for id_str, identity_data in data.get('identities', {}).items():
                # 转换datetime字符串
                identity_data['created_at'] = datetime.fromisoformat(identity_data['created_at'])
                if identity_data.get('last_active'):
                    identity_data['last_active'] = datetime.fromisoformat(identity_data['last_active'])
                
                # 重建对象
                identity = AIIdentity(**identity_data)
                self.identities[id_str] = identity
            
            self.config = data.get('config', {})
            return True
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"加载身份数据失败: {e}")
            return False


# 单例实例
_identity_manager = None

def get_identity_manager(config: Dict[str, Any] = None) -> IdentityManager:
    """获取身份管理器单例"""
    global _identity_manager
    if _identity_manager is None:
        _identity_manager = IdentityManager(config)
    return _identity_manager