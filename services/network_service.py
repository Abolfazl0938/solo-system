import asyncio
from typing import List, Dict, Any


class NetworkService:
    async def fetch_gate_data(self, gate_id: str, delay: float) -> Dict[str, Any]:
        """Simulate fetching gate status from central hunters association server."""
        await asyncio.sleep(delay)
        return {
            "gate_id": gate_id,
            "status": f"Gate {gate_id} scan completed (delay: {delay}s)",
            "is_active": True,
        }

    async def scan_all_gates(self, gates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Concurrent asynchronous scanning of multiple gates."""
        tasks = []
        for idx, g in enumerate(gates, start=1):
            tasks.append(self.fetch_gate_data(g["id"], delay=idx * 0.5))
        return await asyncio.gather(*tasks)
