# 情感驱动的 Reachy Mini Ollama 聊天系统

## 🌟 简介

这个系统让 Reachy Mini 的表情和动作能够随着 Ollama 回复的情感内容自动变化。通过分析文本中的情感关键词、表情符号和语气强度，系统会匹配相应的机器人动作，使互动更加自然和富有表现力。

## 🚀 快速开始

### 1. 运行增强版情感聊天应用
```bash
python emo_v1.py
```

### 2. 测试增强效果
```bash
python emo_v1.py --test
```

### 3. 检查 Ollama 连接
```bash
python check_ollama.py
```

## 🎯 核心功能（增强版）

### 1. **高强度情感分析引擎**
- **大幅增强强度判断**: 默认高强度，关键词权重大幅提升
- **情感类型**: 正面(positive)、负面(negative)、疑问(question)、活动(activity)
- **情感强度**: 高(high)为主，大幅减少低强度判断
- **自动强度提升**: 文本较长或有表情符号时自动提升强度

### 2. **大幅增强的情感-动作映射系统**
```python
# emo_v1.py 中的增强动作映射
emotion_actions = {
    'positive': '高幅度正面动作 - 大幅度点头、大幅度摇头、天线大幅度摆动',
    'negative': '高幅度负面动作 - 大幅度低头、缓慢复位',
    'question': '高幅度疑问动作 - 头大幅度偏向一边',
    'activity': '高幅度活动动作 - 舞蹈序列、大幅度旋转、天线大幅度摆动'
}
```

### 3. **大幅增强的动作幅度系统**
- **高强度**: 动作幅度增加100-150%（幅度1.5-1.8）
- **中强度**: 动作幅度增加80-100%（幅度1.2-1.5）
- **大幅动作**: 所有动作幅度至少增加50%
- **持续时间**: 适当增加动作持续时间（2.5-3.0秒）

## 📊 情感关键词库

### 正面情感关键词
- **高兴**: 开心、快乐、愉快、高兴、喜欢、爱
- **友善**: 谢谢、感谢、请、你好、欢迎、帮助
- **鼓励**: 加油、努力、坚持、相信、一定、很棒
- **惊讶**: 哇、天啊、真的吗、不可思议、太神奇了

### 负面情感关键词
- **悲伤**: 伤心、难过、悲伤、失望、遗憾、抱歉
- **愤怒**: 生气、愤怒、讨厌、烦人、可恶、恨
- **担心**: 担心、忧虑、害怕、恐惧、紧张、不安
- **否定**: 不、不能、不会、没有、不行、错误

### 表情符号映射
- **正面**: 😊😄😍👍🥰😎🎉❤️
- **负面**: 😢😭😡👎😔😞😤💔
- **思考疑问**: 🤔❓⁉️💭🧐🔍

## 🤖 动作映射示例

### 高兴 😄 (高强度)
```python
动作: 快速点头、天线活泼摆动、轻微摇头（开心）、快速复位
幅度: 0.8 (大)
速度: 快
持续时间: 0.5秒/动作
```

### 悲伤 😢 (中强度)
```python
动作: 中等低头、缓慢摇头、天线微垂
幅度: 0.5 (中等)
速度: 慢
持续时间: 1.5秒/动作
```

### 疑问 🤔 (低强度)
```python
动作: 头轻微偏斜、天线轻微摆动、缓慢复位
幅度: 0.3 (小)
速度: 慢
持续时间: 1.5秒/动作
```

## 🔧 技术架构

```
文本输入
    ↓
情感分析引擎
    ├── 关键词匹配
    ├── 表情符号识别
    ├── 语气强度判断
    └── 情感类型分类
    ↓
情感映射系统
    ├── 情感类型 → 动作模式
    ├── 情感强度 → 动作参数
    └── 置信度评估
    ↓
机器人动作执行
    ├── 头部控制 (pitch/yaw)
    ├── 天线控制 (左右摆动)
    └── 时间控制 (duration)
```

## 💻 使用方法（增强版）

### 方法1: 运行完整增强版聊天
```bash
# 启动增强版情感聊天
python emo_v1.py

# 或带参数启动
python emo_v1.py --chat
```

### 方法2: 直接使用增强版控制器
```python
from emo_v1 import HighIntensityEmotionController

with ReachyMini(media_backend="no_media") as reachy:
    controller = HighIntensityEmotionController(reachy)
    
    # 分析文本情感（增强版）
    text = "跳舞时间到了！💃"
    emotion_type, intensity = controller.analyze_with_high_intensity(text)
    print(f"情感: {emotion_type}, 强度: {intensity}")
    
    # 执行高幅度动作
    controller.perform_high_amplitude_action(emotion_type)
```

### 方法3: 使用增强版聊天应用类
```python
from emo_v1 import EnhancedChatApp

app = EnhancedChatApp()
app.start_enhanced_chat()  # 启动高强度交互式聊天
```

### 方法4: 测试增强效果
```bash
# 测试情感强度和动作幅度增强效果
python emo_v1.py --test
```

## 📝 自定义扩展

### 1. 添加新的情感关键词
```python
# 在 EmotionAnalyzer 类中添加
self.emotion_patterns['positive']['keywords'].extend([
    '新关键词1', '新关键词2', '新关键词3'
])
```

### 2. 添加新的动作模式
```python
# 在 EmotionDrivenController 类中添加
def custom_action(self, duration: float, params: Dict):
    """自定义动作"""
    amplitude = params['amplitude']
    # 实现你的自定义动作逻辑
    self.reachy.goto_target(
        head=create_head_pose(pitch=20*amplitude, degrees=True),
        duration=duration/2
    )

# 添加到动作映射
self.emotion_actions['custom'] = self.custom_action
```

### 3. 调整强度参数
```python
# 修改强度参数映射
self.intensity_params = {
    'high': {'amplitude': 1.0, 'speed': 0.5, 'frequency': 1.0},
    'medium': {'amplitude': 0.7, 'speed': 1.0, 'frequency': 0.7},
    'low': {'amplitude': 0.4, 'speed': 1.5, 'frequency': 0.4}
}
```

## 🧪 测试方法

### 1. 单元测试
```bash
# 测试情感分析准确性
python -c "
from test_emotion_analysis import EmotionAnalyzer
analyzer = EmotionAnalyzer()
test_cases = [
    ('我非常开心！', ('positive', 'high')),
    ('有点难过...', ('negative', 'low')),
    ('你怎么看？', ('question', 'medium'))
]
for text, expected in test_cases:
    result = analyzer.analyze_emotion(text)
    print(f'{text}: {result} (预期: {expected})')
"
```

### 2. 集成测试
```bash
# 测试完整的情感驱动系统
python emotion_actions.py --test
```

### 3. 手动测试
```bash
# 交互式测试情感分析
python test_emotion_analysis.py
```

## 🔍 工作原理详解

### 1. 情感分析流程
```
1. 文本预处理: 转换为小写，去除特殊字符
2. 关键词匹配: 扫描预定义的情感关键词
3. 表情符号识别: 识别 Unicode 表情符号
4. 语气强度分析: 通过修饰词判断情感强度
5. 情感分类: 根据得分确定主导情感
6. 置信度计算: 计算情感分析的可靠程度
```

### 2. 动作映射流程
```
1. 情感类型选择: 根据分析结果选择动作模式
2. 强度参数调整: 根据强度级别调整动作参数
3. 动作序列生成: 生成一系列连贯的机器人动作
4. 动作执行: 通过 Reachy Mini SDK 控制机器人
5. 反馈调整: 根据执行效果微调参数
```

## 🛠️ 故障排除

### 常见问题1: 情感分析不准确
**解决方案**:
1. 添加更多相关关键词到情感词库
2. 调整关键词权重
3. 增加表情符号识别

### 常见问题2: 机器人动作不自然
**解决方案**:
1. 调整动作持续时间参数
2. 优化动作序列的连贯性
3. 增加动作之间的延迟

### 常见问题3: 系统响应慢
**解决方案**:
1. 优化关键词匹配算法
2. 减少不必要的正则表达式匹配
3. 使用缓存机制

## 📈 性能优化建议

### 1. 算法优化
```python
# 使用集合进行快速关键词匹配
keywords_set = set(self.positive_words + self.negative_words)
matched_words = keywords_set.intersection(set(text_words))
```

### 2. 缓存优化
```python
# 缓存情感分析结果
from functools import lru_cache

@lru_cache(maxsize=1000)
def analyze_emotion_cached(text: str) -> Dict:
    return self.analyze_emotion(text)
```

### 3. 并行处理
```python
# 使用多线程进行情感分析
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    futures = [executor.submit(analyzer.analyze_emotion, text) 
               for text in text_list]
    results = [f.result() for f in futures]
```

## 🤝 贡献指南

### 1. 添加新的情感类型
1. 在 `emotion_patterns` 字典中添加新的情感类型
2. 定义对应的关键词和表情符号
3. 实现对应的动作函数
4. 更新动作映射

### 2. 改进情感分析算法
1. 研究更先进的情感分析技术
2. 集成机器学习模型
3. 优化关键词权重系统

### 3. 扩展动作库
1. 研究 Reachy Mini 的更多动作可能性
2. 创建更复杂的动作序列
3. 实现动作的组合和串联

## 📚 参考资料

### 相关项目
- [Reachy Mini SDK](https://github.com/pollen-robotics/reachy_mini)
- [Ollama](https://github.com/ollama/ollama)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

### 情感分析算法
- 基于关键词的情感分析
- 表情符号情感映射
- 语气强度识别

### 机器人动作控制
- 逆运动学控制
- 轨迹规划
- 动作时序控制

## 📄 许可证

本项目基于 MIT 许可证开源。详见 LICENSE 文件。

## 🙏 致谢

感谢以下项目和技术的支持：
- Reachy Mini 机器人平台
- Ollama 本地大语言模型
- OpenAI 兼容 API
- Python 开源社区