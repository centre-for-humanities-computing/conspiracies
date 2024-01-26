from pydantic import BaseModel


class ProjectConfig(BaseModel):
    project_name: str
    output_root: str
    language: str


class PreprocessingConfig(BaseModel):
    input_path: str
    doc_type: str


class DocprocessingConfig(BaseModel):
    triplet_extraction_method: str
