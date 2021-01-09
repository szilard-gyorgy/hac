import os
import re
import click
import click_config_file
from hac.components.MQTT import MQTT


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


@clickcmd.command(name="relay:off")
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


@clickcmd.command(name="relay:daemon")
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
        print("Received from topic: {} message: {}".format(message.topic, message.payload.decode("utf-8")))
        match = (re.match(r"^{}(.*)$".format(mqtt_prefix), message.topic))
        if match and match.group(1) in relay.labels:
            if int(message.payload):
                relay.switch_on(match.group(1))
            else:
                relay.switch_off(match.group(1))

    mqtt = MQTT(config, onmessage=_on_message, subscribe=[(mqtt_prefix + label, 0) for label in relay.labels], type="daemon")
    mqtt.loop_forever()
