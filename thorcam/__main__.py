#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2021-07-20
# @Filename: __main__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import os

import click
from click_default_group import DefaultGroup

from sdsstools.daemonizer import DaemonGroup, cli_coro

from thorcam import config
from thorcam.actor import ThorActor
from thorcam.camera import ThorCameraSystem


@click.group(cls=DefaultGroup, default="actor", default_if_no_args=True)
def thorcam():
    """Command Line Interface for Thorlabs Zelux CMOS cameras."""

    pass


@thorcam.group(cls=DaemonGroup, prog="thorcam-actor", workdir=os.getcwd())
@cli_coro()
async def actor():
    """Start/stop the actor as a daemon."""

    thorcam = ThorCameraSystem()
    await thorcam.start_camera_poller()

    thor_actor = ThorActor.from_config(config["actor"], thorcam)
    await thor_actor.start()

    await thor_actor.run_forever()


def main():
    thorcam(obj={}, auto_envvar_prefix="thorcam")


if __name__ == "__main__":
    main()
