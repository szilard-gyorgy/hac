import os
import click
import click_config_file
from hac.components.MQTT import MQTT
from gpiozero import CPUTemperature


defaultConfigFile  = "{}/.config/hac/default.cfg".format(os.getenv('HOME'))


@click.group()
def clickcmd(ctx, debug, verbose):
    pass


@clickcmd.command(name="read:temperature:cpu")
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
