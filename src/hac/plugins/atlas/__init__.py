import os
import click
import click_config_file
from hac.components.MQTT import MQTT
from hac.plugins.atlas.AtlasPH import AtlasPH
from hac.validators.value.variation import variation
from hac.validators.click.RequiredIf import RequiredIf


defaultConfigFile  = "{}/.config/hac/default.cfg".format(os.getenv('HOME'))


@click.group()
def clickcmd(ctx, debug, verbose):
    pass


@clickcmd.command(name="atlas:ph:calibrate")
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
def atlasPhCalibrate(ctx, flag, point, value, address):
    commands = {
        "info": "Cal,?",
        "clear": "Cal, clear",
        "set": "Cal,{},{}".format(point, value)
    }

    sensor = AtlasPH(address=address)
    # print(sensor.readPH())

    if flag in commands.keys():
        print(sensor.query(commands[flag]))


@clickcmd.command(name="atlas:ph:read")
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
def atlasPhRead(ctx, address, topic, tolerance):

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
