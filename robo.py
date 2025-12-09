# 필요한 라이브러리 불러오기
from robolink import * # RoboDK API
from robodk import * # 로봇 툴박스

# 1. RoboDK 연결 및 초기화
RDK = Robolink()

# 2. 아이템 불러오기 (이미지의 트리 구조 이름과 일치시킴)
# 로봇 이름: Doosan Robotics M1013 White
robot = RDK.Item('Doosan Robotics M1013 White')

# 좌표계 및 툴
frame = RDK.Item('Frame 2')
tool = RDK.Item('OnRobot Gecko SP1 Single')

# 타겟 (이미지에 설정된 PICK, PLACE 타겟 사용)
target_pick = RDK.Item('PICK')
target_place = RDK.Item('PLACE')

# 이동할 물체 (박스)
box = RDK.Item('Box 12x10in (Closed)')

# 3. 설정 변수 (요구사항: 안전 고려 이동 궤적 설계)
# 충돌 방지를 위해 물체 바로 위 100mm 지점을 경유점(Approach)으로 설정
approach_dist = 100  # 100mm

# 4. 함수 정의: Pick and Place 루틴
def PickAndPlace():
    # 타겟의 위치(Pose) 정보 가져오기
    pose_pick = target_pick.Pose()
    pose_place = target_place.Pose()
    
    # -------------------------------------------------
    # [PICK 동작]
    # -------------------------------------------------
    # 1) 접근 (Approach): 물체 상공으로 이동 (충돌 방지)
    # pose_pick * transl(0,0, -approach_dist) -> Z축 방향으로 후퇴된 위치 계산
    robot.MoveJ(pose_pick * transl(0, 0, -approach_dist))
    
    # 2) 집기 위치로 이동
    robot.MoveL(target_pick) # 정밀한 접근을 위해 선형 이동(MoveL) 권장
    
    # 3) 그리퍼 동작 (시뮬레이션: 물체 부착)
    # 실제 그리퍼라면 tool.RunInstruction('Close') 등을 사용
    tool.AttachClosest() 
    RDK.ShowMessage("물체 집기(Pick)", False)
    
    # 4) 들어 올리기 (Retract): 다시 상공으로 이동
    robot.MoveL(pose_pick * transl(0, 0, -approach_dist))
    
    # -------------------------------------------------
    # [PLACE 동작]
    # -------------------------------------------------
    # 5) 놓을 위치 상공으로 이동 (안전 궤적)
    robot.MoveJ(pose_place * transl(0, 0, -approach_dist))
    
    # 6) 놓을 위치로 이동
    robot.MoveL(target_place)
    
    # 7) 그리퍼 동작 (시뮬레이션: 물체 분리)
    tool.DetachAll()
    RDK.ShowMessage("물체 놓기(Place)", False)
    
    # 8) 복귀 (Retract): 상공으로 이동
    robot.MoveL(pose_place * transl(0, 0, -approach_dist))

# 5. 메인 실행 루프 (요구사항: Loop / Wait 흐름 제어)
# 예시: 작업을 3회 반복
LOOP_COUNT = 3

# 로봇 기준 좌표계 설정
robot.setPoseFrame(frame)
robot.setPoseTool(tool)

# 시뮬레이션 속도 조절 (너무 빠르면 확인이 어려움)
RDK.setSimulationSpeed(1)

for i in range(LOOP_COUNT):
    print(f"작업 횟수: {i+1}/{LOOP_COUNT}")
    RDK.ShowMessage(f"작업 시작: {i+1}회차", False)
    
    # Pick & Place 실행
    PickAndPlace()
    
    # 상자 원위치 (시뮬레이션 반복을 위해 박스를 다시 PICK 위치로 강제 이동시키는 코드)
    # 실제 로봇에서는 필요 없으나 시뮬레이션 연속성을 위해 추가
    if i < LOOP_COUNT - 1:
        box.setPose(target_pick.Pose()) 
        RDK.ShowMessage("다음 작업을 위해 대기 중...", False)
        
        # 요구사항: Wait (2초 대기)
        RDK.Pause(2000) 

RDK.ShowMessage("모든 작업 완료", False)