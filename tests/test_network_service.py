import asyncio
from services.network_service import NetworkService


def test_network_scan_all_gates():
    async def _run_test():
        service = NetworkService()
        gates = [{"id": "G-1"}, {"id": "G-2"}]
        results = await service.scan_all_gates(gates)
        return results

    results = asyncio.run(_run_test())

    assert len(results) == 2
    assert results[0]["gate_id"] == "G-1"
    assert results[1]["gate_id"] == "G-2"
    assert results[0]["is_active"] is True
