import cv2
import numpy as np
import pytest


@pytest.fixture
def sample_image():
    """A light canvas with a dark circle and a mid-gray box, 400x300."""
    img = np.full((300, 400, 3), 235, np.uint8)
    cv2.rectangle(img, (40, 40), (180, 260), (130, 130, 130), -1)
    cv2.circle(img, (290, 150), 70, (30, 30, 30), -1)
    return img


@pytest.fixture
def sample_png(sample_image):
    return cv2.imencode(".png", sample_image)[1].tobytes()
