import toml
from pydantic import BaseModel


class ProjectConfig(BaseModel):
    project_name: str
    output_root: str
    language: str


class StepConfig(BaseModel):
    enabled: bool = True


class PreprocessingConfig(StepConfig):
    input_path: str
    doc_type: str
    extra: dict = {}


class DocprocessingConfig(StepConfig):
    triplet_extraction_method: str


class PipelineConfig(BaseModel):
    project: ProjectConfig
    preprocessing: PreprocessingConfig
    docprocessing: DocprocessingConfig

    @classmethod
    def from_toml_file(cls, path: str):
        with open(path, "r") as file:
            config_data = toml.load(file)
        return cls(**config_data)
