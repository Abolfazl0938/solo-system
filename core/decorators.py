import time
from functools import wraps
from typing import Any, Callable


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
        print("[TEST] Exception caught successfully in caller scope.")
