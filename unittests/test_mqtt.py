import pytest
from fixtures import env
from low_voltage.mqtt import connect_to_mqtt

# import low_voltage.mqtt as connect_to_mqtt


@pytest.fixture
def mqtt(env):
    return connect_to_mqtt()


def test_connect(mqtt):
    assert mqtt is not None
