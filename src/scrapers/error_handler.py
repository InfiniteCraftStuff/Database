from functools import wraps
from typing import TypeVar, ParamSpec
from collections.abc import Callable

import time
import logging
import requests


P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def with_retries(max_retries: int = 3, delay: float = 0.1, func_name: str | None = None):
    def decorator(func: Callable[P, R]):
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            for_args_str = f"for {', '.join(str(arg) for arg in args)}"
            error_log = (
                f"Error getting {func_name} {for_args_str}" if func_name else f"Error for {args}"
            )

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except requests.exceptions.HTTPError as e:
                    code = e.response.status_code
                    reason = e.response.reason

                    if code == 429 and attempt < max_retries:
                        logger.warning(
                            f"Ratelimited {for_args_str}. Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                        continue

                    else:
                        logger.error(f"{error_log}: {reason} [{code}]")
                        return None

                except requests.exceptions.RequestException as e:
                    if attempt < max_retries:
                        logger.warning(f"{error_log}: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"{error_log} after {max_retries} retries: {e}")
                        return None

                except Exception as e:
                    logger.error(f"{error_log}: {e}")
                    return None

            logger.error(f"{error_log} after {max_retries} retries")
            return None

        return wrapper

    return decorator
