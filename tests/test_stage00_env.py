import importlib.metadata as md
import os

import cv2
import onnxruntime as ort
import pytest

CV = {"opencv-python", "opencv-contrib-python", "opencv-python-headless", "opencv-contrib-python-headless"}

def test_only_one_opencv():
    names = {d.metadata["Name"].lower() for d in md.distributions()}
    assert names & CV == {"opencv-contrib-python"}

def test_charuco_api():
    assert hasattr(cv2.aruco, "CharucoDetector")

@pytest.mark.skipif(os.environ.get("KIMCAM_CPU") == "1", reason="jalur CPU")
def test_cuda_provider():
    ort.preload_dlls()
    assert "CUDAExecutionProvider" in ort.get_available_providers()
    # daftar provider tidak cukup: sesi jatuh diam-diam ke CPU bila DLL CUDA gagal dimuat
    from onnxruntime.datasets import get_example
    sess = ort.InferenceSession(get_example("sigmoid.onnx"), providers=["CUDAExecutionProvider"])
    assert sess.get_providers()[0] == "CUDAExecutionProvider"

def test_imports():
    import aniposelib  # noqa: F401
