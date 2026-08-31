def get_system_status() -> dict[str, str]:
    report = {
        "system_name": "solo leveling system",
        "version": "1.0.0",
        "status": "Active",
    }
    return report


def calculate_next_level_exp(current_level: int) -> int:
    return current_level * 100
