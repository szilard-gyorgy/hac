import os
import json
import click
import click_config_file
from hac.components.MQTT import MQTT
from hac.plugins.ufire.ise_ph import ise_ph
from hac.validators.value.variation import variation
from hac.validators.click.RequiredIf import RequiredIf


defaultConfigFile  = "{}/.config/hac/default.cfg".format(os.getenv('HOME'))


@click.group()
def clickcmd():
    pass


@clickcmd.command(name="ufire:temperature:read")
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
def ufileTemperatureRead(ctx, topic, tolerance, ph_ufire_address):
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


@clickcmd.command(name="ufire:ph:read")
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
def ufirePhRead(ctx, topic, tolerance, samples, ph_ufire_address):
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


@clickcmd.command(name="ufire:ph:calibrate")
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
def ufirePhCalibrate(ctx, flag, point, value, ph_ufire_address):
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
