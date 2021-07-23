#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2021-07-22
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from typing import Optional

<<<<<<< HEAD
from basecam.actor import CameraActor
=======
from basecam.actor import BaseCameraActor
from clu.legacy import LegacyActor
>>>>>>> ecd1831e08fc66f98cdf5d67fac75bb571156315

from thorcam.camera import ThorCameraSystem


<<<<<<< HEAD
class ThorActor(CameraActor):
=======
class ThorActor(BaseCameraActor, LegacyActor):
>>>>>>> ecd1831e08fc66f98cdf5d67fac75bb571156315
    """Thorcam actor."""

    def __init__(
        self,
        camera_system: ThorCameraSystem,
        *args,
        data_dir: Optional[str] = None,
        image_name: Optional[str] = None,
        **kwargs,
    ):

        self.camera_system = camera_system
<<<<<<< HEAD
        super().__init__(camera_system, *args, validate=False, **kwargs)
=======
        super().__init__(camera_system, *args, **kwargs)
>>>>>>> ecd1831e08fc66f98cdf5d67fac75bb571156315

        # The default image namer writes to ./ For production we want to write to /data.
        _data_dir: str = data_dir or "/data/tcam"
        _image_name: str = image_name or "thorcam-{num:04d}.fits"

        camera_class = self.camera_system.camera_class

        camera_class.image_namer.dirname = _data_dir
        camera_class.image_namer.basename = _image_name
        camera_class.fits_model.context.update({"__actor__": self})

        # If the actor is started from __main__.py, the camera_system is already
        # running and cameras may be attached. The changes above won't affect the
        # instance attributes of those cameras. We need to change the image namer
        # and fits_model of any already connected camera.
        for camera in self.camera_system.cameras:
            camera.image_namer.basename = _image_name
            camera.image_namer.dirname = _data_dir
            camera.image_namer.camera = camera
            camera.fits_model.context.update({"__actor__": self})
