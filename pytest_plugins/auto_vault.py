"""Plugin enables pytest to notify and update the requirements"""
import subprocess

from robottelo.utils.vault import Vault


def pytest_addoption(parser):
    """Options to allow user to update the requirements"""
    with Vault() as vclient:
        vclient.login(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
