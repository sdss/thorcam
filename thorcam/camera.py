#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2021-07-21
# @Filename: camera.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import Optional, Type, Union

from basecam.camera import BaseCamera, CameraConnectionError, CameraSystem
from basecam.exposure import Exposure, ImageNamer

from thorcam import __version__ as thorcam_version
from thorcam.tl_camera import TL_SDK


class ThorCamera(BaseCamera):
    """Thorlabs camera."""

    async def _connect_internal(self, **conn_params):
        """Internal method to connect the camera."""

        serial = self.uid

        if serial is None:
            raise CameraConnectionError("unknown serial number.")

        self._sdk_camera = self.camera_system.sdk.open_camera(serial)

        if self._sdk_camera is None:
            raise CameraConnectionError(f"cannot find camera with serial {serial}.")

    async def _expose_internal(self, exposure: Exposure, **kwargs) -> Exposure:
        return await super()._expose_internal(exposure, **kwargs)


class ThorCameraSystem(CameraSystem[ThorCamera]):
    """Thorlabs camera system."""

    __version__ = thorcam_version

    camera_class = ThorCamera

    def __init__(self, *args, **kwargs):

        self.camera_class: Type[ThorCamera] = ThorCamera
        self.sdk = TL_SDK()

        super().__init__(*args, **kwargs)

    def list_available_cameras(self) -> list[str]:

        return self.sdk.list_available_cameras()
