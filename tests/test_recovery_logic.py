import pytest
from recovery_logic import get_recovery_action


def test_terminate_instances():
    actions = get_recovery_action({"Action": "TerminateInstances"})
    assert len(actions) == 4
    assert any("termination was authorized" in item for item in actions)


def test_stop_instances():
    actions = get_recovery_action({"Action": "StopInstances"})
    assert any("stopping the instance was intentional" in item for item in actions)


def test_security_group_change():
    actions = get_recovery_action({"Action": "AuthorizeSecurityGroupIngress"})
    assert any("security group rule changes" in item for item in actions)


def test_delete_vpc():
    actions = get_recovery_action({"Action": "DeleteVpc"})
    assert any("deleted networking resource" in item for item in actions)


def test_modify_instance_attribute():
    actions = get_recovery_action({"Action": "ModifyInstanceAttribute"})
    assert any("changed EC2 instance attributes" in item for item in actions)


def test_ssh_public_key():
    actions = get_recovery_action({"Action": "SendSSHPublicKey"})
    assert any("EC2 Instance Connect access" in item for item in actions)


def test_high_risk_fallback():
    actions = get_recovery_action({"Action": "UnknownAction", "RiskLevel": "HIGH"})
    assert any("high-risk infrastructure event" in item for item in actions)


def test_medium_risk_fallback():
    actions = get_recovery_action({"Action": "UnknownAction", "RiskLevel": "MEDIUM"})
    assert any("infrastructure configuration change" in item for item in actions)


def test_default_fallback():
    actions = get_recovery_action({"Action": "UnknownAction", "RiskLevel": "OTHER"})
    assert any("verify whether it was authorized" in item for item in actions)


def test_specific_action_takes_priority_over_risk():
    actions = get_recovery_action({"Action": "StopInstances", "RiskLevel": "HIGH"})
    assert any("stopping the instance was intentional" in item for item in actions)
    assert not any("high-risk infrastructure event" in item for item in actions)
