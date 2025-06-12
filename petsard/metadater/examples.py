"""Examples demonstrating the functional programming approach"""

import pandas as pd

# Import the new functional API
from petsard.metadater import (
    DataType,
    FieldConfig,
    FieldPipeline,
    SchemaConfig,
    analyze_dataframe_fields,
    analyze_field,
    compose,
    create_field_analyzer,
    create_schema_from_dataframe,
    validate_field_data,
)


def example_basic_field_analysis():
    """Example: Basic field analysis using functional approach"""
    print("=== Basic Field Analysis ===")

    # Create sample data
    data = pd.Series([1, 2, 3, 4, 5, None, 7, 8, 9, 10], name="numbers")

    # Analyze field using functional approach
    field_metadata = analyze_field(
        field_data=data,
        field_name="numbers",
        compute_stats=True,
        infer_logical_type=True,
        optimize_dtype=True,
    )

    print(f"Field: {field_metadata.name}")
    print(f"Data Type: {field_metadata.data_type}")
    print(f"Nullable: {field_metadata.nullable}")
    print(f"Target Dtype: {field_metadata.target_dtype}")
    if field_metadata.stats:
        print(
            f"Stats: {field_metadata.stats.row_count} rows, {field_metadata.stats.na_count} nulls"
        )
    print()


def example_custom_field_analyzer():
    """Example: Creating custom field analyzer with partial application"""
    print("=== Custom Field Analyzer ===")

    # Create a custom analyzer with specific settings
    fast_analyzer = create_field_analyzer(
        compute_stats=False,  # Skip stats for speed
        infer_logical_type=True,
        optimize_dtype=True,
        sample_size=100,  # Small sample for speed
    )

    # Create sample email data
    emails = pd.Series(
        [
            "user1@example.com",
            "user2@test.org",
            "user3@company.net",
            "invalid-email",
            None,
        ],
        name="emails",
    )

    # Analyze using custom analyzer
    email_metadata = fast_analyzer(emails, "emails", None)

    print(f"Field: {email_metadata.name}")
    print(f"Data Type: {email_metadata.data_type}")
    print(f"Logical Type: {email_metadata.logical_type}")
    print(f"Has Stats: {email_metadata.stats is not None}")
    print()


def example_function_composition():
    """Example: Using function composition for complex operations"""
    print("=== Function Composition ===")

    # Create sample data
    data = pd.Series(["10%", "25%", "50%", "75%", "100%"], name="percentages")

    # Define processing steps as pure functions
    def create_base_metadata(series: pd.Series) -> tuple:
        field_name = str(series.name) if series.name is not None else "unnamed"
        return (series, analyze_field(series, field_name, compute_stats=False))

    def add_stats(data_and_metadata: tuple) -> tuple:
        series, metadata = data_and_metadata
        from petsard.metadater.core.field_functions import calculate_field_stats

        stats = calculate_field_stats(series, metadata)
        return (series, metadata.with_stats(stats))

    def add_logical_type(data_and_metadata: tuple) -> tuple:
        series, metadata = data_and_metadata
        from petsard.metadater.core.field_functions import infer_field_logical_type

        logical_type = infer_field_logical_type(series, metadata)
        if logical_type:
            metadata = metadata.with_logical_type(logical_type)
        return (series, metadata)

    # Compose the processing pipeline
    process_field = compose(
        lambda x: x[1],  # Extract metadata
        add_logical_type,
        add_stats,
        create_base_metadata,
    )

    # Process the data
    result = process_field(data)

    print(f"Field: {result.name}")
    print(f"Logical Type: {result.logical_type}")
    print(f"Row Count: {result.stats.row_count if result.stats else 'N/A'}")
    print()


def example_pipeline_approach():
    """Example: Using pipeline approach for field processing"""
    print("=== Pipeline Approach ===")

    # Create sample categorical data
    categories = pd.Series(["A", "B", "A", "C", "B", "A", "C"], name="category")

    # Create a processing pipeline
    pipeline = (
        FieldPipeline()
        .with_stats(enabled=True)
        .with_logical_type_inference(enabled=True)
        .with_dtype_optimization(enabled=True)
    )

    # Create initial metadata
    initial_metadata = analyze_field(
        categories,
        "category",
        compute_stats=False,
        infer_logical_type=False,
        optimize_dtype=False,
    )

    # Process through pipeline
    final_metadata = pipeline.process(categories, initial_metadata)

    print(f"Field: {final_metadata.name}")
    print(f"Logical Type: {final_metadata.logical_type}")
    print(f"Target Dtype: {final_metadata.target_dtype}")
    print(
        f"Distinct Count: {final_metadata.stats.distinct_count if final_metadata.stats else 'N/A'}"
    )
    print()


def example_dataframe_analysis():
    """Example: Analyzing entire DataFrame using functional approach"""
    print("=== DataFrame Analysis ===")

    # Create sample DataFrame
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "email": [
                "alice@test.com",
                "bob@test.com",
                "charlie@test.com",
                "diana@test.com",
                "eve@test.com",
            ],
            "age": [25, 30, 35, 28, 32],
            "score": [85.5, 92.0, 78.5, 88.0, 95.5],
        }
    )

    # Define field configurations
    field_configs = {
        "id": FieldConfig(type_hint="int", nullable=False),
        "email": FieldConfig(logical_type="email", nullable=False),
        "age": FieldConfig(type_hint="int", nullable=False),
    }

    # Analyze all fields
    field_metadata_dict = analyze_dataframe_fields(data=df, field_configs=field_configs)

    print("Field Analysis Results:")
    for name, metadata in field_metadata_dict.items():
        print(
            f"  {name}: {metadata.data_type.value} "
            f"({metadata.logical_type.value if metadata.logical_type else 'no logical type'})"
        )

    # Create schema
    schema = create_schema_from_dataframe(
        data=df,
        schema_id="user_data",
        config=SchemaConfig(
            schema_id="user_data",
            name="User Data Schema",
            fields=field_configs,
            compute_stats=True,
        ),
    )

    print(f"\nSchema: {schema.name}")
    print(f"Fields: {len(schema.fields)}")
    print()


def example_validation():
    """Example: Functional validation approach"""
    print("=== Functional Validation ===")

    # Create sample data with issues
    data = pd.Series([1, 2, None, 4, 5], name="required_field")

    # Create metadata that expects no nulls
    from petsard.metadater.types.field_types import FieldMetadata

    metadata = FieldMetadata(
        name="required_field",
        data_type=DataType.INT64,
        nullable=False,  # This will cause validation to fail
    )

    # Validate
    validation_result = validate_field_data(data, metadata)

    print("Validation Result:")
    print(f"  Valid: {validation_result['valid']}")
    print(f"  Violations: {len(validation_result['violations'])}")
    print(f"  Warnings: {len(validation_result['warnings'])}")

    if validation_result["violations"]:
        for violation in validation_result["violations"]:
            print(f"    - {violation['message']}")
    print()


def run_all_examples():
    """Run all examples"""
    print("🚀 Functional Programming Metadater Examples\n")

    example_basic_field_analysis()
    example_custom_field_analyzer()
    example_function_composition()
    example_pipeline_approach()
    example_dataframe_analysis()
    example_validation()

    print("✅ All examples completed!")


if __name__ == "__main__":
    run_all_examples()
