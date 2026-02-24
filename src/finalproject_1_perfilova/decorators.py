import logging
from functools import wraps


def log_action(action_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_ctx = {
                "username": "-",
                "currency": "-",
                "amount": "-",
                "rate": "-",
                "base": "-",
            }

            try:
                result = func(*args, _log=log_ctx, **kwargs)

                logging.info(
                    f"{action_name} user='{log_ctx['username']}' "
                    f"currency='{log_ctx['currency']}' amount={log_ctx['amount']} "
                    f"rate={log_ctx['rate']} base='{log_ctx['base']}' result=OK"
                )
                return result

            except Exception as e:
                logging.info(
                    f"{action_name} user='{log_ctx['username']}' "
                    f"currency='{log_ctx['currency']}' amount={log_ctx['amount']} "
                    f"rate={log_ctx['rate']} base='{log_ctx['base']}' result=ERROR error='{e}'"
                )
                raise

        return wrapper

    return decorator