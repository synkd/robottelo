import dynaconf
import pytest

from robottelo.config import settings
from robottelo.config.validators import VALIDATORS
from robottelo.logging import logger


def _try_validation(validator):
    try:
        settings.validators.validate(only=validator)
    except dynaconf.ValidationError as err:
        if settings.robottelo.settings.get('ignore_validation_errors'):
            logger.warning(f'Dynaconf validation failed with`n{err}')
        else:
            raise err
    return settings


@pytest.fixture(scope='session')
def validate_broker():
    settings.validators.register(**{'broker': VALIDATORS.get('broker')})
    _try_validation(['broker'])


@pytest.fixture(scope='session')
def validate_contenthost():
    settings.validators.register(**{'content_host': VALIDATORS.get('content_host')})
    _try_validation(['content_host'])


@pytest.fixture(scope='session')
def validate_libvirt():
    settings.validators.register(**{'libvirt': VALIDATORS.get('libvirt')})
    _try_validation(['libvirt'])


@pytest.fixture(scope='session')
def validate_subscription():
    settings.validators.register(**{'subscription': VALIDATORS.get('subscription')})
    _try_validation(['subscription'])
