"""CLI runner for demo scenarios.

Usage: python -m app.simulation.run [scenario_name]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.database.session import SessionLocal
from app.simulation.scenarios import SCENARIOS, run_scenario


def main() -> None:
    scenario = sys.argv[1] if len(sys.argv) > 1 else "brute_force"
    if scenario not in SCENARIOS:
        print(f"Unknown scenario. Available: {', '.join(SCENARIOS)}")
        sys.exit(1)
    db = SessionLocal()
    try:
        result = run_scenario(db, scenario)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
