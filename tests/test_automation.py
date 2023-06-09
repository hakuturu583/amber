from amber.automation.detic_image_labeler import DeticImageLabeler
from amber.automation.nerf_3d_reconstruction import Nerf3DReconstruction
from pathlib import Path
import os
from amber.dataset.images_dataset import ImagesDataset
import torch
import pytest


def test_detic_auto_labeler() -> None:
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    labeler = DeticImageLabeler(
        str(current_path / "automation" / "detic_image_labeler.yaml")
    )
    dataset = ImagesDataset(
        str(current_path / "rosbag" / "ford" / "ford.mcap"),
        str(current_path / "rosbag" / "ford" / "read_image.yaml"),
    )
    labeler.inference(dataset)


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="NeRF is too heavy for CPU machine."
)  # type: ignore
def test_nerf_3d_reconstruction() -> None:
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    labeler = Nerf3DReconstruction(
        str(current_path / "automation" / "nerf_3d_reconstruction.yaml")
    )
    dataset = ImagesDataset(
        str(current_path / "rosbag" / "soccer_goal"),
        str(current_path / "rosbag" / "soccer_goal" / "read_image.yaml"),
    )
    labeler.inference(dataset)
