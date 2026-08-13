from __future__ import annotations

import argparse
import json
import time

from src.data_generator.config import DEV_CONFIG, SMOKE_CONFIG
from src.data_generator.generator import ManufacturingDataGenerator
from src.data_generator.validation import (
    DatasetValidationError,
    DatasetValidator,
)

from src.data_generator.config import DEV_CONFIG, SMOKE_CONFIG
from src.data_generator.generator import ManufacturingDataGenerator
from src.data_generator.validation import (
    DatasetValidationError,
    DatasetValidator,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate and validate synthetic SemiconPlus "
            "semiconductor manufacturing data."
        )
    )

    parser.add_argument(
        "--profile",
        choices=["smoke", "development"],
        default="smoke",
        # default="development",
        help=(
            "Dataset profile to generate. The default profile is smoke."
        ),
    )

    arguments, unknown_arguments = parser.parse_known_args()

    if unknown_arguments:
        print(
            "Ignoring Databricks runtime arguments: "
            f"{unknown_arguments}"
        )

    return arguments


def select_config(profile: str):
    if profile == "smoke":
        return SMOKE_CONFIG

    if profile == "development":
        return DEV_CONFIG

    raise ValueError(f"Unsupported generator profile: {profile}")


def main() -> int:
    arguments = parse_arguments()
    config = select_config(arguments.profile)

    print("=" * 72)
    print("SEMICONPLUS SYNTHETIC DATA GENERATOR")
    print("=" * 72)
    print(f"Profile      : {arguments.profile}")
    print(f"Start date   : {config.start_date}")
    print(f"End date     : {config.end_date}")
    print(f"Random seed  : {config.random_seed}")
    print(f"Output root  : {config.output_root}")
    print("=" * 72)

    generation_start = time.perf_counter()

    generator = ManufacturingDataGenerator(config)
    manifest = generator.generate_all()

    generation_seconds = time.perf_counter() - generation_start

    print("\nGeneration completed.")
    print(f"Generation time: {generation_seconds:.2f} seconds")
    print("\nGenerated record counts:")
    print(
        json.dumps(
            manifest["record_counts"],
            indent=2,
            sort_keys=True,
        )
    )

    print("\nStarting dataset validation...")

    validation_start = time.perf_counter()
    validator = DatasetValidator(config)

    try:
        validation_result = validator.validate_all()
    except DatasetValidationError as error:
        validation_seconds = (
            time.perf_counter() - validation_start
        )

        print("\nDATASET VALIDATION FAILED")
        print(str(error))
        print(
            f"Validation time: {validation_seconds:.2f} seconds"
        )
        return 1

    validation_seconds = time.perf_counter() - validation_start

    print("\nDATASET VALIDATION PASSED")
    print(
        json.dumps(
            validation_result,
            indent=2,
            sort_keys=True,
        )
    )
    print(
        f"\nValidation time: {validation_seconds:.2f} seconds"
    )
    print(
        f"Total runtime: "
        f"{generation_seconds + validation_seconds:.2f} seconds"
    )
    print("=" * 72)

    return 0


if __name__ == "__main__":
    exit_code = main()

    if exit_code != 0:
        raise RuntimeError(
            f"SemiconPlus generator failed with exit code {exit_code}."
        )