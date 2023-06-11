import os
from torch.utils.data import Dataset
from typing import Any, Dict, List
from yaml import safe_load  # type: ignore
from amber.exception import TaskDescriptionError
from dataclasses import dataclass
from dataclass_wizard import JSONWizard
import glob
import boto3


@dataclass
class MessageMetaData(JSONWizard):  # type: ignore
    sequence: int = 0
    topic: str = ""
    rosbag_path: str = ""


class Rosbag2Dataset(Dataset):  # type: ignore
    message_metadata: List[MessageMetaData] = []

    def __init__(
        self,
        rosbag_path: str,
        task_description_yaml_path: str,
        transform: Any = None,
        target_transform: Any = None,
    ) -> None:
        if os.path.isfile(rosbag_path):
            self.rosbag_files = [rosbag_path]
        else:
            self.rosbag_files = glob.glob(rosbag_path + "/**/*.mcap", recursive=True)
        self.transform = transform
        self.target_transform = target_transform
        self.task_description_yaml_path = task_description_yaml_path
        self.message_metadata.clear()

    def get_metadata(self, index: int) -> MessageMetaData:
        return self.message_metadata[index]


def download_rosbag(
    bucket_name: str,
    remote_rosbag_directory: str,
    remote_rosbag_filename: str,
    endpoint_url: str,
    download_dir: str = "/tmp/amber/remote_bags",
    aws_access_key_id: str = os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key: str = os.environ["AWS_SECRET_ACCESS_KEY"],
) -> str:
    s3 = boto3.resource(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    remote_rosbag_path = os.path.join(remote_rosbag_directory, remote_rosbag_filename)
    bucket = s3.Bucket(bucket_name)
    local_rosbag_path = os.path.join(download_dir, remote_rosbag_path)
    bucket.download_file(remote_rosbag_path, local_rosbag_path)
    return local_rosbag_path
