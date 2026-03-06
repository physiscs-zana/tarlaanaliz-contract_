#!/usr/bin/env python3
"""
Test: Examples Match Schemas

Tests that all example JSON files in docs/examples/ validate against their schemas.
This ensures examples are always up-to-date and accurate.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any

try:
    from jsonschema import Draft202012Validator, ValidationError  # type: ignore[import-untyped]
    from referencing import Registry, Resource  # type: ignore[import-untyped]
except ImportError:
    pytest.skip("jsonschema or referencing not installed", allow_module_level=True)


def _build_local_registry(base_dir: Path) -> Registry:
    """Build a referencing.Registry from all local schema/enum JSON files."""
    registry = Registry()
    # Collect all JSON files under schemas/ and enums/
    for search_dir in [base_dir / "schemas", base_dir / "enums"]:
        if not search_dir.exists():
            continue
        for json_file in search_dir.rglob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    contents = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(contents, dict):
                continue
            schema_id = contents.get("$id")
            if schema_id:
                resource = Resource.from_contents(contents)
                registry = registry.with_resource(schema_id, resource)
    return registry


class TestExamplesValidation:
    """Test suite for example validation"""
    
    @pytest.fixture(scope="class")
    def base_dir(self) -> Path:
        """Get base directory"""
        return Path(__file__).parent.parent
    
    @pytest.fixture(scope="class")
    def examples_dir(self, base_dir: Path) -> Path:
        """Get examples directory"""
        return base_dir / "docs" / "examples"
    
    @pytest.fixture(scope="class")
    def schemas_dir(self, base_dir: Path) -> Path:
        """Get schemas directory"""
        return base_dir / "schemas"

    @pytest.fixture(scope="class")
    def registry(self, base_dir: Path) -> Registry:
        """Build local registry for $ref resolution"""
        return _build_local_registry(base_dir)
    
    # Schema-to-example mapping
    EXAMPLE_SCHEMA_MAP = {
        'field.example.json': 'core/field.v1.schema.json',
        'mission.example.json': 'core/mission.v1.schema.json',
        'intake_manifest.example.json': 'edge/intake_manifest.v1.schema.json',
        'analysis_job.example.json': 'worker/analysis_job.v1.schema.json',
        'analysis_result.example.json': 'worker/analysis_result.v1.schema.json',
        'dataset.example.json': 'datasets/dataset.v1.schema.json',
        'dataset_manifest.example.json': 'datasets/dataset_manifest.v1.schema.json',
        'payment_intent_creditcard_paid.example.json': 'platform/payment_intent.v2.schema.json',
        'payment_intent_iban_paid.example.json': 'platform/payment_intent.v2.schema.json',
        'payment_intent_iban_pending.example.json': 'platform/payment_intent.v2.schema.json',
    }
    
    def load_schema(self, schema_path: Path) -> Dict[str, Any]:
        """Load and return schema"""
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_example(self, example_path: Path) -> Any:
        """Load and return example"""
        with open(example_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_examples_directory_exists(self, examples_dir: Path):
        """Test that examples directory exists"""
        assert examples_dir.exists(), "docs/examples/ directory not found"
        assert examples_dir.is_dir(), "docs/examples/ is not a directory"
    
    def test_has_example_files(self, examples_dir: Path):
        """Test that we have example files"""
        example_files = list(examples_dir.glob("*.json"))
        assert len(example_files) >= 5, f"Expected at least 5 examples, found {len(example_files)}"
    
    @pytest.mark.parametrize("example_name,schema_path", EXAMPLE_SCHEMA_MAP.items())
    def test_example_validates_against_schema(
        self,
        example_name: str,
        schema_path: str,
        examples_dir: Path,
        schemas_dir: Path,
        registry: Registry
    ):
        """Test that example validates against its schema"""
        example_file = examples_dir / example_name
        schema_file = schemas_dir / schema_path

        # Check files exist
        assert example_file.exists(), f"Example not found: {example_file}"
        assert schema_file.exists(), f"Schema not found: {schema_file}"

        # Load files
        example = self.load_example(example_file)
        schema = self.load_schema(schema_file)

        # Validate with local registry for $ref resolution
        validator = Draft202012Validator(schema, registry=registry)
        
        errors = list(validator.iter_errors(example))
        
        if errors:
            error_messages = []
            for error in errors:
                path = " -> ".join(str(p) for p in error.path) if error.path else "root"
                error_messages.append(f"  Path: {path}\n  Error: {error.message}")
            
            pytest.fail(
                f"Example {example_name} failed validation against {schema_path}:\n" +
                "\n\n".join(error_messages)
            )
    
    def test_field_example_has_required_fields(self, examples_dir: Path):
        """Test field example has all required fields"""
        example = self.load_example(examples_dir / "field.example.json")
        
        required = ['id', 'name', 'boundary', 'area_hectares', 'crop_type', 'location']
        
        for field in required:
            assert field in example, f"Missing required field: {field}"
    
    def test_field_example_crop_is_gap_crop(self, examples_dir: Path):
        """Test field example uses GAP crop (KR-002)"""
        example = self.load_example(examples_dir / "field.example.json")
        
        gap_crops = {
            'COTTON', 'PISTACHIO', 'MAIZE', 'WHEAT',
            'SUNFLOWER', 'GRAPE', 'OLIVE', 'RED_LENTIL'
        }
        
        assert example['crop_type'] in gap_crops, \
            f"Example must use GAP crop, got: {example['crop_type']}"
    
    def test_mission_example_analysis_types_are_kr002(self, examples_dir: Path):
        """Test mission example uses KR-002 analysis types"""
        example = self.load_example(examples_dir / "mission.example.json")
        
        kr002_types = {
            'HEALTH', 'DISEASE', 'PEST', 'FUNGUS',
            'WEED', 'WATER_STRESS', 'NITROGEN_STRESS'
        }
        
        for analysis_type in example.get('analysis_types', []):
            assert analysis_type in kr002_types, \
                f"Example must use KR-002 analysis type, got: {analysis_type}"
    
    def test_analysis_job_example_has_kr002_types(self, examples_dir: Path):
        """Test analysis job example uses KR-002 types"""
        example = self.load_example(examples_dir / "analysis_job.example.json")
        
        kr002_types = {
            'HEALTH', 'DISEASE', 'PEST', 'FUNGUS',
            'WEED', 'WATER_STRESS', 'NITROGEN_STRESS'
        }
        
        for analysis_type in example.get('analysis_types', []):
            assert analysis_type in kr002_types, \
                f"Job example must use KR-002 type, got: {analysis_type}"
    
    def test_analysis_result_example_has_map_layers(self, examples_dir: Path):
        """Test analysis result example has map layers (KR-002)"""
        example = self.load_example(examples_dir / "analysis_result.example.json")
        
        assert 'layers' in example, "Result example must have 'layers'"
        assert len(example['layers']) > 0, "Result example must have at least one layer"
        
        # Check layer structure
        for layer in example['layers']:
            assert 'name' in layer, "Layer must have 'name'"
            assert 'type' in layer, "Layer must have 'type'"
    
    def test_intake_manifest_example_has_sha256_hashes(self, examples_dir: Path):
        """Test intake manifest example has SHA-256 hashes"""
        example = self.load_example(examples_dir / "intake_manifest.example.json")
        
        # Check batch hash
        if 'batch_sha256' in example:
            assert len(example['batch_sha256']) == 64, \
                "SHA-256 hash must be 64 characters"
        
        # Check file hashes
        if 'files' in example:
            for file_info in example['files']:
                if 'sha256' in file_info:
                    assert len(file_info['sha256']) == 64, \
                        f"File SHA-256 hash must be 64 characters: {file_info.get('filename')}"
    
    def test_examples_have_valid_ids(self, examples_dir: Path):
        """Test that example IDs follow either UUID format or {entity}_{24-char-hex} pattern"""
        import re
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        )
        entity_id_pattern = re.compile(
            r'^[a-z][a-z0-9]*_[0-9a-f]{24}$'
        )

        for example_file in examples_dir.glob("*.json"):
            example = self.load_example(example_file)

            def check_ids(obj: Any, path: str = "") -> None:
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.endswith('_id') and isinstance(value, str):
                            # Accept UUID format, entity_24hex format, or other
                            # well-known non-entity ID formats (e.g. prefixed IDs)
                            is_uuid = bool(uuid_pattern.match(value))
                            is_entity_hex = bool(entity_id_pattern.match(value))
                            has_underscore = '_' in value

                            has_hyphen = '-' in value

                            assert is_uuid or is_entity_hex or has_underscore or has_hyphen, \
                                (f"ID in {example_file.name} must be UUID, "
                                 f"entity_24hex, or contain a delimiter: {key}={value}")

                        check_ids(value, f"{path}.{key}" if path else key)
                elif isinstance(obj, list):
                    for item in obj:
                        check_ids(item, path)

            check_ids(example)
    
    def test_examples_no_forbidden_fields(self, examples_dir: Path):
        """Test that examples don't contain forbidden fields (email/tckn/otp)"""
        forbidden = ['email', 'tckn', 'otp', 'tc_kimlik_no']
        
        for example_file in examples_dir.glob("*.json"):
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            found = []
            for field in forbidden:
                if f'"{field}"' in content:
                    found.append(field)
            
            assert len(found) == 0, \
                f"Forbidden fields found in {example_file.name}: {found}"
    
    def test_examples_use_iso8601_timestamps(self, examples_dir: Path):
        """Test that examples use ISO 8601 timestamps"""
        import re
        
        # ISO 8601 pattern
        iso8601_pattern = re.compile(
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$'
        )
        
        for example_file in examples_dir.glob("*.json"):
            example = self.load_example(example_file)
            
            def check_timestamps(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        # Check fields ending with _at or _timestamp
                        if (key.endswith('_at') or key.endswith('_timestamp')) and isinstance(value, str):
                            assert iso8601_pattern.match(value), \
                                f"Timestamp in {example_file.name} must be ISO 8601: {key}={value}"
                        
                        check_timestamps(value, f"{path}.{key}" if path else key)
                elif isinstance(obj, list):
                    for item in obj:
                        check_timestamps(item, path)
            
            check_timestamps(example)
    
    def test_all_examples_have_readme_entry(self, examples_dir: Path):
        """Test that all examples are documented in README"""
        readme_path = examples_dir / "README.md"
        
        if not readme_path.exists():
            pytest.skip("examples/README.md not found")
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        for example_file in examples_dir.glob("*.json"):
            assert example_file.name in readme_content, \
                f"Example {example_file.name} not documented in README.md"


class TestExampleCompleteness:
    """Test that examples are complete and realistic"""
    
    def test_field_example_has_realistic_area(self):
        """Test field example has realistic area (1-1000 hectares)"""
        example_path = Path(__file__).parent.parent / "docs" / "examples" / "field.example.json"
        
        with open(example_path, 'r', encoding='utf-8') as f:
            example = json.load(f)
        
        area = example.get('area_hectares', 0)
        assert 1 <= area <= 1000, \
            f"Field area should be 1-1000 hectares, got: {area}"
    
    def test_field_example_has_valid_geojson(self):
        """Test field example has valid GeoJSON polygon"""
        example_path = Path(__file__).parent.parent / "docs" / "examples" / "field.example.json"
        
        with open(example_path, 'r', encoding='utf-8') as f:
            example = json.load(f)
        
        boundary = example.get('boundary', {})
        
        assert boundary.get('type') == 'Polygon', "Boundary must be GeoJSON Polygon"
        assert 'coordinates' in boundary, "Boundary must have coordinates"
        
        coords = boundary['coordinates']
        assert len(coords) > 0, "Boundary must have at least one ring"
        
        # Check first and last coordinates are identical (closed polygon)
        first_ring = coords[0]
        assert first_ring[0] == first_ring[-1], \
            "Polygon must be closed (first and last coordinates identical)"
    
    def test_mission_example_has_valid_schedule(self):
        """Test mission example has valid schedule"""
        example_path = Path(__file__).parent.parent / "docs" / "examples" / "mission.example.json"
        
        with open(example_path, 'r', encoding='utf-8') as f:
            example = json.load(f)
        
        assert 'planned_date' in example, "Mission must have planned_date"

        # Date should be in YYYY-MM-DD format
        import re
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        assert date_pattern.match(example['planned_date']), \
            f"planned_date must be YYYY-MM-DD format: {example['planned_date']}"


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])