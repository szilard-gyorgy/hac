import sys
import os
import click
import click_config_file
import logging
import time
# from hac.libs.ise_probe.ise_ph import ise_ph
from hac.components.AtlasPH import AtlasPH
from hac.validators.click.RequiredIf import RequiredIf
from hac.validators.click.NotRequiredIf import NotRequiredIf
from hac.components.MQTT import MQTT
from hac.validators.value.variation import variation
from gpiozero import CPUTemperature


# ise = ise_ph(0x3f, 1)

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
    value = sensor.readPH()

    if topic:
        old_value = float(mqtt.topic_data[topic]) if topic in mqtt.topic_data else float(value)
        if abs(old_value - value) / value * 100 < tolerance:
            mqtt.publish(topic, round(value, 2))
        else:
            mqtt.publish(topic, '')
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
    value = CPUTemperature().temperature

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
            value = AtlasPH(address=config['ph_atlas_address']).readPH()
        elif sensor[0] == "temperature:cpu":
            value = CPUTemperature().temperature

        if sensor[1]:
            if sensor[1] in mqtt.topic_data:
                value = variation.filter_invalid(float(mqtt.topic_data[sensor[1]]), value, config['tolerance'])
            mqtt.publish(sensor[1], round(value, 2))

        else:
            click.echo("{}:{}".format(sensor[0], value))
