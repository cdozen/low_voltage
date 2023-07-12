import pytest
from fixtures import env
import low_voltage.mqtt as mqtt_mod


@pytest.fixture
def mqtt(env):
    return mqtt_mod


def test_connect(mqtt):
    assert True
