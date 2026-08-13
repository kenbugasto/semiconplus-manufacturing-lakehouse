from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .config import GeneratorConfig


class DatasetValidationError(Exception):
    """Raised when generated data fails validation."""


class DatasetValidator:
    """Validate generated SemiconPlus source datasets."""

    REQUIRED_DIRECTORIES = [
        "reference",
        "batch/production_lots",
        "batch/equipment_events",
        "batch/unit_test_results",
        "batch/tester_logs",
        "streaming/tester_events",
        "binary",
        "manifests",
    ]

    REQUIRED_REFERENCE_FILES = [
        "product_groups.csv",
        "devices.csv",
        "sites.csv",
        "equipment.csv",
    ]

    def __init__(self, config: GeneratorConfig) -> None:
        self.config = config
        self.output_root = Path(config.output_root)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.metrics: dict[str, Any] = {}

    def _add_error(self, message: str) -> None:
        self.errors.append(message)

    def _add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def validate_directories(self) -> None:
        for relative_path in self.REQUIRED_DIRECTORIES:
            directory = self.output_root / relative_path

            if not directory.exists():
                self._add_error(
                    f"Required directory does not exist: {relative_path}"
                )

    def validate_reference_files(self) -> None:
        reference_directory = self.output_root / "reference"

        for file_name in self.REQUIRED_REFERENCE_FILES:
            file_path = reference_directory / file_name

            if not file_path.exists():
                self._add_error(
                    f"Required reference file does not exist: {file_name}"
                )
            elif file_path.stat().st_size == 0:
                self._add_error(
                    f"Reference file is empty: {file_name}"
                )

    def _read_csv_ids(
        self,
        file_path: Path,
        id_column: str,
        delimiter: str = ",",
    ) -> set[str]:
        identifiers: set[str] = set()

        with file_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as input_file:
            reader = csv.DictReader(
                input_file,
                delimiter=delimiter,
            )

            for row in reader:
                value = row.get(id_column)

                if value:
                    identifiers.add(value)

        return identifiers

    def validate_reference_integrity(self) -> None:
        reference_directory = self.output_root / "reference"

        device_ids = self._read_csv_ids(
            reference_directory / "devices.csv",
            "device_id",
        )
        product_group_ids = self._read_csv_ids(
            reference_directory / "product_groups.csv",
            "product_group_id",
        )
        site_ids = self._read_csv_ids(
            reference_directory / "sites.csv",
            "site_id",
        )
        equipment_ids = self._read_csv_ids(
            reference_directory / "equipment.csv",
            "equipment_id",
        )

        self.metrics["reference_device_count"] = len(device_ids)
        self.metrics["reference_product_group_count"] = len(
            product_group_ids
        )
        self.metrics["reference_site_count"] = len(site_ids)
        self.metrics["reference_equipment_count"] = len(equipment_ids)

        if len(device_ids) != self.config.product_group_count * (
            self.config.devices_per_product_group
        ):
            self._add_error(
                "Device reference count does not match configuration."
            )

        expected_equipment_count = (
            self.config.site_count
            * self.config.equipment_per_site
        )

        if len(equipment_ids) != expected_equipment_count:
            self._add_error(
                "Equipment reference count does not match configuration."
            )

        with (
            reference_directory / "devices.csv"
        ).open("r", encoding="utf-8", newline="") as input_file:
            for row in csv.DictReader(input_file):
                if row["product_group_id"] not in product_group_ids:
                    self._add_error(
                        "Device references an unknown product group: "
                        f"{row['device_id']}"
                    )

        with (
            reference_directory / "equipment.csv"
        ).open("r", encoding="utf-8", newline="") as input_file:
            for row in csv.DictReader(input_file):
                if row["site_id"] not in site_ids:
                    self._add_error(
                        "Equipment references an unknown site: "
                        f"{row['equipment_id']}"
                    )

    def validate_production_lots(self) -> None:
        reference_directory = self.output_root / "reference"

        valid_device_ids = self._read_csv_ids(
            reference_directory / "devices.csv",
            "device_id",
        )
        valid_site_ids = self._read_csv_ids(
            reference_directory / "sites.csv",
            "site_id",
        )
        valid_equipment_ids = self._read_csv_ids(
            reference_directory / "equipment.csv",
            "equipment_id",
        )

        lot_files = sorted(
            (
                self.output_root / "batch/production_lots"
            ).glob("*.csv")
        )

        if not lot_files:
            self._add_error("No production-lot files were generated.")
            return

        lot_ids: set[str] = set()
        duplicate_count = 0
        unknown_reference_count = 0
        row_count = 0
        observed_dates: list[str] = []

        for file_path in lot_files:
            with file_path.open(
                "r",
                encoding="utf-8",
                newline="",
            ) as input_file:
                for row in csv.DictReader(input_file):
                    row_count += 1
                    lot_id = row["lot_id"]
                    observed_dates.append(row["production_date"])

                    if lot_id in lot_ids:
                        duplicate_count += 1
                    else:
                        lot_ids.add(lot_id)

                    if (
                        row["device_id"] not in valid_device_ids
                        or row["site_id"] not in valid_site_ids
                        or row["equipment_id"]
                        not in valid_equipment_ids
                    ):
                        unknown_reference_count += 1

                    quantity_started = int(row["quantity_started"])
                    quantity_passed = int(row["quantity_passed"])
                    quantity_failed = int(row["quantity_failed"])

                    if quantity_started != (
                        quantity_passed + quantity_failed
                    ):
                        self._add_error(
                            f"Quantity mismatch for lot {lot_id}"
                        )

        self.metrics["production_lot_rows"] = row_count
        self.metrics["unique_lot_ids"] = len(lot_ids)
        self.metrics["known_duplicate_lots"] = duplicate_count
        self.metrics["known_unknown_references"] = (
            unknown_reference_count
        )

        if duplicate_count == 0:
            self._add_error(
                "Expected duplicate production lot was not generated."
            )

        if unknown_reference_count == 0:
            self._add_error(
                "Expected unknown device reference was not generated."
            )

        if observed_dates:
            if min(observed_dates) != self.config.start_date.isoformat():
                self._add_error(
                    "Dataset does not begin on the configured start date."
                )

            if max(observed_dates) != self.config.end_date.isoformat():
                self._add_error(
                    "Dataset does not end on the configured end date."
                )

    def validate_equipment_events(self) -> None:
        event_files = sorted(
            (
                self.output_root / "batch/equipment_events"
            ).glob("*.tsv")
        )

        if not event_files:
            self._add_error("No equipment-event files were generated.")
            return

        row_count = 0
        invalid_duration_count = 0

        for file_path in event_files:
            with file_path.open(
                "r",
                encoding="utf-8",
                newline="",
            ) as input_file:
                reader = csv.DictReader(
                    input_file,
                    delimiter="\t",
                )

                for row in reader:
                    row_count += 1

                    if int(row["duration_seconds"]) < 0:
                        invalid_duration_count += 1

        self.metrics["equipment_event_rows"] = row_count
        self.metrics["known_invalid_durations"] = (
            invalid_duration_count
        )

        if invalid_duration_count == 0:
            self._add_error(
                "Expected invalid equipment duration was not generated."
            )

    def validate_json_files(self) -> None:
        json_directories = [
            self.output_root / "batch/unit_test_results",
            self.output_root / "streaming/tester_events",
        ]

        parsed_rows = 0

        for directory in json_directories:
            json_files = sorted(directory.glob("*.json"))

            if not json_files:
                self._add_error(
                    f"No JSON files generated in {directory.name}."
                )
                continue

            for file_path in json_files:
                with file_path.open(
                    "r",
                    encoding="utf-8",
                ) as input_file:
                    for line_number, line in enumerate(
                        input_file,
                        start=1,
                    ):
                        try:
                            json.loads(line)
                            parsed_rows += 1
                        except json.JSONDecodeError as error:
                            self._add_error(
                                f"Malformed JSON in {file_path.name}, "
                                f"line {line_number}: {error}"
                            )

        self.metrics["parsed_json_rows"] = parsed_rows

    def validate_binary_documents(self) -> None:
        binary_files = sorted(
            (self.output_root / "binary").glob("*.bin")
        )

        if len(binary_files) != 25:
            self._add_error(
                "Expected 25 binary documents, "
                f"but found {len(binary_files)}."
            )

        for file_path in binary_files:
            content = file_path.read_bytes()

            if not content.startswith(
                b"SEMICONPLUS MAINTENANCE DOCUMENT"
            ):
                self._add_error(
                    f"Unexpected binary document header: {file_path.name}"
                )

        self.metrics["binary_document_count"] = len(binary_files)

    def validate_manifests(self) -> None:
        manifest_path = (
            self.output_root / "manifests/dataset_manifest.json"
        )
        errors_path = (
            self.output_root / "manifests/expected_errors.json"
        )

        for file_path in [manifest_path, errors_path]:
            if not file_path.exists():
                self._add_error(
                    f"Required manifest is missing: {file_path.name}"
                )
                continue

            try:
                json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                self._add_error(
                    f"Invalid manifest JSON in {file_path.name}: {error}"
                )

    def validate_all(self) -> dict[str, Any]:
        self.validate_directories()
        self.validate_reference_files()

        if not self.errors:
            self.validate_reference_integrity()
            self.validate_production_lots()
            self.validate_equipment_events()
            self.validate_json_files()
            self.validate_binary_documents()
            self.validate_manifests()

        result = {
            "status": "PASSED" if not self.errors else "FAILED",
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }

        if self.errors:
            raise DatasetValidationError(
                json.dumps(result, indent=2)
            )

        return result