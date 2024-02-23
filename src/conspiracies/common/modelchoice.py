import logging
from typing import Any


class ModelChoice:
    """Helper class for selecting an appropriate model based on language codes.

    An error will be thrown on unsupported languages. To avoid that, set 'fallback'
    model if appropriate.

    If choices are given as supplier functions, they will be called and then returned.

    Usage:

    >>> mc1 = ModelChoice(da="danish_model", fallback="fallback_model")
    >>> mc1.get_model("da") # "danish_model"
    >>> mc1.get_model("de") # "fallback_model"
    >>> mc2 = ModelChoice(da="danish_model")
    >>> mc2.get_model("de") # throws error
    >>> mc3 = ModelChoice(da=lambda: "danish_model")
    >>> mc3.get_model("da") # "danish_model"
    """

    def __init__(self, **choices: Any):
        self.models = choices

    def get_model(self, language: str):
        if language not in self.models:
            error = f"Language '{language}' not supported!"
            if "fallback" in self.models:
                logging.warning(error + " Using fallback model.")
                language = "fallback"
            else:
                raise ValueError(error)
        model = self.models[language]
        if callable(model):  # if supplier function
            model = model()
        logging.debug("Using '%s' model: %s", language, model)
        return model
