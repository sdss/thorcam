#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2021-07-21
# @Filename: camera.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

from typing import Type

import astropy.time

from basecam.camera import BaseCamera, CameraEvent, CameraSystem
from basecam.exceptions import CameraConnectionError, ExposureError
from basecam.exposure import Exposure

from thorcam import __version__ as thorcam_version
from thorcam.tl_camera import TL_SDK


class ThorCamera(BaseCamera):
    """Thorlabs camera."""

    async def _connect_internal(self, **conn_params):
        """Internal method to connect the camera."""

        serial = self.uid

        if serial is None:
            raise CameraConnectionError("Unknown serial number.")

        assert isinstance(self.camera_system, ThorCameraSystem)
        self._sdk_camera = self.camera_system.sdk.open_camera(serial)

        if self._sdk_camera is None:
            raise CameraConnectionError(f"Cannot find camera with serial {serial}.")

    async def _expose_internal(self, exposure: Exposure, **kwargs) -> Exposure:

        image_type = exposure.image_type
        if image_type == "dark":
            raise ExposureError("Darks are not supported with this camera.")

        exposure.obstime = astropy.time.Time.now()

        data = await self._sdk_camera.expose_async(exposure.exptime)
        exposure.data = data

        return exposure


class ThorCameraSystem(CameraSystem[ThorCamera]):
    """Thorlabs camera system."""

    __version__ = thorcam_version

    camera_class = ThorCamera

    def __init__(self, *args, **kwargs):

        self.camera_class: Type[ThorCamera] = ThorCamera
        self.sdk = TL_SDK()

        super().__init__(*args, **kwargs)

    async def setup(self):
        """Loads the available cameras."""

        serials = self.list_available_cameras()
        for serial in serials:
            await self.add_camera(uid=serial)

        return self

    def list_available_cameras(self) -> list[str]:
        """Lists available cameras."""

        return self.sdk.list_available_cameras()

    async def start_camera_poller(self):
        raise NotImplementedError("This camera system does not allow polling.")

    async def disconnect(self):

        for camera in self.cameras:
            camera._sdk_camera.close()

        self.sdk.close()

        return await super().disconnect()
