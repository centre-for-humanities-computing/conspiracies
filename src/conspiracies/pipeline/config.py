import toml
from pydantic import BaseModel


class BaseConfig(BaseModel):
    project_name: str
    output_root: str
    language: str


class StepConfig(BaseModel):
    enabled: bool = True


class PreProcessingConfig(StepConfig):
    input_path: str
    doc_type: str
    extra: dict = {}


class DocProcessingConfig(StepConfig):
    triplet_extraction_method: str


class CorpusProcessingConfig(StepConfig):
    pass


class PipelineConfig(BaseModel):
    base: BaseConfig
    preprocessing: PreProcessingConfig
    docprocessing: DocProcessingConfig
    corpusprocessing: CorpusProcessingConfig

    @staticmethod
    def update_nested_dict(d, path, value):
        keys = path.split(".")
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    @classmethod
    def from_toml_file(cls, path: str, extra_config: dict = None):
        with open(path, "r") as file:
            config_data = toml.load(file)
        if extra_config:
            for path, value in extra_config.items():
                if value is None:
                    continue
                PipelineConfig.update_nested_dict(config_data, path, value)
        return cls(**config_data)
