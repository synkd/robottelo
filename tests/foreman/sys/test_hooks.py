"""Test class for Foreman Hooks

:Requirement: Foreman Hooks

:CaseAutomation: Automated

:CaseLevel: System

:CaseComponent: HooksPlugin

:Assignee: rdrazny

:TestType: Functional

:CaseImportance: High

:Upstream: No
"""
import pytest
from fauxfactory import gen_ipaddr
from nailgun import entities
from requests.exceptions import HTTPError

from robottelo import ssh
from robottelo.datafactory import valid_hostgroups_list
from robottelo.datafactory import valid_hosts_list

HOOKS_DIR = '/usr/share/foreman/config/hooks'
LOGS_DIR = '/usr/share/foreman/tmp/hooks.log'
SCRIPT_PATH = f'{HOOKS_DIR}/logger.sh'


pytestmark = [pytest.mark.run_in_one_thread, pytest.mark.destructive]


@pytest.fixture(scope='function')
def logger_hook(default_org):
    """Create logger script to be executed via hooks"""
    ssh.command(
        '''printf '#!/bin/sh\necho "$(date): Executed $1 hook'''
        + f''' on object $2" > {LOGS_DIR}' > {SCRIPT_PATH}'''
    )
    ssh.command(f'chmod 774 {SCRIPT_PATH}')
    ssh.command(f'chown foreman:foreman {SCRIPT_PATH}')
    ssh.command(f'restorecon -RvF {HOOKS_DIR}')
    yield

    ssh.command(f'rm -rf {HOOKS_DIR}/*')


def test_positive_host_hooks(logger_hook):
    """Create hooks to be executed on host create, update and destroy

    :id: 4fe35fda-1524-44f7-9221-96d1aeafc75c

    :Steps:
        1. Create hook directories with symlinks to logger script
        for subset of supported events: create, update, destroy
        2. Perform trigger actions (create, update and delete host)
        3. Observe custom logs created by hook script

    :expectedresults: hook scripts are executed at proper time
    """
    host_name = valid_hosts_list()[0]
    expected_msg = 'Executed {0} hook on object {1}'

    # create hook destination directories with logger script
    create_event = 'create'
    update_event = 'update'
    destroy_event = 'destroy'
    for event in [create_event, destroy_event, update_event]:
        hook_dir = f'{HOOKS_DIR}/host/managed/{event}'
        ssh.command(f'mkdir -p {hook_dir}')
        ssh.command(f'ln -sf {SCRIPT_PATH} {hook_dir}/')
    result = ssh.command('systemctl restart httpd')
    assert result.return_code == 0

    # delete host, check logs for hook activity
    host = entities.Host(name=host_name).create()
    assert host.name == f'{host_name}.{host.domain.read().name}'
    result = ssh.command(f'cat {LOGS_DIR}')
    assert result.return_code == 0
    assert expected_msg.format(create_event, host_name) in result.stdout[0]

    # update host, check logs for hook activity
    new_ip = gen_ipaddr()
    host.ip = new_ip
    host = host.update(['ip'])
    assert host.ip == new_ip
    result = ssh.command(f'cat {LOGS_DIR}')
    assert result.return_code == 0
    assert expected_msg.format(update_event, host_name) in result.stdout[0]

    # delete host, check logs for hook activity
    host.delete()
    with pytest.raises(HTTPError):
        host.read()
    result = ssh.command(f'cat {LOGS_DIR}')
    assert result.return_code == 0
    assert expected_msg.format(destroy_event, host_name) in result.stdout[0]


def test_positive_hostgroup_hooks(logger_hook, default_org):
    """Create hooks to be executed on hostgroup create, udpdate and destroy

    :id: 7e935dec-e4fe-47d8-be02-8c687a99ae7a

    :steps:
        1. Create hook directories with symlinks to logger script
        for subset of supported events: before_create, before_update,
        before_destroy
        2. Perform trigger actions (create, update and delete host group)
        3. Observe custom logs created by hook script

    :expectedresults: hook scripts are executed at proper time
    """
    hg_name = valid_hostgroups_list()[0]
    expected_msg = 'Executed {0} hook on object {1}'

    # create hook destination directories with logger script
    create_event = 'before_create'
    update_event = 'before_update'
    destroy_event = 'before_destroy'
    for event in [create_event, update_event, destroy_event]:
        hook_dir = f'{HOOKS_DIR}/hostgroup/{event}'
        ssh.command(f'mkdir -p {hook_dir}')
        ssh.command(f'ln -sf {SCRIPT_PATH} {hook_dir}/')
    result = ssh.command('systemctl restart httpd')
    assert result.return_code == 0

    # create hg, check logs for hook activity
    hg = entities.HostGroup(name=hg_name, organization=[default_org.id]).create()
    assert hg.name == hg_name
    result = ssh.command(f'cat {LOGS_DIR}')
    assert result.return_code == 0
    assert expected_msg.format(create_event, hg_name) in result.stdout[0]

    # update hg, check logs for hook activity
    new_arch = entities.Architecture().create()
    hg.architecture = new_arch
    hg = hg.update(['architecture'])
    assert hg.architecture.read().name == new_arch.name
    result = ssh.command(f'cat {LOGS_DIR}')
    assert result.return_code == 0
    assert expected_msg.format(update_event, hg_name) in result.stdout[0]

    # delete hg, check logs for hook activity
    hg.delete()
    with pytest.raises(HTTPError):
        hg.read()
    result = ssh.command(f'cat {LOGS_DIR}')
    assert result.return_code == 0
    assert expected_msg.format(destroy_event, hg_name) in result.stdout[0]
