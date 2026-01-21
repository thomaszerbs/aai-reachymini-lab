from reachy_mini import ReachyMini  
from reachy_mini.motion.recorded_move import RecordedMoves  
  
with ReachyMini() as mini:  
    # 加载舞蹈库  
    dances = RecordedMoves("pollen-robotics/reachy-mini-dances-library")  
    print("可用舞蹈:", dances.list_moves())  
      
    # 加载表情库  
    emotions = RecordedMoves("pollen-robotics/reachy-mini-emotions-library")  
    print("可用表情:", emotions.list_moves())  
      
    # 播放一个舞蹈  
    mini.play_move(dances.get("dance_name"), initial_goto_duration=1.0)  
      
    # 播放一个表情  
    mini.play_move(emotions.get("happy"), initial_goto_duration=1.0)