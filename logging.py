import json
import logging

from typing import Any

import structlog
from structlog.tracebacks import ExceptionDictTransformer
from structlog.typing import ExcInfo


class CustomExceptionDictTransformer(ExceptionDictTransformer):
    def __call__(self, exc_info: ExcInfo) -> list[dict[str, Any]]:
        stacks = super().__call__(exc_info)
        stack_dict = stacks[0]
        stack_dict["place"] = stack_dict["frames"][2]
        stacks[0] = dict(  # noqa: C408
            exc_type=stack_dict["exc_type"],
            exc_value=stack_dict["exc_value"],
            place=stack_dict["place"],
        )
        return stacks


structlog.configure(
    cache_logger_on_first_use=True,
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.BytesLoggerFactory(),
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.ExceptionRenderer(
            CustomExceptionDictTransformer(show_locals=False, max_frames=2)
        ),
        structlog.processors.JSONRenderer(serializer=json.dumps),
    ],
)
logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)
