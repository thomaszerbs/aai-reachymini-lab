# Desktop app roadmap

## Phase A — stable booth app (approved starting point)

Goal: replace the notebook as the operator UI, without introducing flaky booth behavior.

Planned work:
- Single main window desktop app
- Mode selector for Piper / Edge / vision / demo
- Piper model dropdown populated from the repo models folder
- Edge voice dropdown populated from known voice names
- Persistent prompt editor
- Always-visible chat transcript and input field
- Optional microphone toggle
- Always-on demo mode with safe idle motion + periodic speaking
- Clear startup and error states when connect/backends are unavailable

Acceptance criteria:
- starts cleanly from the repo root
- no notebook rerun needed between changes
- model and voice can be selected from the UI
- demo mode can be turned on and off reliably
- chat still works even when the robot is offline or unavailable

## Phase B — heavier immersive demo (trigger after Phase A passes)

Goal: upgrade from steady booth demo to a more animated, camera-aware showpiece after the base app is stable.

Planned work:
- add lightweight face/object detection loop with a lower frame rate and lower CPU usage
- trigger only short, timed attention reactions instead of a constant heavy inference loop
- keep a separate toggle for active camera reaction vs idle motion mode
- add better status indicators for camera stream, model health, and demo cycle timing
- tune the app to avoid flapping or overloading the robot when many events fire at once

Acceptance criteria:
- demo remains stable for long periods
- active reaction only triggers in short cycles with a clear stop path
- camera detection does not block chat or the main operator controls

## Implementation order

1. Window shell and control layout
2. model/voice selection wiring
3. prompt editor + chat message loop
4. safe demo mode
5. validation and stability pass
6. move to Phase B enhancements if the app remains stable
