from reachy_mini import ReachyMini
from reachy_mini.motion.recorded_move import RecordedMoves

with ReachyMini() as mini:
    recorded_moves = RecordedMoves("pollen-robotics/reachy-mini-dances-library")
    print(recorded_moves.list_moves())

    for move_name in recorded_moves.list_moves():
        print(f"Playing move: {move_name}")
        mini.play_move(recorded_moves.get(move_name), initial_goto_duration=1.0)