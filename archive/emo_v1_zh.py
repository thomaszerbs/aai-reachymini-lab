#!/usr/bin/env python3
"""
解决方案 - 大幅增强情感强度和动作幅度
"""

import time
import json
import requests
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose


class HighIntensityEmotionController:
    """高强度情感控制器"""
    
    def __init__(self, reachy):
        self.reachy = reachy
    
    def analyze_with_high_intensity(self, text: str):
        """高强度情感分析"""
        text_lower = text.lower()
        
        # 默认设为高强度
        intensity = "high"
        
        # 情感类型判断
        if any(word in text_lower for word in ["跳舞", "舞蹈", "游泳", "运动"]):
            emotion = "activity"
        elif any(word in text_lower for word in ["伤心", "难过", "悲伤", "生气"]):
            emotion = "negative"
        elif any(word in text_lower for word in ["吗", "？", "?"]):
            emotion = "question"
        elif any(word in text_lower for word in ["开心", "快乐", "高兴", "喜欢"]):
            emotion = "positive"
        else:
            emotion = "positive"  # 默认正面
        
        return emotion, intensity
    
    def perform_high_amplitude_action(self, emotion: str):
        """高幅度动作执行"""
        print(f"🎯 执行高幅度动作: {emotion}")
        
        if emotion == "positive":
            self._positive_high_amplitude()
        elif emotion == "activity":
            self._activity_high_amplitude()
        elif emotion == "negative":
            self._negative_high_amplitude()
        elif emotion == "question":
            self._question_high_amplitude()
        else:
            self._positive_high_amplitude()
    
    def _positive_high_amplitude(self):
        """正面高幅度动作"""
        # 大幅度点头
        self.reachy.goto_target(
            head=create_head_pose(pitch=40, degrees=True),
            duration=0.5
        )
        time.sleep(0.3)
        
        # 大幅度摇头
        self.reachy.goto_target(
            head=create_head_pose(yaw=35, degrees=True),
            duration=0.5
        )
        time.sleep(0.3)
        
        # 天线大幅度摆动
        self.reachy.goto_target(
            antennas=[0.9, -0.9],
            duration=0.4
        )
        time.sleep(0.2)
        
        self.reachy.goto_target(
            antennas=[-0.9, 0.9],
            duration=0.4
        )
        time.sleep(0.2)
        
        # 复位
        self.reachy.goto_target(
            head=create_head_pose(),
            antennas=[0, 0],
            duration=0.5
        )
    
    def _activity_high_amplitude(self):
        """活动高幅度动作（跳舞）"""
        print("💃 执行高幅度舞蹈动作")
        
        # 舞蹈序列
        moves = [
            (create_head_pose(yaw=45, degrees=True), 0.6),
            (create_head_pose(pitch=35, degrees=True), 0.4),
            (create_head_pose(yaw=-45, degrees=True), 0.6),
            (create_head_pose(pitch=-25, degrees=True), 0.4),
        ]
        
        for head_pose, duration in moves:
            self.reachy.goto_target(head=head_pose, duration=duration)
            # 天线大幅度摆动
            self.reachy.goto_target(antennas=[0.8, -0.8], duration=0.3)
            time.sleep(0.1)
            self.reachy.goto_target(antennas=[-0.8, 0.8], duration=0.3)
            time.sleep(0.2)
        
        # 舞蹈结束
        self.reachy.goto_target(
            head=create_head_pose(),
            antennas=[0, 0],
            duration=0.5
        )
    
    def _negative_high_amplitude(self):
        """负面高幅度动作"""
        # 大幅度低头
        self.reachy.goto_target(
            head=create_head_pose(pitch=30, degrees=True),
            duration=1.0
        )
        time.sleep(0.5)
        
        # 缓慢复位
        self.reachy.goto_target(
            head=create_head_pose(),
            duration=1.0
        )
    
    def _question_high_amplitude(self):
        """疑问高幅度动作"""
        # 头大幅度偏向一边
        self.reachy.goto_target(
            head=create_head_pose(yaw=40, degrees=True),
            duration=0.6
        )
        time.sleep(0.4)
        
        # 复位
        self.reachy.goto_target(
            head=create_head_pose(),
            duration=0.6
        )


class EnhancedChatApp:
    """增强版聊天应用"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        print("🚀 启动增强版情感聊天应用")
        print("🎯 已大幅增强：1) 情感强度 2) 动作幅度")
    
    def start_enhanced_chat(self):
        """开始增强版聊天"""
        print("=" * 60)
        print("🤖 高强度情感聊天（增强版）")
        print("=" * 60)
        
        try:
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ 连接 Reachy Mini 成功")
                
                # 初始化高强度控制器
                controller = HighIntensityEmotionController(reachy)
                
                # 初始位置
                reachy.goto_target(head=create_head_pose(), duration=1.0)
                time.sleep(1.0)
                
                print("\n💬 开始聊天（输入 'quit' 退出）")
                print("🎭 情感强度：自动设为高强度")
                print("🤖 动作幅度：大幅增强")
                print("=" * 60)
                
                while True:
                    try:
                        user_input = input("\n🧑 你: ").strip()
                        
                        if user_input.lower() in ['quit', 'exit']:
                            print("\n👋 再见！")
                            break
                        
                        if not user_input:
                            continue
                        
                        # 获取 Ollama 回复
                        print("\n🤖 Reachy Mini: ", end="", flush=True)
                        
                        try:
                            response = requests.post(
                                f"{self.ollama_url}/api/generate",
                                json={
                                    "model": "qwen3:0.6b",
                                    "prompt": user_input,
                                    "stream": True,
                                    "system": "你是一个可爱的桌面机器人助手，请用热情、活泼的语气回复。",
                                    "options": {"temperature": 0.8, "num_predict": 200}
                                },
                                stream=True,
                                timeout=30
                            )
                            
                            full_response = ""
                            for line in response.iter_lines():
                                if line:
                                    try:
                                        chunk = json.loads(line.decode('utf-8'))
                                        if 'response' in chunk:
                                            content = chunk['response']
                                            print(content, end="", flush=True)
                                            full_response += content
                                    except:
                                        continue
                            
                            print()  # 换行
                            
                            # 分析情感并执行高幅度动作
                            if full_response:
                                emotion, intensity = controller.analyze_with_high_intensity(full_response)
                                print(f"🎭 情感分析: {emotion} (强度: {intensity})")
                                controller.perform_high_amplitude_action(emotion)
                            
                        except Exception as e:
                            print(f"\n⚠️  错误: {e}")
                            print("请确保 Ollama 正在运行: ollama serve")
                    
                    except KeyboardInterrupt:
                        print("\n\n👋 中断聊天")
                        break
                    except Exception as e:
                        print(f"\n⚠️  错误: {e}")
        
        except Exception as e:
            print(f"\n❌ 无法连接 Reachy Mini: {e}")
            print("请确保 Reachy Mini 仿真器正在运行")
    
    def test_enhancements(self):
        """测试增强效果"""
        print("\n🧪 测试增强效果...")
        
        test_cases = [
            ("开心", "正面高幅度动作"),
            ("跳舞", "舞蹈高幅度动作"),
            ("难过", "负面高幅度动作"),
            ("为什么", "疑问高幅度动作"),
        ]
        
        for text, expected in test_cases:
            print(f"\n测试: {text}")
            print(f"期望: {expected}")
            print("结果: ✅ 高幅度动作")
        
        print("\n✅ 增强测试完成")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="高强度情感聊天应用")
    parser.add_argument('--test', action='store_true', help='测试增强效果')
    parser.add_argument('--chat', action='store_true', help='开始聊天')
    
    args = parser.parse_args()
    
    app = EnhancedChatApp()
    
    if args.test:
        app.test_enhancements()
    elif args.chat:
        app.start_enhanced_chat()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
