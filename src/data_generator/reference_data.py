from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ProductGroup:
    product_group_id: str
    product_group_name: str
    business_unit: str
    restricted: bool


@dataclass(frozen=True)
class Device:
    device_id: str
    device_name: str
    product_group_id: str
    package_type: str
    target_yield: float
    lifecycle_status: str


@dataclass(frozen=True)
class Site:
    site_id: str
    site_name: str
    country: str
    timezone: str


@dataclass(frozen=True)
class Equipment:
    equipment_id: str
    site_id: str
    equipment_model: str
    equipment_type: str
    rated_units_per_hour: int


PRODUCT_GROUPS = [
    ProductGroup("PG01", "Power Management", "Automotive", True),
    ProductGroup("PG02", "High Precision Analog", "Industrial", True),
    ProductGroup("PG03", "Connectivity", "Consumer", False),
    ProductGroup("PG04", "Embedded Processing", "Industrial", False),
    ProductGroup("PG05", "Sensor Products", "Automotive", True),
    ProductGroup("PG06", "Standard Logic", "Consumer", False),
]

SITES = [
    Site("SITE01", "Kaohsiung Assembly and Test", "Taiwan", "Asia/Taipei"),
    Site("SITE02", "Clark Assembly and Test", "Philippines", "Asia/Manila"),
    Site("SITE03", "Dallas Test Operations", "USA", "America/Chicago"),
]

PACKAGE_TYPES = ["QFN", "BGA", "TSSOP", "SOIC", "WLCSP"]
LIFECYCLE_STATUSES = ["NPI", "RAMP", "MASS_PRODUCTION", "MATURE"]
EQUIPMENT_MODELS = ["TST-A100", "TST-A200", "TST-B150", "TST-C300"]
DEFECT_CODES = [
    "PASS",
    "OPEN_SHORT",
    "LEAKAGE",
    "FUNCTIONAL",
    "TIMING",
    "CONTACT",
    "HANDLER_JAM",
    "UNKNOWN",
]

EQUIPMENT_EVENT_TYPES = [
    "RUN",
    "IDLE",
    "SETUP",
    "PLANNED_DOWNTIME",
    "UNPLANNED_DOWNTIME",
    "ALARM",
    "MAINTENANCE",
]


def build_devices() -> list[Device]:
    devices: list[Device] = []

    for product_group_index, product_group in enumerate(PRODUCT_GROUPS, start=1):
        for device_index in range(1, 6):
            device_number = ((product_group_index - 1) * 5) + device_index

            devices.append(
                Device(
                    device_id=f"DV{device_number:03d}",
                    device_name=f"SEMICONPLUS-DV{device_number:03d}",
                    product_group_id=product_group.product_group_id,
                    package_type=PACKAGE_TYPES[
                        (device_number - 1) % len(PACKAGE_TYPES)
                    ],
                    target_yield=round(
                        0.91 + ((device_number % 7) * 0.01),
                        4,
                    ),
                    lifecycle_status=LIFECYCLE_STATUSES[
                        (device_number - 1) % len(LIFECYCLE_STATUSES)
                    ],
                )
            )

    return devices


def build_equipment() -> list[Equipment]:
    equipment: list[Equipment] = []

    for site in SITES:
        for equipment_index in range(1, 9):
            equipment.append(
                Equipment(
                    equipment_id=f"{site.site_id}-EQ{equipment_index:03d}",
                    site_id=site.site_id,
                    equipment_model=EQUIPMENT_MODELS[
                        (equipment_index - 1) % len(EQUIPMENT_MODELS)
                    ],
                    equipment_type="FINAL_TESTER",
                    rated_units_per_hour=(
                        420 + (equipment_index * 35)
                    ),
                )
            )

    return equipment


def records(items: list[object]) -> list[dict]:
    return [asdict(item) for item in items]