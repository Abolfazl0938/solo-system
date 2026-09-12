import time
from functools import wraps
from typing import Any, Callable
from exceptions import InsufficientRankError

RANK_ORDER = {
    "E": 1,
    "D": 2,
    "C": 3,
    "B": 4,
    "A": 5,
    "S": 6,
}


def system_logger(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"[SYSTEM] Action triggered: {func.__name__} | Args: {args} {kwargs}")
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed = (end_time - start_time) * 1000
            print(f"[SYSTEM] Action {func.__name__} completed in {elapsed:.4f} ms")
            return result
        except Exception as e:
            print(f"[SYSTEM ERROR] Action {func.__name__} failed with error: {e}")
            raise e

    return wrapper


def require_rank(min_rank: Any):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # متدی که این دکوراتور روش می‌شیند متد کلاسه، پس args[0] همون self (آبجکت بازیکن) است
            player = args[0]

            player_rank_val = (
                player.rank.value if hasattr(player.rank, "value") else str(player.rank)
            )
            required_rank_val = (
                min_rank.value if hasattr(min_rank, "value") else str(min_rank)
            )

            # بررسی شرط: آیا رنک بازیکن کمتر از رنک مورد نیازه؟
            if RANK_ORDER.get(player_rank_val, 0) < RANK_ORDER.get(
                required_rank_val, 0
            ):
                raise InsufficientRankError(
                    f"Access Denied: Player rank '{player_rank_val}' is lower than required '{required_rank_val}'."
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    print("--- TEST 1: Normal Execution ---")

    @system_logger
    def simulate_dungeon_clear(hunter_name: str, exp_gain: int) -> str:
        time.sleep(0.05)
        return f"{hunter_name} gained {exp_gain} EXP!"

    msg = simulate_dungeon_clear("Sung Jinwoo", 500)
    print(f"Output: {msg}\n")

    print("--- TEST 2: Error Handling ---")

    @system_logger
    def trigger_system_penalty(reason: str):
        raise ValueError(f"Penalty triggered: {reason}")

    try:
        trigger_system_penalty("Missed daily quest")
    except ValueError:
        print("[TEST] Exception caught successfully in caller scope.\n")

    print("--- TEST 3: Parameterized Decorator (@require_rank) ---")

    # ساخت یک کلاس موقت برای تست شبیه‌سازی بازیکن
    class MockPlayer:

        def __init__(self, name: str, rank: str):
            self.name = name
            self.rank = rank

        @require_rank("B")
        def enter_red_gate(self):
            return f"Welcome Hunter {self.name}, Red Gate unlocked!"

    low_rank_hunter = MockPlayer("Jinwoo (Beginner)", "E")
    high_rank_hunter = MockPlayer("Jinwoo (Awakened)", "S")

    # تست دسترسی نامعتبر
    try:
        low_rank_hunter.enter_red_gate()
    except InsufficientRankError as e:
        print(f"[TEST 3.1 SUCCESS] Blocked weak player: {e}")

    # تست دسترسی معتبر
    success_msg = high_rank_hunter.enter_red_gate()
    print(f"[TEST 3.2 SUCCESS] {success_msg}")
