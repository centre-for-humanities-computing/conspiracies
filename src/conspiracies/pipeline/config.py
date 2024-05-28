from typing import Any

import toml
from pydantic import BaseModel


class BaseConfig(BaseModel):
    project_name: str
    output_root: str = "output"
    language: str


class StepConfig(BaseModel):
    enabled: bool = True


class PreProcessingConfig(StepConfig):
    input_path: str
    n_docs: int = None
    doc_type: str = "text"
    metadata_fields: set[str] = ["*"]
    extra: dict = {}


class DocProcessingConfig(StepConfig):
    batch_size: int = 25
    continue_from_last: bool = True
    triplet_extraction_method: str = "multi2oie"
    prefer_gpu_for_coref: bool = False


class ClusteringThresholds(BaseModel):
    min_cluster_size: int
    min_samples: int

    @classmethod
    def estimate_from_n_triplets(cls, n_triplets: int):
        factor = n_triplets / 1000
        thresholds = cls(
            min_cluster_size=max(int(factor + 1), 2),
            min_samples=int(factor + 1),
        )
        return thresholds


class CorpusProcessingConfig(StepConfig):
    dimensions: int = None
    n_neighbors: int = 15
    embedding_model: str = None
    thresholds: ClusteringThresholds = None


class PipelineConfig(BaseModel):
    base: BaseConfig
    preprocessing: PreProcessingConfig
    docprocessing: DocProcessingConfig
    corpusprocessing: CorpusProcessingConfig

    @staticmethod
    def update_nested_dict(d: dict[str, Any], path: str, value: Any) -> None:
        """Sets or updates a nested dict in place with a TOML-like string key.

        >>> some_dict = {"a": {"b": 1}}
        >>> PipelineConfig.update_nested_dict(some_dict, "a.b", 2)
        >>> some_dict["a"]["b"] == 2  # True

        Args:
            d: (nested) dict with str keys to be updated
            path: a TOML-like string key with '.' as level separators, e.g. "a.b.c"
            value: value to set under the nested key
        """
        keys = path.split(".")
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    @staticmethod
    def full_update_nested_dict(d: dict[str, Any], values: dict[str, Any]):
        for path, value in values.items():
            if value is None:
                continue
            PipelineConfig.update_nested_dict(d, path, value)

    @classmethod
    def from_toml_file(cls, path: str, extra_config: dict = None):
        with open(path, "r") as file:
            config_data = toml.load(file)
        if extra_config:
            PipelineConfig.full_update_nested_dict(config_data, extra_config)
        return cls(**config_data)

    @classmethod
    def default_with_extra_config(cls, extra_config: dict):
        config_data = {
            "base": {},
            "preprocessing": {},
            "docprocessing": {},
            "corpusprocessing": {},
        }
        PipelineConfig.full_update_nested_dict(config_data, extra_config)
        return cls(**config_data)
