from __future__ import annotations

import csv
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from src.data_generator.config import SMOKE_CONFIG
from src.data_generator.generator import ManufacturingDataGenerator
from src.data_generator.reference_data import (
    PRODUCT_GROUPS,
    SITES,
    build_devices,
    build_equipment,
)
from src.data_generator.validation import DatasetValidator


@pytest.fixture()
def generated_dataset(tmp_path: Path):
    """Generate a small deterministic dataset for automated tests."""

    config = replace(
        SMOKE_CONFIG,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 2),
        average_lots_per_day=2,
        units_per_lot=3,
        equipment_events_per_day=5,
        streaming_event_count=20,
        output_root=str(tmp_path / "generated"),
    )

    generator = ManufacturingDataGenerator(config)
    manifest = generator.generate_all()

    return config, Path(config.output_root), manifest


def read_csv_rows(file_path: Path) -> list[dict[str, str]]:
    with file_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as input_file:
        return list(csv.DictReader(input_file))


def read_monthly_csv_rows(
    directory: Path,
    pattern: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for file_path in sorted(directory.glob(pattern)):
        rows.extend(read_csv_rows(file_path))

    return rows


def test_reference_entity_counts() -> None:
    devices = build_devices()
    equipment = build_equipment()

    assert len(PRODUCT_GROUPS) == 6
    assert len(devices) == 30
    assert len(SITES) == 3
    assert len(equipment) == 24


def test_reference_foreign_keys() -> None:
    product_group_ids = {
        item.product_group_id for item in PRODUCT_GROUPS
    }
    site_ids = {item.site_id for item in SITES}

    assert all(
        device.product_group_id in product_group_ids
        for device in build_devices()
    )

    assert all(
        equipment.site_id in site_ids
        for equipment in build_equipment()
    )


def test_generator_creates_required_directories(
    generated_dataset,
) -> None:
    _, output_root, _ = generated_dataset

    required_directories = [
        "reference",
        "batch/production_lots",
        "batch/equipment_events",
        "batch/unit_test_results",
        "batch/tester_logs",
        "streaming/tester_events",
        "binary",
        "manifests",
    ]

    for relative_path in required_directories:
        assert (output_root / relative_path).is_dir()


def test_generated_date_coverage(generated_dataset) -> None:
    config, output_root, _ = generated_dataset

    rows = read_monthly_csv_rows(
        output_root / "batch/production_lots",
        "*.csv",
    )
    observed_dates = {
        row["production_date"] for row in rows
    }

    assert config.start_date.isoformat() in observed_dates
    assert config.end_date.isoformat() in observed_dates


def test_expected_quality_failures_are_generated(
    generated_dataset,
) -> None:
    _, output_root, _ = generated_dataset

    expected_errors_path = (
        output_root / "manifests/expected_errors.json"
    )
    expected_errors = json.loads(
        expected_errors_path.read_text(encoding="utf-8")
    )

    generated_error_types = {
        item["error_type"] for item in expected_errors
    }

    assert "DUPLICATE_BUSINESS_KEY" in generated_error_types
    assert "UNKNOWN_REFERENCE" in generated_error_types
    assert "NULL_BUSINESS_KEY" in generated_error_types
    assert "INVALID_DURATION" in generated_error_types
    assert "DUPLICATE_STREAM_EVENT" in generated_error_types


def test_manifest_counts_match_generated_files(
    generated_dataset,
) -> None:
    _, output_root, manifest = generated_dataset

    manifest_path = (
        output_root / "manifests/dataset_manifest.json"
    )
    stored_manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    assert stored_manifest["random_seed"] == 42
    assert stored_manifest["record_counts"] == (
        manifest["record_counts"]
    )
    assert stored_manifest["record_counts"][
        "binary_documents"
    ] == 25


def test_generated_json_is_readable(
    generated_dataset,
) -> None:
    _, output_root, _ = generated_dataset

    json_directories = [
        output_root / "batch/unit_test_results",
        output_root / "streaming/tester_events",
    ]

    parsed_count = 0

    for directory in json_directories:
        for file_path in sorted(directory.glob("*.json")):
            for line in file_path.read_text(
                encoding="utf-8"
            ).splitlines():
                json.loads(line)
                parsed_count += 1

    assert parsed_count > 0


def test_validator_passes_generated_dataset(
    generated_dataset,
) -> None:
    config, _, _ = generated_dataset

    result = DatasetValidator(config).validate_all()

    assert result["status"] == "PASSED"
    assert result["errors"] == []


def test_fixed_seed_produces_same_business_data(
    tmp_path: Path,
) -> None:
    first_config = replace(
        SMOKE_CONFIG,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 2),
        average_lots_per_day=2,
        units_per_lot=3,
        equipment_events_per_day=5,
        streaming_event_count=20,
        output_root=str(tmp_path / "first"),
    )
    second_config = replace(
        first_config,
        output_root=str(tmp_path / "second"),
    )

    ManufacturingDataGenerator(first_config).generate_all()
    ManufacturingDataGenerator(second_config).generate_all()

    comparable_directories = [
        "reference",
        "batch",
        "binary",
        "streaming",
    ]

    for relative_directory in comparable_directories:
        first_files = sorted(
            path
            for path in (
                Path(first_config.output_root)
                / relative_directory
            ).rglob("*")
            if path.is_file()
        )
        second_files = sorted(
            path
            for path in (
                Path(second_config.output_root)
                / relative_directory
            ).rglob("*")
            if path.is_file()
        )

        assert [
            path.relative_to(first_config.output_root)
            for path in first_files
        ] == [
            path.relative_to(second_config.output_root)
            for path in second_files
        ]

        for first_file, second_file in zip(
            first_files,
            second_files,
            strict=True,
        ):
            assert first_file.read_bytes() == (
                second_file.read_bytes()
            )