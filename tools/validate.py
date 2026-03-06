#!/usr/bin/env python3
"""
TarlaAnaliz Contracts Validator
Validates all JSON Schema and OpenAPI files
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Forbidden fields (per KR-050: NO email, NO TCKN, NO OTP)
FORBIDDEN_FIELDS = ['email', 'e_mail', 'tckn', 'tc_kimlik_no', 'otp', 'one_time_password']


def _check_forbidden_recursive(obj: Any, path: str, schema_path: Path) -> List[str]:
    """Recursively check for forbidden PII fields in nested objects."""
    errors = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in FORBIDDEN_FIELDS:
                errors.append(
                    f"FORBIDDEN field '{key}' found at {path}.{key} in {schema_path}"
                )
            errors.extend(_check_forbidden_recursive(value, f"{path}.{key}", schema_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            errors.extend(_check_forbidden_recursive(item, f"{path}[{i}]", schema_path))
    return errors


def _check_unevaluated_in_defs(schema: dict, schema_path: Path) -> List[str]:
    """Check that all object-type $defs have unevaluatedProperties: false."""
    errors = []
    defs = schema.get('$defs', {})
    if not isinstance(defs, dict):
        return errors
    for def_name, def_schema in defs.items():
        if not isinstance(def_schema, dict):
            continue
        if def_schema.get('type') == 'object':
            if 'unevaluatedProperties' not in def_schema:
                errors.append(
                    f"Missing unevaluatedProperties in $defs.{def_name} in {schema_path}"
                )
            elif def_schema['unevaluatedProperties'] is not False:
                errors.append(
                    f"unevaluatedProperties must be false in $defs.{def_name} in {schema_path}"
                )
    return errors


def validate_json_schema(schema_path: Path) -> List[str]:
    """Validate JSON Schema file"""
    errors = []

    try:
        with open(schema_path) as f:
            schema = json.load(f)

        # Check $schema
        if '$schema' not in schema:
            errors.append(f"Missing $schema in {schema_path}")
        elif 'draft/2020-12' not in schema['$schema']:
            errors.append(f"Wrong draft version in {schema_path} (must be 2020-12)")

        # Check $id (KR-081: mandatory, must use canonical URL)
        if '$id' not in schema:
            errors.append(f"Missing $id in {schema_path}")
        elif not schema['$id'].startswith('https://api.tarlaanaliz.com/schemas/'):
            errors.append(
                f"Invalid $id format in {schema_path}: "
                f"must start with https://api.tarlaanaliz.com/schemas/"
            )

        # Check title (KR-081: mandatory)
        if 'title' not in schema:
            errors.append(f"Missing title in {schema_path}")

        # Check type (KR-081: mandatory)
        if 'type' not in schema:
            errors.append(f"Missing type in {schema_path}")

        # Check unevaluatedProperties at root level
        if schema.get('type') == 'object':
            if 'unevaluatedProperties' not in schema:
                errors.append(f"Missing unevaluatedProperties in {schema_path}")
            elif schema['unevaluatedProperties'] is not False:
                errors.append(f"unevaluatedProperties must be false in {schema_path}")

        # Check unevaluatedProperties in $defs
        errors.extend(_check_unevaluated_in_defs(schema, schema_path))

        # Check for forbidden fields recursively (KR-050)
        errors.extend(_check_forbidden_recursive(schema, "$", schema_path))

    except json.JSONDecodeError as e:
        errors.append(f"JSON parse error in {schema_path}: {e}")
    except Exception as e:
        errors.append(f"Error validating {schema_path}: {e}")

    return errors


def validate_enum_file(enum_path: Path) -> List[str]:
    """Validate enum file structure."""
    errors = []

    try:
        with open(enum_path) as f:
            data = json.load(f)

        # Check required fields
        if 'enum' not in data:
            errors.append(f"Missing 'enum' array in {enum_path}")
        else:
            values = data['enum']
            if len(values) != len(set(values)):
                errors.append(f"Duplicate enum values in {enum_path}")
            if not values:
                errors.append(f"Empty enum array in {enum_path}")

        # Check for forbidden fields
        errors.extend(_check_forbidden_recursive(data, "$", enum_path))

    except json.JSONDecodeError as e:
        errors.append(f"JSON parse error in {enum_path}: {e}")
    except Exception as e:
        errors.append(f"Error validating {enum_path}: {e}")

    return errors


def main():
    """Main validation"""
    print("🔍 TarlaAnaliz Contracts Validator\n")

    base_dir = Path(__file__).parent.parent
    schemas_dir = base_dir / 'schemas'
    enums_dir = base_dir / 'enums'

    all_errors = []
    total_files = 0

    # Validate all JSON Schema files
    for schema_file in schemas_dir.rglob('*.json'):
        total_files += 1
        print(f"Validating {schema_file.relative_to(base_dir)}...")
        errors = validate_json_schema(schema_file)
        all_errors.extend(errors)

    # Validate enum files
    if enums_dir.exists():
        for enum_file in enums_dir.rglob('*.json'):
            total_files += 1
            print(f"Validating {enum_file.relative_to(base_dir)}...")
            errors = validate_enum_file(enum_file)
            all_errors.extend(errors)

    # Print results
    print(f"\n{'='*60}")
    print(f"Total files validated: {total_files}")
    print(f"Total errors: {len(all_errors)}")

    if all_errors:
        print("\n❌ VALIDATION FAILED\n")
        for error in all_errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("\n✅ ALL VALIDATIONS PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
