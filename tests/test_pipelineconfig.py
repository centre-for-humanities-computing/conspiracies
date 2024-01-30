from conspiracies.pipeline.config import (
    PipelineConfig,
    BaseConfig,
    PreProcessingConfig,
    DocProcessingConfig,
    CorpusProcessingConfig,
)


def test_config_loading():
    config = PipelineConfig.from_toml_file("test_data/test_config.toml")
    assert config == PipelineConfig(
        base=BaseConfig(
            project_name="test",
            output_root="output",
            language="en",
        ),
        preprocessing=PreProcessingConfig(
            enabled=False,
            input_path="some_input",
            doc_type="test",
            extra={
                "some_extra_value": 1234,
            },
        ),
        docprocessing=DocProcessingConfig(
            triplet_extraction_method="test",
        ),
        corpusprocessing=CorpusProcessingConfig(),
    )
