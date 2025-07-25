from typing import Union

from llm.local.inference import LocalInference
from utils.app_config import AppConfig, InferenceEngine


class Inference:
    def __init__(self, app_config: AppConfig = AppConfig.load_default()):
        self.app_config = app_config
        self.llm: Union[LocalInference, None] = None

        match self.app_config.inference.inference_engine:
            case InferenceEngine.LOCAL:
                self.llm = LocalInference()
            case _:
                raise ValueError("Unknown inference engine")

    def get_llm(self) -> Union[LocalInference, None]:
        return self.llm
