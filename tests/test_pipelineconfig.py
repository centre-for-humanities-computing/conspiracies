from conspiracies.pipeline.config import (
    PipelineConfig,
    ProjectConfig,
    PreprocessingConfig,
    DocprocessingConfig,
)


def test_config_loading():
    config = PipelineConfig.from_toml_file("test_data/test_config.toml")
    assert config == PipelineConfig(
        project=ProjectConfig(
            project_name="test",
            output_root="output",
            language="en",
        ),
        preprocessing=PreprocessingConfig(
            enabled=False,
            input_path="some_input",
            doc_type="test",
            extra={
                "some_extra_value": 1234,
            },
        ),
        docprocessing=DocprocessingConfig(
            triplet_extraction_method="test",
        ),
    )
