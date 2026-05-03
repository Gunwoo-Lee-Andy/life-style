import os
import time
import subprocess
import json
from pathlib import Path

# --- 오토리서치 설정 ---
LOOP_INTERVAL = 60 * 10  # 10분마다 루프
TRACK = "A" # "A": 콘텐츠 기획 최적화, "B": 코드 최적화

def run_command(cmd):
    """터미널 명령어 실행 유틸리티"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def current_git_hash():
    out, err = run_command("git rev-parse HEAD")
    return out

def revert_changes():
    """실패 시 이전 상태로 되돌리기"""
    print("[Karpathy Loop] 평가 실패: 변경 사항을 롤백(Revert)합니다.")
    run_command("git reset --hard HEAD")
    run_command("git clean -fd")

def commit_changes(score, msg):
    """성공 시 변경 사항 확정"""
    print(f"[Karpathy Loop] 평가 성공! (점수: {score}) 변경 사항을 커밋합니다.")
    run_command("git add .")
    run_command(f'git commit -m "[AutoResearch] {msg} (Score: {score})"')

def evaluate_fitness(track_type):
    """
    LLM as a Judge (Business 에이전트 역할) 또는 PyTest 실행
    - 반환값: (점수, 피드백)
    """
    if track_type == "B":
        # 트랙 B: 코드 테스트 결과가 기준점
        out, err = run_command("pytest _agents/youtube/tools/")
        if "failed" not in out.lower() and "error" not in err.lower():
            return 100, "All tests passed"
        return 0, err
    
    elif track_type == "A":
        # 트랙 A: Business 에이전트가 예상 ROI 점수 산정 (현재는 더미 로직, 이후 LLM 연동)
        # TODO: Business API를 호출하여 생성된 hook_library.md의 최근 항목 점수 채점
        return 85, "Good hook, but lacks emotional trigger."
        
    return 0, "Unknown track"

def propose_mutation(track_type):
    """
    Writer(콘텐츠) 또는 Developer(코드)에게 변경안(Diff) 제안을 요청 (LLM 연동 포인트)
    """
    print(f"[Karpathy Loop] 새로운 가설(Mutation)을 제안합니다. (Track: {track_type})")
    if track_type == "A":
        # 예시: Writer가 hook_library.md에 새로운 아이디어를 덧붙임
        hook_path = Path("../../_shared/hook_library.md")
        if not hook_path.exists():
            hook_path.touch()
        with open(hook_path, "a") as f:
            f.write(f"\n- [New Hook] {time.time()} - 감동적인 3D 프린팅의 순간\n")
        return "콘텐츠 아이디어 추가"
        
    elif track_type == "B":
        # 예시: 코드를 변경
        return "코드 리팩토링 시도"

def run_loop():
    print("🚀 Karpathy AutoResearch Loop Started...")
    
    while True:
        print("\n--- 새로운 이터레이션 시작 ---")
        # 1. 초기 상태 기록
        start_hash = current_git_hash()
        
        # 2. 가설 제안 및 적용 (Propose & Execute)
        mutation_msg = propose_mutation(TRACK)
        
        # 3. 평가 (Evaluate)
        score, feedback = evaluate_fitness(TRACK)
        print(f"평가 점수: {score}/100")
        
        # 4. 결정 (Commit or Revert)
        # 기준선(Threshold) 설정. 예: 80점 이상이면 통과
        THRESHOLD = 80
        
        if score >= THRESHOLD:
            commit_changes(score, mutation_msg)
        else:
            print(f"[Karpathy Loop] 피드백: {feedback}")
            revert_changes()
            
        print(f"다음 루프까지 대기... ({LOOP_INTERVAL}초)")
        time.sleep(LOOP_INTERVAL)

if __name__ == "__main__":
    # 무인 서버나 심야 시간에 이 스크립트 실행
    # run_loop()
    print("AutoResearch script initialized. Uncomment run_loop() to start.")
