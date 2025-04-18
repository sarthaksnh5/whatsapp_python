import os
from ast import literal_eval
from pathlib import Path

def get_env_variable(setting, default=None):
    """Returns the variable value from .env file or from system environment
    variable.

    Args:
        setting: variable name to fetch.
        default: value to use if variable is not found anywhere.

    Raises ImproperlyConfigured if variable is not found anywhere and a default
    is not specified.
    """
    def _load_env_file():
        env_path = Path('.env')
        if not env_path.exists():
            return None

        environ = {}
        with env_path.open() as env_file:
            for line in env_file:
                name, _, value = [c.strip() for c in line.partition('=')]
                if line.startswith('#') or line.isspace() or value is None:
                    continue
                environ[name] = literal_eval(value)

        return environ

    environ = _load_env_file() or os.environ
    try:
        return environ[setting]
    except KeyError:
        if default is not None:
            return default
        error_msg = f'Set the {setting} environment variable'
        raise NotImplementedError(error_msg) from None