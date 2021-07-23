#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: José Sánchez-Gallego (gallegoj@uw.edu)
# @Date: 2021-07-21
# @Filename: tl_camera.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import ctypes
import pathlib
from ctypes import (
    POINTER,
    c_bool,
    c_char,
    c_char_p,
    c_int,
    c_longlong,
    c_uint,
    c_ushort,
    c_void_p,
)
from dataclasses import dataclass
from enum import IntEnum
from functools import partial
from time import sleep

from typing import Optional

import numpy

from .exceptions import SDKError


CWD = pathlib.Path(__file__).parent.absolute()


tl_handle = c_void_p


SDK_FUNCTION_PROTOTYPES = {
    "open_sdk": [],
    "close_sdk": [],
    "discover_available_cameras": [c_char_p, c_int],
    "open_camera": [c_char_p, POINTER(tl_handle)],
    "close_camera": [tl_handle],
    "get_usb_port_type": [tl_handle, POINTER(c_int)],
    "get_camera_sensor_type": [tl_handle, POINTER(c_int)],
    "get_sensor_readout_time": [tl_handle, POINTER(c_int)],
    "get_is_armed": [tl_handle, POINTER(c_bool)],
    "get_exposure_time": [tl_handle, POINTER(c_longlong)],
    "get_exposure_time_range": [tl_handle, POINTER(c_longlong), POINTER(c_longlong)],
    "set_exposure_time": [tl_handle, c_longlong],
    "arm": [tl_handle, c_int],
    "disarm": [tl_handle],
    "issue_software_trigger": [tl_handle],
    "set_frames_per_trigger_zero_for_unlimited": [tl_handle, c_uint],
    "set_image_poll_timeout": [tl_handle, c_int],
    "get_pending_frame_or_null": [
        tl_handle,
        POINTER(POINTER(c_ushort)),
        POINTER(c_int),
        POINTER(POINTER(c_char)),
        POINTER(c_int),
    ],
    "get_image_height": [tl_handle, POINTER(c_int)],
    "get_image_width": [tl_handle, POINTER(c_int)],
}


def chk_err(sdk: TL_SDK, func_name: str, err: int) -> int:
    """SDK error handling."""

    if err > 0:
        last_error = sdk.libc.tl_camera_get_last_error().decode()
        raise SDKError(f"Function {func_name} failed with error {err}: {last_error}.")
    return err


class TL_SDK:
    """Thorlabs Camera SDK wrapper."""

    def __init__(self):

        self.is_sdk_open = False

        lib_path = "libthorlabs_tsi_camera_sdk.so"

        try:
            self.libc = ctypes.cdll.LoadLibrary(str(lib_path))
        except OSError as err:
            if "No such file or directory" in str(err):
                raise OSError(
                    f"Cannot open {lib_path}. The shared object file was not found. "
                    "Did you copy the libthorlabs libraries to /usr/local/lib?"
                )
            else:
                raise

        self.load_argtypes()

        self.libc.open_sdk()
        self.is_sdk_open = True

        # We need to run this once even if we know the serial of the camera to connect.
        self.list_available_cameras()

    def __del__(self):
        if self.is_sdk_open:
            self.libc.close_sdk()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def load_argtypes(self):
        """Load C types for SDK functions."""

        for func_name in SDK_FUNCTION_PROTOTYPES:
            func = self.libc.__getattr__("tl_camera_" + func_name)
            func.argtypes = SDK_FUNCTION_PROTOTYPES[func_name]
            func.restype = partial(chk_err, self, func_name)

            # Add shortcut for function names without the tl_camera prefix.
            setattr(self.libc, func_name, func)

        self.libc.tl_camera_get_last_error.restype = c_char_p

    def list_available_cameras(self) -> list[str]:
        """Returns a list of connected camera identifiers."""

        if not self.is_sdk_open:
            raise SDKError("SDK is not open.")

        buffer = ctypes.create_string_buffer(100)
        self.libc.tl_camera_discover_available_cameras(buffer, 100)

        cameras = buffer.value.decode().split()

        return cameras

    def open_camera(self, serial: str):
        """Opens a camera and returns a `.SDKCamera` object."""

        camera_serial = serial.encode() + b"\0"
        handle = c_void_p()

        self.libc.open_camera(camera_serial, handle)

        return SDKCamera(self, handle)

    def close(self):
        """Closes the SDK."""

        self.libc.close_sdk()


@dataclass
class SDKCamera:
    """An SDK camera."""

    sdk: TL_SDK
    handle: c_void_p

    def __post_init__(self):

        usb_type = c_int()
        self.sdk.libc.get_usb_port_type(self.handle, usb_type)
        self.usb_type = USB_PORT_TYPE(usb_type.value)

        sensor_type = c_int()
        self.sdk.libc.get_camera_sensor_type(self.handle, sensor_type)
        self.sensor_type = SENSOR_TYPE(sensor_type.value)

        readout_time = c_int()
        self.sdk.libc.get_sensor_readout_time(self.handle, readout_time)
        self.readout_time = readout_time.value  # ns

        min_exp_time = c_longlong()
        max_exp_time = c_longlong()
        self.sdk.libc.get_exposure_time_range(self.handle, min_exp_time, max_exp_time)
        self.exposure_time_range = (min_exp_time.value / 1e6, max_exp_time.value / 1e6)

        height = c_int()
        width = c_int()
        self.sdk.libc.get_image_height(self.handle, height)
        self.sdk.libc.get_image_width(self.handle, width)
        self.height = height.value
        self.width = width.value

    def __del__(self):
        self.sdk.libc.close_camera(self.handle)

    def is_armed(self):
        """Is the camera armed?"""

        is_armed = c_bool()
        self.sdk.libc.get_is_armed(self.handle, is_armed)
        return is_armed.value

    @property
    def exposure_time(self) -> float:
        """Return exposure time (seconds)."""

        exp_time = c_longlong()
        self.sdk.libc.get_exposure_time(self.handle, exp_time)
        return exp_time.value / 1e6

    @exposure_time.setter
    def exposure_time(self, value: float):

        exp_time_range = self.exposure_time_range
        if value < exp_time_range[0] or value > exp_time_range[1]:
            raise SDKError("Exposure time outside of valid range.")

        exp_time = c_longlong(int(value * 1e6))
        self.sdk.libc.set_exposure_time(self.handle, exp_time)

    def _get_frame(self):
        """Returns a frame as a Numpy array."""

        image_buffer = POINTER(c_ushort)()
        frame_count = c_int()
        metadata_pointer = POINTER(c_char)()
        metadata_size_in_bytes = c_int()
        self.sdk.libc.tl_camera_get_pending_frame_or_null(
            self.handle,
            image_buffer,
            frame_count,
            metadata_pointer,
            metadata_size_in_bytes,
        )

        if not image_buffer:
            return None

        image_buffer._wrapper = self
        image_buffer_as_array = numpy.ctypeslib.as_array(
            image_buffer,
            shape=(self.height, self.width),
        )

        self.sdk.libc.disarm(self.handle)

        return image_buffer_as_array

    def expose(self, exposure_time: Optional[float] = None) -> numpy.ndarray | None:
        """Expose and return a Numpy array. Blocks synchronously."""

        if self.is_armed():
            self.sdk.libc.disarm(self.handle)

        if exposure_time is not None:
            self.exposure_time = exposure_time

        self.sdk.libc.set_image_poll_timeout(self.handle, 100)
        self.sdk.libc.arm(self.handle, 1)
        self.sdk.libc.issue_software_trigger(self.handle)

        sleep(self.exposure_time)

        return self._get_frame()

    async def expose_async(
        self,
        exposure_time: Optional[float] = None,
    ) -> numpy.ndarray | None:
        """Expose and return a Numpy array. Blocks synchronously."""

        if self.is_armed():
            self.sdk.libc.disarm(self.handle)

        if exposure_time is not None:
            self.exposure_time = exposure_time

        self.sdk.libc.set_image_poll_timeout(self.handle, 100)
        self.sdk.libc.arm(self.handle, 1)
        self.sdk.libc.issue_software_trigger(self.handle)

        await asyncio.sleep(self.exposure_time)

        return self._get_frame()


class OPERATION_MODE(IntEnum):
    """The OPERATION_MODE enumeration defines the available modes for a camera."""

    # Use software operation mode to generate one or more frames
    # per trigger or to run continuous video mode.
    SOFTWARE_TRIGGERED = 0

    # Use hardware triggering to generate one or more frames per trigger
    # by issuing hardware signals.
    HARDWARE_TRIGGERED = 1

    # Use bulb-mode triggering to generate one or more frames per trigger
    # by issuing hardware signals. Please refer to the camera manual for
    # signalling details.
    BULB = 2

    RESERVED1 = 3  # Reserved for internal use.

    RESERVED2 = 4  # Reserved for internal use.


class SENSOR_TYPE(IntEnum):
    """This describes the physical capabilities of the camera sensor."""

    # Each pixel of the sensor indicates an intensity.
    MONOCHROME = 0

    # The sensor has a bayer-patterned filter overlaying it, allowing the camera
    # SDK to distinguish red, green, and blue values.
    BAYER = 1

    # The sensor has a polarization filter overlaying it allowing the camera to
    # capture polarization information from the incoming light.
    MONOCHROME_POLARIZED = 2


class TRIGGER_POLARITY(IntEnum):
    """Options available for specifying the hardware trigger polarity.

    These values specify which edge of the input trigger pulse that will
    initiate image acquisition.

    """

    # Acquire an image on the RISING edge of the trigger pulse.
    ACTIVE_HIGH = 0

    # Acquire an image on the FALLING edge of the trigger pulse.
    ACTIVE_LOW = 1


class DATA_RATE(IntEnum):
    """Options for setting the desired image data delivery rate."""

    RESERVED1 = 0  # A RESERVED value (DO NOT USE).
    RESERVED2 = 1  # A RESERVED value (DO NOT USE).
    FPS_30 = 2  # Sets the device to deliver images at 30 frames per second.
    FPS_50 = 3  # Sets the device to deliver images at 50 frames per second.


class USB_PORT_TYPE(IntEnum):
    """Values the SDK uses for specifying the USB bus speed.

    These values are returned by SDK API functions and callbacks based on the
    type of physical USB port that the device is connected to.

    """

    # The device is connected to a USB 1.0/1.1 port (1.5 Mbits/sec or 12 Mbits/sec).
    USB1_0 = 0

    # The device is connected to a USB 2.0 port (480 Mbits/sec).
    USB2_0 = 1

    # The device is connected to a USB 3.0 port (5000 Mbits/sec).
    USB3_0 = 2


class COMMUNICATION_INTERFACE(IntEnum):
    """Used to identify what interface the camera is currently using.

    If using USB, the specific USB version can also be identified using USB_PORT_TYPE.

    """

    GIG_E = 0  # The camera uses the GigE Vision (GigE) interface standard.
    LINK = 1  # The camera uses the CameraLink serial-communication-protocol standard.
    USB = 2  # The camera uses a USB interface.
