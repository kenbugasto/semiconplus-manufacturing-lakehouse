from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GeneratorConfig:
    """Configuration for the synthetic manufacturing-data generator."""

    start_date: date = date(2021, 1, 1)
    end_date: date = date(2025, 12, 31)
    random_seed: int = 42

    product_group_count: int = 6
    devices_per_product_group: int = 5
    site_count: int = 3
    equipment_per_site: int = 8

    average_lots_per_day: int = 10
    units_per_lot: int = 10
    equipment_events_per_day: int = 140
    streaming_event_count: int = 30_000

    duplicate_rate: float = 0.005
    null_key_rate: float = 0.002
    malformed_rate: float = 0.002
    late_event_rate: float = 0.01
    unknown_reference_rate: float = 0.003

    output_root: str = (
        "/Volumes/semiconplus_portfolio/landing/test_data/development"
    )


DEV_CONFIG = GeneratorConfig()


SMOKE_CONFIG = GeneratorConfig(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 3),
    average_lots_per_day=2,
    units_per_lot=3,
    equipment_events_per_day=10,
    streaming_event_count=50,
    output_root="/Volumes/semiconplus_portfolio/landing/test_data/smoke",
)