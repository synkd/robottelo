import pytest

from dynaconf import LazySettings
from dynaconf.validator import ValidationError
from robottelo.config.validators import VALIDATORS
from robottelo.logging import logger


settings = LazySettings(
    envvar_prefix="ROBOTTELO",
    core_loaders=["YAML"],
    settings_file="settings.yaml",
    preload=["conf/*.yaml"],
    includes=["settings.local.yaml", ".secrets.yaml", ".secrets_*.yaml"],
    envless_mode=True,
    lowercase_read=True,
    load_dotenv=True,
)

@pytest.fixture(scope='session')
def subscription_validators():
    SUBSCRIPTION_VALIDATORS = { k: VALIDATORS.get(k) for k in ['broker', 'content_host', 'libvirt', 'subscription',]}
    settings.validators.register(**SUBSCRIPTION_VALIDATORS)

    try:
        settings.validators.validate()
    except ValidationError as err:
        if settings.robottelo.settings.get('ignore_validation_errors'):
            logger.warning(f'Dynaconf validation failed with\n{err}')
        else:
            raise err
    return settings