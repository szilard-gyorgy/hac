import os
import click
import click_config_file
from w1thermsensor import W1ThermSensor


defaultConfigFile  = "{}/.config/hac/default.cfg".format(os.getenv('HOME'))


@click.group()
def clickcmd(ctx, debug, verbose):
    pass


@clickcmd.command(name="w1temp:list")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def w1TempList(ctx):
    for sensor in W1ThermSensor.get_available_sensors():
        click.echo("Sensor type: {} id: {}".format(sensor.type, sensor.id))


@clickcmd.command(name="w1temp:read")
@click.option('--sensor-id',
              required=True,
              help="Sensor ID")
@click.option('--sensor-type',
              required=True,
              default="40",
              type=int,
              help="Sensor TYPE")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def w1TempRead(ctx, sensor_id, sensor_type):
    sensor = W1ThermSensor(sensor_type, sensor_id)
    click.echo("{}°C".format(sensor.get_temperature()))
