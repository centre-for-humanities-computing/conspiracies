from pathlib import Path

import pytest

from conspiracies.pipeline.config import (
    PipelineConfig,
    BaseConfig,
    PreProcessingConfig,
    DocProcessingConfig,
    CorpusProcessingConfig,
)


@pytest.fixture()
def path():
    data_path = Path(__file__).parent / "test_data" / "test_config.toml"
    return data_path


def test_config_loading(path: str):
    config = PipelineConfig.from_toml_file(path)
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
            metadata_fields={"metadata_field"},
            extra={
                "some_extra_value": 1234,
            },
        ),
        docprocessing=DocProcessingConfig(
            triplet_extraction_method="test",
        ),
        corpusprocessing=CorpusProcessingConfig(),
    )
