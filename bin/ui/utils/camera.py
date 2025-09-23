# pylint: disable=no-name-in-module
"""pass"""
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from bin.modules.logger_config import setup_logger
from bin.modules.mv_cam.camera_mv import CameraMVSDK
logger = setup_logger(__name__)


class CameraThread(QThread):
    """Thread camera handling"""
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_id: int = 0):
        super().__init__()
        self._camera = CameraMVSDK(camera_id)
        self._run_flag = True

        self._set_size(4000, 3000)
        self.set_exposure(30)

    def _set_size(self, width: int, height: int) -> None:
        """pass"""
        self._camera.set_size(width, height)

    def set_exposure(self, exposure_ms: int) -> None:
        """pass"""
        self._camera.set_camera_exposure(exposure_ms)

    def run(self):
        """pass"""
        logger.info("Starting the camera stream")
        try:
            while self._run_flag:
                frame = self._camera.get_frame()
                if frame.shape[2] == 1:  # if mono camera
                    frame_rgb = np.repeat(frame, 3, axis=2)  # → (H, W, 3)
                else:
                    frame_rgb = frame

                self.frame_ready.emit(frame_rgb)
                self.msleep(20)
        finally:
            logger.info("Closing the camera and ending the stream")
            self._camera.close()

    def stop(self):
        """Stopping the camera"""
        logger.info("Stopping the camera thread")
        self._run_flag = False
        try:
            self._camera.close()
        except Exception as e:
            logger.error(f"Error when closing the camera in 'stop': {e}")

        if self.isRunning():
            if not self.wait(3000):
                logger.warning("Forced termination of the camera stream")
                self.terminate()
                self.wait()
