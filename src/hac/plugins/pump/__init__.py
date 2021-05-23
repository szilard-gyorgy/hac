import os
import click
import click_config_file
from hac.components.Stepper import Stepper

defaultConfigFile  = "{}/.config/hac/default.cfg".format(os.getenv('HOME'))


@click.group()
def clickcmd(ctx, debug, verbose):
    pass


@clickcmd.command(name="pump")
@click.option('--enable-pin',
              required=True,
              default="18",
              type=int,
              help="Enable PIN")
@click.option('--step-pin',
              required=True,
              default="17",
              type=int,
              help="Step PIN")
@click.option('--dir-pin',
              required=True,
              default="23",
              type=int,
              help="Direction PIN")
@click.option('--stop-pin',
              required=True,
              default="25",
              type=int,
              help="Stop PIN")
@click.option('--direction',
              required=True,
              default="forward",
              type=click.Choice(['forward', 'back'], case_sensitive=True),
              help="Direction")
@click.option('--delay',
              required=True,
              default="800",
              type=int,
              help="step per microseconds")
@click.option('--reversesteps',
              required=True,
              default="100",
              type=int,
              help="Revers number of steps when hit endstop")
@click.option('--steps',
              required=True,
              type=int,
              help="Number of steps to execute")
@click.pass_context
@click_config_file.configuration_option(config_file_name=defaultConfigFile)
def Pump(ctx, enable_pin, step_pin, dir_pin, stop_pin, direction, delay, reversesteps, steps):
    pump = Stepper(enable_pin, step_pin, dir_pin, stop_pin, delay, reversesteps)
    pump.run(steps, direction)
