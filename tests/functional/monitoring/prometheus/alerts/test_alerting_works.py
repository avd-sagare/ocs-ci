import logging

from flaky import flaky
import pytest

from ocs_ci.framework.pytest_customization.marks import (
    tier1,
    blue_squad,
    provider_mode,
)
from ocs_ci.ocs import constants
from ocs_ci.ocs.ocp import OCP
import ocs_ci.utility.prometheus


log = logging.getLogger(__name__)


@blue_squad
def test_alerting_works(threading_lock):
    """
    If alerting works then there is at least one alert.
    """
    prometheus = ocs_ci.utility.prometheus.PrometheusAPI(threading_lock=threading_lock)
    alerts_response = prometheus.get(
        "alerts", payload={"silenced": False, "inhibited": False}
    )
    assert alerts_response.ok is True
    alerts = alerts_response.json()["data"]["alerts"]
    log.info(f"Prometheus Alerts: {alerts}")
    assert len(alerts) > 0


@provider_mode
@blue_squad
@pytest.mark.polarion_id("OCS-2503")
@tier1
@flaky(max_runs=3)
def test_prometheus_rule_failures(threading_lock):
    """
    There should be no PrometheusRuleFailures alert when OCS is configured.
    """
    prometheus = ocs_ci.utility.prometheus.PrometheusAPI(threading_lock=threading_lock)
    alerts_response = prometheus.get(
        "alerts", payload={"silenced": False, "inhibited": False}
    )
    assert alerts_response.ok is True
    alerts = alerts_response.json()["data"]["alerts"]
    log.info(f"Prometheus Alerts: {alerts}")
    assert constants.ALERT_PROMETHEUSRULEFAILURES not in [
        alert["labels"]["alertname"] for alert in alerts
    ]


def setup_module(module):
    ocs_obj = OCP()
    module.original_user = ocs_obj.get_user_name()


def teardown_module(module):
    ocs_obj = OCP()
    ocs_obj.login_as_user(module.original_user)
