"""WebUI tests for the Docker Image Tags feature.

:Requirement: Docker Image Tag

:CaseAutomation: Automated

:CaseLevel: Acceptance

:CaseComponent: ContainerManagement-Content

:team: Phoenix-content

:TestType: Functional

:CaseImportance: High

:Upstream: No
"""
from nailgun import entities
import pytest

from robottelo.constants import (
    CONTAINER_REGISTRY_HUB,
    CONTAINER_UPSTREAM_NAME,
    ENVIRONMENT,
    REPO_TYPE,
)


@pytest.fixture(scope="module")
def module_org():
    return entities.Organization().create()


@pytest.fixture(scope="module")
def module_product(module_org):
    return entities.Product(organization=module_org).create()


@pytest.fixture(scope="module")
def module_repository(module_product):
    repo = entities.Repository(
        content_type=REPO_TYPE['docker'],
        docker_upstream_name=CONTAINER_UPSTREAM_NAME,
        product=module_product,
        url=CONTAINER_REGISTRY_HUB,
    ).create()
    repo.sync(timeout=1440)
    return repo


@pytest.mark.skip_if_open("BZ:2009069")
@pytest.mark.tier2
def test_positive_search(session, module_org, module_product, module_repository):
    """Search for a docker image tag and reads details of it

    :id: 28640396-c44d-4487-9d6d-3d5f2ed599d7

    :expectedresults: The docker image tag can be searched and found,
        details are read

    :CaseLevel: Integration
    """
    with session:
        session.organization.select(org_name=module_org.name)
        search = session.containerimagetag.search('latest')
        assert module_product.name in [i['Product Name'] for i in search]
        assert module_repository.name in [i['Repository Name'] for i in search]
        values = session.containerimagetag.read('latest')
        assert module_product.name == values['details']['product']
        assert module_repository.name == values['details']['repository']
        assert values['lce']['table'][0]['Environment'] == ENVIRONMENT
