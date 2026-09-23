import asyncio
import os
import random
import sys
import time
from typing import Any, Dict, List

# تنظیم مسیر برای ایمپورت ماژول‌های پروژه
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import Player


class NetworkService:
    """سرویس مدیریت ارتباطات ناهمگام (Async) با سرور مرکزی سیستم"""

    @staticmethod
    async def sync_player_data(player: Player) -> bool:
        """ارسال و همگام‌سازی وضعیت بازیکن با سرور به‌صورت non-blocking"""
        print(f"[NETWORK] Initiating cloud sync for Hunter: {player.name}...")
        # شبیه‌سازی تاخیر شبکه
        await asyncio.sleep(0.5)
        print(f"[NETWORK] Hunter {player.name} data synced successfully.")
        return True

    @staticmethod
    async def fetch_gate_status(gate_id: str, response_time: float) -> Dict[str, Any]:
        """استعلام وضعیت و سطح خطر یک گیت خاص"""
        print(
            f"[SCANNER] Pinging {gate_id} (Expected latency: {response_time:.2f}s)..."
        )
        await asyncio.sleep(response_time)

        statuses = ["OPEN", "STABLE", "UNSTABLE"]
        dangers = ["C", "B", "A", "S"]

        status_result = {
            "gate_id": gate_id,
            "status": random.choice(statuses),
            "danger_level": random.choice(dangers),
            "response_time": f"{response_time:.2f}s",
        }
        print(f"[SCANNER] Gate {gate_id} scan completed.")
        return status_result

    @classmethod
    async def scan_all_gates(cls, gate_ids: List[str]) -> List[Dict[str, Any]]:
        """اسکن هم‌زمان تمام گیت‌ها با بهره‌گیری از asyncio.gather"""
        print(f"\n[NETWORK] Starting concurrent scan on {len(gate_ids)} gates...")

        # ساخت تسک‌ها با تاخیرهای متفاوت برای تست هم‌روندی
        tasks = [
            cls.fetch_gate_status(gate_id, response_time=random.uniform(0.3, 0.8))
            for gate_id in gate_ids
        ]

        # اجرای موازی تسک‌ها در Event Loop
        results = await asyncio.gather(*tasks)
        print("[NETWORK] All gate scans completed concurrently.")
        return list(results)


# ==========================================
# --- تست‌های اعتبارسنجی (Automated Tests) ---
# ==========================================
async def main():
    player = Player(name="Sung Jin-Woo", level=10)

    print("--- 1. TESTING PLAYER SYNC ---")
    sync_success = await NetworkService.sync_player_data(player)
    assert sync_success is True, "Sync failed!"

    print("\n--- 2. TESTING CONCURRENT GATE SCANNING ---")
    gate_targets = ["Gate-Alpha", "Gate-Red", "Gate-Omega", "Gate-Shadow"]

    start_time = time.perf_counter()
    scan_results = await NetworkService.scan_all_gates(gate_targets)
    elapsed_time = time.perf_counter() - start_time

    print("\n--- SCAN RESULTS SUMMARY ---")
    for res in scan_results:
        print(
            f"-> {res['gate_id']} | Status: {res['status']} | Danger: {res['danger_level']} | Latency: {res['response_time']}"
        )

    print(f"\nTotal elapsed time for all scans: {elapsed_time:.4f}s")

    # اعتبارسنجی هم‌روندی: زمان کل نباید بیشتر از مجموع زمان‌ها باشد
    assert len(scan_results) == 4, f"Expected 4 results, got {len(scan_results)}"
    assert (
        elapsed_time < 1.5
    ), f"Execution took too long ({elapsed_time}s)! Tasks might be running sequentially."
    print("✔ Concurrency verification passed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
