import os
import re
import click
import click_config_file
from hac.components.MQTT import MQTT
from hac.components.Relay import Relay
from hac.validators.click.NotRequiredIf import NotRequiredIf

defaultConfigFile  = "{}/.config/hac/default.cfg".format(os.getenv('HOME'))

@click.group()
def clickcmd(ctx, debug, verbose):
    pass


@clickcmd.command(name="relay:on")
@click.option('--board',
              required=True,
              default="1",
              type=int,
              help="Board number")
@click.option('--name',
              required=True,
              type=str,
              cls=NotRequiredIf,
              not_required_if='number',
              help="Relay name")
@click.option('--type',
              required=True,
              default="pcf8574",
              type=click.Choice(['pcf8574', 'DockerPi', 'GPIO'], case_sensitive=True),
              help="Board type")
@click.option('--number',
              required=True,
              type=int,
              cls=NotRequiredIf,
              not_required_if='name',
              help="Relay number")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def relayON(ctx, board, type, name, number):
    relay = Relay(type)
    if name:
        number = relayGetID(board, name, ctx.default_map)
    relay.switch_on(number)


@clickcmd.command(name="relay:off")
@click.option('--board',
              required=True,
              default="1",
              type=int,
              help="Board number")
@click.option('--name',
              required=True,
              type=str,
              cls=NotRequiredIf,
              not_required_if='number',
              help="Relay name")
@click.option('--type',
              required=True,
              default="pcf8574",
              type=click.Choice(['pcf8574', 'DockerPi', 'GPIO'], case_sensitive=True),
              help="Board type")
@click.option('--number',
              required=True,
              type=int,
              cls=NotRequiredIf,
              not_required_if='name',
              help="Relay number")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def relayOFF(ctx, board, type, name, number):
    relay = Relay(type)
    if name:
        number = relayGetID(board, name, ctx.default_map)
    relay.switch_off(number)


@clickcmd.command(name="relay:daemon")
@click.option('--board',
              required=True,
              default="1",
              type=int,
              help="Board number")
@click.option('--type',
              required=True,
              default="pcf8574",
              type=click.Choice(['pcf8574', 'DockerPi', 'GPIO'], case_sensitive=True),
              help="Board type")
@click.option('--mqtt_prefix',
              required=True,
              type=str,
              help="mqtt prefix")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def relayDaemon(ctx, board, type, mqtt_prefix):

    config = ctx.default_map
    relay = Relay(type, board)

    def _on_message(client, userdata, message):
        print("Received from topic: {} message: {}".format(message.topic, message.payload.decode("utf-8")))
        match = (re.match(r"^{}(.*)$".format(mqtt_prefix), message.topic))
        if match and match.group(1) in relay.labels:
            if int(message.payload):
                relay.switch_on(match.group(1))
            else:
                relay.switch_off(match.group(1))

    mqtt = MQTT(config, onmessage=_on_message, subscribe=[(mqtt_prefix + label, 0) for label in relay.labels], type="daemon")
    mqtt.loop_forever()

def relayGetID(board, name, config):
    for key, value in config.items():
        match = (re.match(r"^relay_{}_(\d+)$".format(board), key))
        if match and value[0] == name:
            return int(match.group(1))
