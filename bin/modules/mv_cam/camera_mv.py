# pylint: disable=invalid-name, logging-fstring-interpolation
"""pass"""
import platform
import numpy as np
import bin.modules.mv_cam.mvsdk as mvsdk
from bin.modules.logger_config import setup_logger

logger = setup_logger(__name__)


class CameraMVSDK:
    """Class for working with cameras MV SDK"""
    EXPOSURE_DEFAULT = 30  # ms

    def __init__(self, camera_index: int = 0):
        camera_list = mvsdk.CameraEnumerateDevice()
        if len(camera_list) < 1:
            raise RuntimeError("No camera was found!")

        camera_info = camera_list[camera_index]
        self.hCamera = 0
        try:
            self.hCamera = mvsdk.CameraInit(camera_info, -1, -1)
        except mvsdk.CameraException as e:
            print(f"CameraInit Failed({e.error_code}): {e.message}")

        # camera characteristics
        self.cap = mvsdk.CameraGetCapability(self.hCamera)
        self.max_width = self.cap.sResolutionRange.iWidthMax
        self.max_height = self.cap.sResolutionRange.iHeightMax

        self.mono_camera = self.cap.sIspCapacity.bMonoSensor != 0
        if self.mono_camera:
            mvsdk.CameraSetIspOutFormat(
                self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        else:
            mvsdk.CameraSetIspOutFormat(
                self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

        # default maximum resolution
        self.set_size(self.max_width, self.max_height)

        # camera to continuous shooting mode
        mvsdk.CameraSetTriggerMode(self.hCamera, 0)
        # manual exposure mode
        mvsdk.CameraSetAeState(self.hCamera, 0)

        mvsdk.CameraPlay(self.hCamera)

        frame_buffer_size = self.max_width * \
            self.max_height * (1 if self.mono_camera else 3)
        # image storage buffer
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(frame_buffer_size, 16)

    def set_size(self, width: int, height: int):
        """Setting the camera resolution"""
        # Stopping the camera before changing the parameters
        mvsdk.CameraStop(self.hCamera)

        current_settings = mvsdk.CameraGetImageResolution(self.hCamera)

        # calculating the offset for centering the ROI
        h_offset = (self.max_width - width) // 2
        v_offset = (self.max_height - height) // 2

        # new parameters ROI
        current_settings.iIndex = 255
        current_settings.iHOffsetFOV = h_offset
        current_settings.iVOffsetFOV = v_offset
        current_settings.iWidthFOV = width
        current_settings.iHeightFOV = height
        current_settings.iWidth = width
        current_settings.iHeight = height

        # apply
        mvsdk.CameraSetImageResolution(self.hCamera, current_settings)

        # freeing the old buffer
        if hasattr(self, 'pFrameBuffer') and self.pFrameBuffer:
            mvsdk.CameraAlignFree(self.pFrameBuffer)

        # allocate a new buffer for the current resolution
        frame_buffer_size = width * height * (1 if self.mono_camera else 3)
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(frame_buffer_size, 16)

        self.set_camera_exposure(self.EXPOSURE_DEFAULT)
        mvsdk.CameraPlay(self.hCamera)

    def set_camera_exposure(self, exposure_ms):
        """Camera exposure time in milliseconds"""
        # Converting milliseconds to microseconds for the API
        exposure_time = exposure_ms * 1000

        max_fps = 1000 / exposure_ms if exposure_ms > 0 else 30
        target_fps = min(max_fps, 90)

        logger.debug(f"Exposure: {exposure_ms} ms")
        logger.debug(f"Target FPS: {target_fps:.1f}")

        # setting exposure and frame rate
        mvsdk.CameraSetFrameSpeed(self.hCamera, 2)  # high speed
        mvsdk.CameraSetExposureTime(self.hCamera, exposure_time)

        logger.info(
            f"The parameters are set - Exposure: {exposure_ms} ms, FPS: {target_fps:.1f}")

    def get_frame(self):
        """Getting a single frame from the camera"""
        pRawData, frame_head = mvsdk.CameraGetImageBuffer(self.hCamera, 1000)
        mvsdk.CameraImageProcess(
            self.hCamera, pRawData, self.pFrameBuffer, frame_head)
        mvsdk.CameraReleaseImageBuffer(self.hCamera, pRawData)

        # Converting the buffer to OpenCV
        if platform.system() == "Windows":
            mvsdk.CameraFlipFrameBuffer(self.pFrameBuffer, frame_head, 1)

        frame_data = (mvsdk.c_ubyte *
                      frame_head.uBytes).from_address(self.pFrameBuffer)
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = frame.reshape((frame_head.iHeight, frame_head.iWidth,
                              1 if frame_head.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3))

        return frame

    def __del__(self):
        """Closing the camera and freeing up resources"""
        self.close()

    def close(self):
        """Freeing the camera and buffer"""
        try:
            mvsdk.CameraPause(self.hCamera)
            mvsdk.CameraStop(self.hCamera)
            mvsdk.CameraUnInit(self.hCamera)
            if hasattr(self, "pFrameBuffer") and self.pFrameBuffer:
                mvsdk.CameraAlignFree(self.pFrameBuffer)
                self.pFrameBuffer = None
            logger.info("The camera is closed and resources are released")
        except Exception as e:
            logger.error(f"Error when releasing the camera: {e}")
