import sys
import os
import re
import click
import click_config_file
import logging
import time
import json
from hac.libs.ise_probe.ise_ph import ise_ph
from hac.components.AtlasPH import AtlasPH
from hac.components.MQTT import MQTT
from hac.validators.click.RequiredIf import RequiredIf
from hac.validators.click.NotRequiredIf import NotRequiredIf
from hac.validators.value.variation import variation
from gpiozero import CPUTemperature


logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s]: %(message)s',
    level=logging.WARN,
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
defaultConfigFile  = "{}/.config/hac/default.cfg".format(os.getenv('HOME'))


@click.group()
@click.pass_context
@click.option('--debug/--no-debug', default=False)
@click.option('-v', '--verbose', count=True)
@click.version_option()
def main(ctx, debug, verbose):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['VERBOSE'] = verbose

    logging.StreamHandler(sys.stdout)
    if verbose:
        logger.setLevel(logging.INFO)
    if debug:
        logger.setLevel(logging.DEBUG)
    pass


@main.command(name="calibrate:ph:atlas")
@click.option('--info', 'flag',
              flag_value='info',
              is_flag=True,
              help="Check if device is calibrated")
@click.option('--clear', 'flag',
              flag_value='clear',
              is_flag=True,
              help="Delete calibration data")
@click.option('--set', 'flag', flag_value='set',
              is_flag=True,
              help="Calibration point (mid, low, high) with associated value ( ex: --point mid 7.00 )")
@click.option('--point',
              required=False,
              default="mid",
              type=click.Choice(['mid', 'low', 'high'], case_sensitive=True),
              help="Calibration point (mid or low or high)")
@click.option('--value',
              required=True,
              multiple=False,
              default="7.0",
              cls=RequiredIf,
              required_if='point',
              type=float,
              help="Calibration value")
@click.option('--address',
              required=False,
              default="99",
              type=int,
              help="PH sensor address")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def calibratePhAtlas(ctx, flag, point, value, address):
    commands = {
        "info": "Cal,?",
        "clear": "Cal, clear",
        "set": "Cal,{},{}".format(point, value)
    }

    sensor = AtlasPH(address=address)
    # print(sensor.readPH())

    if flag in commands.keys():
        print(sensor.query(commands[flag]))


@main.command(name="read:ph:atlas")
@click.option('--address',
              required=False,
              default="99",
              type=int,
              help="PH sensor address")
@click.option('--topic',
              required=False,
              default=False,
              type=str,
              help="Publish to mqtt topic")
@click.option('--tolerance',
              required=False,
              default=50,
              type=int,
              help="tolerance in %")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def readPhAtlas(ctx, address, topic, tolerance):

    if topic:
        mqtt = MQTT(ctx.default_map, subscribe=topic)

    sensor = AtlasPH(address=address)
    value = round(sensor.readPH(), 2)

    if topic:
        if topic in mqtt.topic_data:
            value = variation.filter_invalid(mqtt.topic_data[topic], value, tolerance)
        mqtt.publish(topic, value)
    else:
        click.echo(value)


@main.command(name="read:temperature:cpu")
@click.option('--topic',
              required=False,
              default=False,
              type=str,
              help="Publish to mqtt topic")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def readTemperatureCpu(ctx, topic):
    value = round(CPUTemperature().temperature, 2)

    if topic:
        mqtt = MQTT(ctx.default_map, subscribe=topic)
        mqtt.publish(topic, value)
    else:
        click.echo(value)


@main.command(name="read:temperature:multiple")
@click.option('--mqtt-sensor',
              required=False,
              default=False,
              multiple=True,
              cls=NotRequiredIf,
              not_required_if='text-sensor',
              type=(str, str),
              help="Read sensor and publish to mqtt topic (ex: --mqtt-sensor ph:atlas home/aquarium/ph \
                    --mqtt-sensor temperature:cpu home/aquarium/temperature/cpu")
@click.option('--text-sensor',
              required=False,
              default=False,
              multiple=True,
              cls=NotRequiredIf,
              not_required_if='mqtt-sensor',
              type=str,
              help="Read sensor and publish to mqtt topic (ex: --text-sensor ph:atlas \
                    --text-sensor temperature:cpu")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def multipleTemperatureRead(ctx, mqtt_sensor, text_sensor):
    config = ctx.default_map
    if mqtt_sensor:
        sensors = mqtt_sensor
        mqtt = MQTT(config, subscribe=[(sensor[1], 0) for sensor in sensors])
        time.sleep(config['mqtt_startup_delay'])
    else:
        sensors = [(sensor, False) for sensor in text_sensor]

    for sensor in sensors:
        if sensor[0] == "ph:atlas":
            value = round(AtlasPH(address=config['ph_atlas_address']).readPH(), 2)
        elif sensor[0] == "temperature:cpu":
            value = round(CPUTemperature().temperature, 2)
        elif sensor[0] == "ph:ufire":
            value = round(ise_ph(config['ph_ufire_address'], 1).measurepH(), 2)
        elif sensor[0] == 'temperature:ufire':
            value = ise_ph(config['ph_ufire_address'], 1).measureTemp()

        if sensor[1]:
            if sensor[1] in mqtt.topic_data:
                value = variation.filter_invalid(mqtt.topic_data[sensor[1]], value, config['tolerance'])
            mqtt.publish(sensor[1], value)

        else:
            click.echo("{}:{}".format(sensor[0], value))


@main.command(name="relay:on")
@click.option('--board',
              required=True,
              default="1",
              type=int,
              help="Board number")
@click.option('--type',
              required=True,
              default="pcf8574",
              type=click.Choice(['pcf8574', 'DockerPi'], case_sensitive=True),
              help="Board type")
@click.option('--name',
              required=True,
              type=str,
              help="Relay name")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def relayON(ctx, board, type, name):
    if type == 'pcf8574':
        from hac.components.PCF8574 import Relay
    else:
        from hac.components.DockerPi import Relay

    relay = Relay(board, ctx.default_map)
    relay.switch_on(name)


@main.command(name="relay:off")
@click.option('--board',
              required=True,
              default="1",
              type=int,
              help="Board number")
@click.option('--type',
              required=True,
              default="pcf8574",
              type=click.Choice(['pcf8574', 'DockerPi'], case_sensitive=True),
              help="Board type")
@click.option('--name',
              required=True,
              type=str,
              help="Relay name")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def relayOFF(ctx, board, type, name):
    if type == 'pcf8574':
        from hac.components.PCF8574 import Relay
    else:
        from hac.components.DockerPi import Relay

    relay = Relay(board, ctx.default_map)
    relay.switch_off(name)


@main.command(name="relay:daemon")
@click.option('--board',
              required=True,
              default="1",
              type=int,
              help="Board number")
@click.option('--type',
              required=True,
              default="pcf8574",
              type=click.Choice(['pcf8574', 'DockerPi'], case_sensitive=True),
              help="Board type")
@click.option('--mqtt_prefix',
              required=True,
              type=str,
              help="mqtt prefix")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def relayDaemon(ctx, board, type, mqtt_prefix):
    if type == 'pcf8574':
        from hac.components.PCF8574 import Relay
    else:
        from hac.components.DockerPi import Relay

    config = ctx.default_map
    relay = Relay(board, ctx.default_map)

    def _on_message(client, userdata, message):
        match = (re.match(r"^{}(.*)$".format(mqtt_prefix), message.topic))
        if match and match.group(1) in relay.labels:
            if int(message.payload):
                relay.switch_on(match.group(1))
            else:
                relay.switch_off(match.group(1))

    mqtt = MQTT(config, onmessage=_on_message, subscribe=[(mqtt_prefix + label, 0) for label in relay.labels])
    mqtt.loop_forever()


@main.command(name="read:temperature:ufire")
@click.option('--topic',
              required=False,
              default=False,
              type=str,
              help="Publish to mqtt topic")
@click.option('--tolerance',
              required=False,
              default=50,
              type=int,
              help="tolerance in %")
@click.option('--address', 'ph_ufire_address',
              required=False,
              default=0x3f,
              type=int,
              help="Sensor address")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def readTemperatureUfire(ctx, topic, tolerance, ph_ufire_address):
    if topic:
        mqtt = MQTT(ctx.default_map, subscribe=topic)

    ise = ise_ph(ph_ufire_address, 1)
    value = round(ise.measureTemp(), 3)

    if topic:
        if topic in mqtt.topic_data:
            value = variation.filter_invalid(mqtt.topic_data[topic], value, tolerance)
        mqtt.publish(topic, value)
    else:
        click.echo(value)


@main.command(name="read:ph:ufire")
@click.option('--topic',
              required=False,
              default=False,
              type=str,
              help="Publish to mqtt topic")
@click.option('--samples',
              required=False,
              default=3,
              type=int,
              help="AVG for Samples")
@click.option('--tolerance',
              required=False,
              default=50,
              type=int,
              help="tolerance in %")
@click.option('--address', 'ph_ufire_address',
              required=False,
              default=0x3f,
              type=int,
              help="Sensor address")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def readPhUfire(ctx, topic, tolerance, samples, ph_ufire_address):
    if topic:
        mqtt = MQTT(ctx.default_map, subscribe=topic)

    ise = ise_ph(ph_ufire_address, 1)
    values = []
    for x in range(0, samples):
        values.append(ise.measurepH())
    value = round(sum(values) / samples, 5)

    if topic:
        if topic in mqtt.topic_data:
            value = variation.filter_invalid(mqtt.topic_data[topic], value, tolerance)
        mqtt.publish(topic, value)
    else:
        click.echo(value)


@main.command(name="calibrate:ph:ufire")
@click.option('--info', 'flag',
              flag_value='info',
              is_flag=True,
              help="Check if device is calibrated")
@click.option('--clear', 'flag',
              flag_value='clear',
              is_flag=True,
              help="Delete calibration data")
@click.option('--set', 'flag', flag_value='set',
              is_flag=True,
              help="Calibration point (mid, low, high) with associated value ( ex: --point mid 7.00 )")
@click.option('--point',
              required=False,
              default="single",
              type=click.Choice(['single', 'low', 'high'], case_sensitive=True),
              help="Calibration point (mid or low or high)")
@click.option('--value',
              required=True,
              multiple=False,
              default="7.0",
              cls=RequiredIf,
              required_if='point',
              type=float,
              help="Calibration value")
@click.option('--address', 'ph_ufire_address',
              required=False,
              default=0x3f,
              type=int,
              help="PH sensor address")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def calibratePhUfire(ctx, flag, point, value, ph_ufire_address):
    ise = ise_ph(ph_ufire_address, 1)

    if flag == 'info':
        config = {
            "offset": str(ise.getCalibrateOffset()),
            "dual point": str(ise.usingDualPoint()),
            "low reference": {
                "reference": str(ise.getCalibrateLowReference()),
                "reading": str(ise.getCalibrateLowReading())
            },
            "high reference": {
                "reference": str(ise.getCalibrateHighReference()),
                "reading": str(ise.getCalibrateHighReading())
            },
            "temperature composation": str(ise.usingTemperatureCompensation())
        }
        click.echo(json.dumps(config, indent=4))
    elif flag == 'clear':
        ise.reset()
    elif flag == 'set':
        if point == 'single':
            ise.calibrateSingle(float(value))
        elif point == 'low':
            ise.calibrateProbeLow(float(value))
        elif point == 'high':
            ise.calibrateProbeHigh(float(value))
