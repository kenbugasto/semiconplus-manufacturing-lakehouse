from __future__ import annotations

import csv
import json
import random
from collections import defaultdict
from dataclasses import asdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

from .config import GeneratorConfig
from .reference_data import (
    DEFECT_CODES,
    EQUIPMENT_EVENT_TYPES,
    PRODUCT_GROUPS,
    SITES,
    build_devices,
    build_equipment,
    records,
)


class ManufacturingDataGenerator:
    """Generate deterministic synthetic semiconductor manufacturing data."""

    def __init__(self, config: GeneratorConfig) -> None:
        self.config = config
        self.random = random.Random(config.random_seed)
        self.output_root = Path(config.output_root)

        self.devices = build_devices()
        self.equipment = build_equipment()

        self.devices_by_id = {
            device.device_id: device for device in self.devices
        }
        self.equipment_by_site: dict[str, list[Any]] = defaultdict(list)

        for equipment in self.equipment:
            self.equipment_by_site[equipment.site_id].append(equipment)

        self.manifest: dict[str, Any] = {
            "project": "SemiconPlus Manufacturing Lakehouse",
            "generator_version": "1.0.0",
            "random_seed": config.random_seed,
            "start_date": config.start_date.isoformat(),
            "end_date": config.end_date.isoformat(),
            "generated_at_utc": None,
            "record_counts": defaultdict(int),
            "files": [],
        }

        self.expected_errors: list[dict[str, Any]] = []

    def prepare_directories(self) -> None:
        directories = [
            "reference",
            "batch/production_lots",
            "batch/equipment_events",
            "batch/unit_test_results",
            "batch/tester_logs",
            "streaming/tester_events",
            "binary",
            "manifests",
        ]

        for directory in directories:
            (self.output_root / directory).mkdir(
                parents=True,
                exist_ok=True,
            )

    def _register_file(
        self,
        file_path: Path,
        record_type: str,
        record_count: int,
    ) -> None:
        self.manifest["files"].append(
            {
                "relative_path": str(
                    file_path.relative_to(self.output_root)
                ),
                "record_type": record_type,
                "record_count": record_count,
                "size_bytes": file_path.stat().st_size,
            }
        )
        self.manifest["record_counts"][record_type] += record_count

    def _write_csv(
        self,
        file_path: Path,
        rows: list[dict[str, Any]],
        delimiter: str = ",",
    ) -> None:
        if not rows:
            return

        with file_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as output_file:
            writer = csv.DictWriter(
                output_file,
                fieldnames=list(rows[0].keys()),
                delimiter=delimiter,
            )
            writer.writeheader()
            writer.writerows(rows)

    def generate_reference_data(self) -> None:
        reference_files = {
            "product_groups": records(PRODUCT_GROUPS),
            "devices": records(self.devices),
            "sites": records(SITES),
            "equipment": records(self.equipment),
        }

        for name, rows in reference_files.items():
            file_path = self.output_root / "reference" / f"{name}.csv"
            self._write_csv(file_path, rows)
            self._register_file(file_path, name, len(rows))

    def _date_range(self) -> list[date]:
        number_of_days = (
            self.config.end_date - self.config.start_date
        ).days + 1

        return [
            self.config.start_date + timedelta(days=offset)
            for offset in range(number_of_days)
        ]

    def _random_timestamp(self, production_date: date) -> datetime:
        seconds = self.random.randint(0, 86_399)

        return datetime.combine(
            production_date,
            time.min,
            tzinfo=timezone.utc,
        ) + timedelta(seconds=seconds)

    def _monthly_key(self, production_date: date) -> str:
        return production_date.strftime("%Y_%m")

    def _select_defect_code(self, passed: bool) -> str:
        if passed:
            return "PASS"

        failure_codes = [
            code
            for code in DEFECT_CODES
            if code not in {"PASS", "UNKNOWN"}
        ]
        return self.random.choice(failure_codes)

    def generate_batch_data(self) -> None:
        monthly_lots: dict[str, list[dict[str, Any]]] = defaultdict(list)
        monthly_results: dict[str, list[dict[str, Any]]] = defaultdict(list)
        monthly_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
        monthly_logs: dict[str, list[str]] = defaultdict(list)

        lot_sequence = 1
        test_sequence = 1
        event_sequence = 1

        for production_date in self._date_range():
            month_key = self._monthly_key(production_date)

            daily_lot_count = max(
                1,
                self.config.average_lots_per_day
                + self.random.randint(-2, 2),
            )

            for _ in range(daily_lot_count):
                device = self.random.choice(self.devices)
                site = self.random.choice(SITES)
                equipment = self.random.choice(
                    self.equipment_by_site[site.site_id]
                )

                lot_id = f"LOT{production_date:%Y%m%d}{lot_sequence:06d}"
                start_timestamp = self._random_timestamp(production_date)
                quantity_started = self.random.randint(700, 1_500)

                seasonal_adjustment = (
                    0.015
                    if production_date.month in {3, 6, 9, 12}
                    else 0.0
                )
                random_variation = self.random.uniform(-0.035, 0.02)

                actual_yield = min(
                    0.999,
                    max(
                        0.75,
                        device.target_yield
                        + seasonal_adjustment
                        + random_variation,
                    ),
                )

                quantity_passed = round(
                    quantity_started * actual_yield
                )
                quantity_failed = quantity_started - quantity_passed

                lot_row = {
                    "lot_id": lot_id,
                    "production_date": production_date.isoformat(),
                    "device_id": device.device_id,
                    "product_group_id": device.product_group_id,
                    "site_id": site.site_id,
                    "equipment_id": equipment.equipment_id,
                    "start_timestamp_utc": start_timestamp.isoformat(),
                    "quantity_started": quantity_started,
                    "quantity_passed": quantity_passed,
                    "quantity_failed": quantity_failed,
                    "actual_yield": round(actual_yield, 6),
                    "test_program_revision": (
                        f"REV{self.random.randint(1, 5):02d}"
                    ),
                    "source_system": "MES_BATCH",
                }
                monthly_lots[month_key].append(lot_row)

                for unit_number in range(
                    1,
                    self.config.units_per_lot + 1,
                ):
                    passed = (
                        self.random.random() <= actual_yield
                    )
                    defect_code = self._select_defect_code(passed)

                    result_row = {
                        "test_result_id": f"TR{test_sequence:010d}",
                        "lot": {
                            "lot_id": lot_id,
                            "unit_sequence": unit_number,
                        },
                        "product": {
                            "device_id": device.device_id,
                            "product_group_id": device.product_group_id,
                        },
                        "test_context": {
                            "site_id": site.site_id,
                            "equipment_id": equipment.equipment_id,
                            "program_revision": (
                                lot_row["test_program_revision"]
                            ),
                        },
                        "result": {
                            "status": "PASS" if passed else "FAIL",
                            "defect_code": defect_code,
                            "test_time_seconds": round(
                                self.random.uniform(8.0, 38.0),
                                3,
                            ),
                        },
                        "event_timestamp_utc": (
                            start_timestamp
                            + timedelta(seconds=unit_number * 45)
                        ).isoformat(),
                    }
                    monthly_results[month_key].append(result_row)
                    test_sequence += 1

                monthly_logs[month_key].append(
                    (
                        f"{start_timestamp.isoformat()} "
                        f"INFO lot={lot_id} "
                        f"device={device.device_id} "
                        f"equipment={equipment.equipment_id} "
                        f"started={quantity_started} "
                        f"passed={quantity_passed} "
                        f"failed={quantity_failed}"
                    )
                )

                lot_sequence += 1

            for _ in range(self.config.equipment_events_per_day):
                site = self.random.choice(SITES)
                equipment = self.random.choice(
                    self.equipment_by_site[site.site_id]
                )
                event_timestamp = self._random_timestamp(production_date)
                event_type = self.random.choices(
                    EQUIPMENT_EVENT_TYPES,
                    weights=[55, 15, 8, 5, 8, 6, 3],
                    k=1,
                )[0]

                duration_seconds = self.random.randint(30, 3_600)

                event_row = {
                    "event_id": f"EV{event_sequence:012d}",
                    "event_timestamp_utc": event_timestamp.isoformat(),
                    "site_id": site.site_id,
                    "equipment_id": equipment.equipment_id,
                    "event_type": event_type,
                    "duration_seconds": duration_seconds,
                    "alarm_code": (
                        f"ALM{self.random.randint(1, 25):03d}"
                        if event_type == "ALARM"
                        else ""
                    ),
                    "source_system": "EQUIPMENT_LOG",
                }

                monthly_events[month_key].append(event_row)
                event_sequence += 1

        self._inject_batch_errors(
            monthly_lots,
            monthly_results,
            monthly_events,
        )

        for month_key, rows in monthly_lots.items():
            file_path = (
                self.output_root
                / "batch/production_lots"
                / f"production_lots_{month_key}.csv"
            )
            self._write_csv(file_path, rows)
            self._register_file(file_path, "production_lots", len(rows))

        for month_key, rows in monthly_events.items():
            file_path = (
                self.output_root
                / "batch/equipment_events"
                / f"equipment_events_{month_key}.tsv"
            )
            self._write_csv(file_path, rows, delimiter="\t")
            self._register_file(file_path, "equipment_events", len(rows))

        for month_key, rows in monthly_results.items():
            file_path = (
                self.output_root
                / "batch/unit_test_results"
                / f"unit_test_results_{month_key}.json"
            )

            with file_path.open("w", encoding="utf-8") as output_file:
                for row in rows:
                    output_file.write(
                        json.dumps(row, separators=(",", ":")) + "\n"
                    )

            self._register_file(file_path, "unit_test_results", len(rows))

        for month_key, lines in monthly_logs.items():
            file_path = (
                self.output_root
                / "batch/tester_logs"
                / f"tester_{month_key}.log"
            )

            with file_path.open("w", encoding="utf-8") as output_file:
                output_file.write("\n".join(lines) + "\n")

            self._register_file(file_path, "tester_logs", len(lines))

    def _inject_batch_errors(
        self,
        monthly_lots: dict[str, list[dict[str, Any]]],
        monthly_results: dict[str, list[dict[str, Any]]],
        monthly_events: dict[str, list[dict[str, Any]]],
    ) -> None:
        first_month = sorted(monthly_lots)[0]

        if monthly_lots[first_month]:
            duplicate = dict(monthly_lots[first_month][0])
            monthly_lots[first_month].append(duplicate)

            self.expected_errors.append(
                {
                    "error_type": "DUPLICATE_BUSINESS_KEY",
                    "dataset": "production_lots",
                    "business_key": duplicate["lot_id"],
                    "expected_action": "DEDUPLICATE",
                }
            )

        if len(monthly_lots[first_month]) > 1:
            monthly_lots[first_month][1]["device_id"] = "UNKNOWN_DEVICE"

            self.expected_errors.append(
                {
                    "error_type": "UNKNOWN_REFERENCE",
                    "dataset": "production_lots",
                    "business_key": monthly_lots[first_month][1]["lot_id"],
                    "expected_action": "QUARANTINE",
                }
            )

        if monthly_results[first_month]:
            monthly_results[first_month][0]["lot"]["lot_id"] = None

            self.expected_errors.append(
                {
                    "error_type": "NULL_BUSINESS_KEY",
                    "dataset": "unit_test_results",
                    "business_key": (
                        monthly_results[first_month][0]["test_result_id"]
                    ),
                    "expected_action": "QUARANTINE",
                }
            )

        if monthly_events[first_month]:
            monthly_events[first_month][0]["duration_seconds"] = -120

            self.expected_errors.append(
                {
                    "error_type": "INVALID_DURATION",
                    "dataset": "equipment_events",
                    "business_key": (
                        monthly_events[first_month][0]["event_id"]
                    ),
                    "expected_action": "QUARANTINE",
                }
            )

    def generate_streaming_events(self) -> None:
        streaming_directory = (
            self.output_root / "streaming/tester_events"
        )
        batch_size = 500
        generated_count = 0

        base_event_timestamp = datetime.combine(
            self.config.end_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )

        for batch_number, start_index in enumerate(
            range(0, self.config.streaming_event_count, batch_size),
            start=1,
        ):
            batch_records: list[dict[str, Any]] = []

            current_batch_size = min(
                batch_size,
                self.config.streaming_event_count - start_index,
            )

            for local_index in range(current_batch_size):
                event_number = start_index + local_index + 1
                device = self.random.choice(self.devices)
                site = self.random.choice(SITES)
                equipment = self.random.choice(
                    self.equipment_by_site[site.site_id]
                )

                event_timestamp = (
                    base_event_timestamp + timedelta(seconds=event_number)
                )

                is_late = (
                    self.random.random()
                    < self.config.late_event_rate
                )

                if is_late:
                    event_timestamp -= timedelta(hours=3)

                status = self.random.choices(
                    ["PASS", "FAIL", "ALARM"],
                    weights=[92, 6, 2],
                    k=1,
                )[0]

                record = {
                    "event_id": f"STREAM{event_number:012d}",
                    "event_timestamp_utc": event_timestamp.isoformat(),
                    "ingestion_timestamp_utc": (
                        base_event_timestamp
                        + timedelta(seconds=event_number + 60)
                    ).isoformat(),
                    "site_id": site.site_id,
                    "equipment_id": equipment.equipment_id,
                    "device_id": device.device_id,
                    "product_group_id": device.product_group_id,
                    "event_type": "TEST_RESULT",
                    "status": status,
                    "test_time_seconds": round(
                        self.random.uniform(8.0, 38.0),
                        3,
                    ),
                    "is_deliberately_late": is_late,
                }

                batch_records.append(record)

            if batch_number == 1 and batch_records:
                duplicate = dict(batch_records[0])
                batch_records.append(duplicate)

                self.expected_errors.append(
                    {
                        "error_type": "DUPLICATE_STREAM_EVENT",
                        "dataset": "streaming_events",
                        "business_key": duplicate["event_id"],
                        "expected_action": "DEDUPLICATE",
                    }
                )

            file_path = (
                streaming_directory
                / f"event_batch_{batch_number:05d}.json"
            )

            with file_path.open("w", encoding="utf-8") as output_file:
                for record in batch_records:
                    output_file.write(json.dumps(record) + "\n")

            self._register_file(
                file_path,
                "streaming_events",
                len(batch_records),
            )
            generated_count += len(batch_records)

        self.manifest["streaming_records_written"] = generated_count

    def generate_binary_documents(self) -> None:
        binary_directory = self.output_root / "binary"

        for document_number in range(1, 26):
            equipment = self.random.choice(self.equipment)

            document_text = (
                "SEMICONPLUS MAINTENANCE DOCUMENT\n"
                f"Document Number: MNT-{document_number:05d}\n"
                f"Equipment ID: {equipment.equipment_id}\n"
                f"Equipment Model: {equipment.equipment_model}\n"
                f"Maintenance Type: PREVENTIVE\n"
                f"Technician ID: TECH-{document_number:04d}\n"
                "Result: COMPLETED\n"
                "Confidentiality: SYNTHETIC PORTFOLIO DATA\n"
            )

            file_path = (
                binary_directory
                / f"maintenance_document_{document_number:05d}.txt.bin"
            )
            file_path.write_bytes(document_text.encode("utf-8"))

            self._register_file(
                file_path,
                "binary_documents",
                1,
            )

    def write_manifests(self) -> None:
        self.manifest["generated_at_utc"] = datetime.now(
            timezone.utc
        ).isoformat()
        self.manifest["record_counts"] = dict(
            self.manifest["record_counts"]
        )

        manifest_path = (
            self.output_root / "manifests/dataset_manifest.json"
        )
        expected_errors_path = (
            self.output_root / "manifests/expected_errors.json"
        )

        manifest_path.write_text(
            json.dumps(self.manifest, indent=2),
            encoding="utf-8",
        )
        expected_errors_path.write_text(
            json.dumps(self.expected_errors, indent=2),
            encoding="utf-8",
        )

    def generate_all(self) -> dict[str, Any]:
        self.prepare_directories()
        self.generate_reference_data()
        self.generate_batch_data()
        self.generate_streaming_events()
        self.generate_binary_documents()
        self.write_manifests()

        return self.manifest