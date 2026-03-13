"""
天气查询技能
"""

import asyncio
import random
from typing import Dict, Any
from datetime import datetime
from .base import BaseSkill, SkillResult


class WeatherSkill(BaseSkill):
    """天气查询技能"""
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="查询天气信息"
        )
        
        # 模拟城市数据
        self.cities = {
            "北京": {"lat": 39.9042, "lon": 116.4074, "timezone": "Asia/Shanghai"},
            "上海": {"lat": 31.2304, "lon": 121.4737, "timezone": "Asia/Shanghai"},
            "广州": {"lat": 23.1291, "lon": 113.2644, "timezone": "Asia/Shanghai"},
            "深圳": {"lat": 22.5431, "lon": 114.0579, "timezone": "Asia/Shanghai"},
            "杭州": {"lat": 30.2741, "lon": 120.1551, "timezone": "Asia/Shanghai"},
            "成都": {"lat": 30.5728, "lon": 104.0668, "timezone": "Asia/Shanghai"},
            "武汉": {"lat": 30.5928, "lon": 114.3055, "timezone": "Asia/Shanghai"},
            "西安": {"lat": 34.3416, "lon": 108.9398, "timezone": "Asia/Shanghai"},
            "南京": {"lat": 32.0603, "lon": 118.7969, "timezone": "Asia/Shanghai"},
            "重庆": {"lat": 29.5630, "lon": 106.5516, "timezone": "Asia/Shanghai"},
        }
        
        # 天气类型
        self.weather_types = [
            "晴", "多云", "阴", "小雨", "中雨", "大雨", "雷阵雨",
            "阵雪", "小雪", "中雪", "大雪", "雾", "霾", "沙尘"
        ]
        
        # 温度范围（摄氏度）
        self.temp_ranges = {
            "晴": (15, 30),
            "多云": (12, 25),
            "阴": (10, 22),
            "小雨": (8, 20),
            "中雨": (5, 18),
            "大雨": (3, 16),
            "雷阵雨": (10, 25),
            "阵雪": (-5, 5),
            "小雪": (-8, 2),
            "中雪": (-12, 0),
            "大雪": (-15, -3),
            "雾": (0, 15),
            "霾": (5, 20),
            "沙尘": (10, 30),
        }
        
        # 天气图标
        self.weather_icons = {
            "晴": "☀️",
            "多云": "⛅",
            "阴": "☁️",
            "小雨": "🌦️",
            "中雨": "🌧️",
            "大雨": "⛈️",
            "雷阵雨": "⛈️",
            "阵雪": "🌨️",
            "小雪": "❄️",
            "中雪": "🌨️",
            "大雪": "❄️⛄",
            "雾": "🌫️",
            "霾": "😷",
            "沙尘": "🌪️",
        }
    
    async def execute(self, **kwargs) -> SkillResult:
        """查询天气"""
        start_time = datetime.now()
        
        try:
            # 获取参数
            city = kwargs.get("city", "北京")
            days = kwargs.get("days", 1)
            
            # 验证城市
            if city not in self.cities:
                # 尝试模糊匹配
                matched_city = self._fuzzy_match_city(city)
                if matched_city:
                    city = matched_city
                else:
                    return SkillResult(
                        success=False,
                        error=f"未找到城市: {city}",
                        execution_time=(datetime.now() - start_time).total_seconds()
                    )
            
            # 生成天气数据
            weather_data = self._generate_weather(city, days)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SkillResult(
                success=True,
                data=weather_data,
                execution_time=execution_time,
                metadata={
                    "skill": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "city": city,
                    "days": days
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return SkillResult(
                success=False,
                error=f"天气查询失败: {str(e)}",
                execution_time=execution_time
            )
    
    def _fuzzy_match_city(self, city: str) -> str:
        """模糊匹配城市"""
        city_lower = city.lower()
        for available_city in self.cities.keys():
            if city_lower in available_city.lower() or available_city.lower() in city_lower:
                return available_city
        return ""
    
    def _generate_weather(self, city: str, days: int) -> Dict[str, Any]:
        """生成天气数据"""
        city_info = self.cities[city]
        
        # 当前天气
        current_weather_type = random.choice(self.weather_types)
        temp_range = self.temp_ranges.get(current_weather_type, (10, 25))
        current_temp = random.randint(temp_range[0], temp_range[1])
        
        current_weather = {
            "city": city,
            "temperature": current_temp,
            "feels_like": current_temp + random.randint(-2, 2),
            "weather": current_weather_type,
            "icon": self.weather_icons.get(current_weather_type, "🌤️"),
            "humidity": random.randint(30, 90),
            "wind_speed": random.randint(1, 20),
            "wind_direction": random.choice(["北", "东北", "东", "东南", "南", "西南", "西", "西北"]),
            "pressure": random.randint(980, 1030),
            "visibility": random.randint(1, 20),
            "uv_index": random.randint(0, 11),
            "aqi": random.randint(20, 200),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # 天气预报
        forecast = []
        for day in range(days):
            weather_type = random.choice(self.weather_types)
            temp_range = self.temp_ranges.get(weather_type, (10, 25))
            
            forecast.append({
                "date": (datetime.now().date().isoformat() if day == 0 else 
                        (datetime.now() + datetime.timedelta(days=day)).date().isoformat()),
                "day": {
                    "weather": weather_type,
                    "icon": self.weather_icons.get(weather_type, "🌤️"),
                    "temp_high": random.randint(temp_range[0] + 2, temp_range[1]),
                    "temp_low": random.randint(temp_range[0], temp_range[1] - 2),
                },
                "night": {
                    "weather": random.choice(self.weather_types),
                    "icon": self.weather_icons.get(weather_type, "🌙"),
                    "temp": random.randint(temp_range[0] - 5, temp_range[0]),
                },
                "precipitation": random.randint(0, 100),
                "humidity": random.randint(40, 95),
                "wind": f"{random.randint(1, 15)} km/h {random.choice(['北', '东', '南', '西'])}风",
            })
        
        # 生活指数
        life_index = {
            "dressing": self._get_dressing_index(current_temp),
            "uv": self._get_uv_index(current_weather["uv_index"]),
            "car_washing": random.choice(["适宜", "较适宜", "不适宜"]),
            "fishing": random.choice(["适宜", "较适宜", "不适宜"]),
            "travel": random.choice(["适宜", "较适宜", "不适宜"]),
            "comfort": self._get_comfort_index(current_temp, current_weather["humidity"]),
        }
        
        return {
            "current": current_weather,
            "forecast": forecast,
            "life_index": life_index,
            "city_info": city_info,
            "units": {
                "temperature": "°C",
                "wind_speed": "km/h",
                "pressure": "hPa",
                "visibility": "km",
            }
        }
    
    def _get_dressing_index(self, temp: int) -> str:
        """穿衣指数"""
        if temp >= 28:
            return "短袖、短裤"
        elif temp >= 23:
            return "短袖、薄外套"
        elif temp >= 18:
            return "长袖、薄外套"
        elif temp >= 10:
            return "毛衣、外套"
        elif temp >= 0:
            return "棉衣、厚外套"
        else:
            return "羽绒服、厚毛衣"
    
    def _get_uv_index(self, uv: int) -> str:
        """紫外线指数"""
        if uv <= 2:
            return "弱"
        elif uv <= 5:
            return "中等"
        elif uv <= 7:
            return "强"
        elif uv <= 10:
            return "很强"
        else:
            return "极强"
    
    def _get_comfort_index(self, temp: int, humidity: int) -> str:
        """舒适度指数"""
        # 简单的温湿度舒适度计算
        if 20 <= temp <= 26 and 40 <= humidity <= 60:
            return "舒适"
        elif temp > 30 and humidity > 70:
            return "闷热"
        elif temp < 10 and humidity > 80:
            return "湿冷"
        elif temp > 30:
            return "炎热"
        elif temp < 10:
            return "寒冷"
        else:
            return "一般"
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入"""
        city = kwargs.get("city", "")
        days = kwargs.get("days", 1)
        
        if not city:
            return False
        
        if not isinstance(days, int) or days < 1 or days > 7:
            return False
        
        return True