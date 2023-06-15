from typing import Any
from abc import ABC, abstractmethod
from amber.dataset.images_dataset import Rosbag2Dataset
from mcap.writer import CompressionType, Writer
from typing import List, Dict
import json
from mcap.reader import NonSeekingReader
from mcap_ros2.writer import Writer
from mcap.records import Schema
from amber.dataset.schema import StringMessageSchema
from amber.exception import RosbagSchemaError


class Automation(ABC):
    @abstractmethod
    def __init__(self, yaml_path: str) -> None:
        pass

    @abstractmethod
    def inference(self, dataset: Rosbag2Dataset) -> Any:
        pass

    def write(
        self,
        dataset: Rosbag2Dataset,
        topic: str,
        annotation_data: List[Any],
        output_rosbag_path: str,
    ) -> None:
        annotation_json: Dict[str, List[Schema]] = {"annotations": []}
        rosbag_file = open(output_rosbag_path, "w+b")
        writer = Writer(rosbag_file)
        schema_dicts: Dict[str, Schema] = {}  # {schena name : schema}
        for rosbag_filepath in dataset.rosbag_files:
            reader = NonSeekingReader(rosbag_filepath)
            # Copy all topics
            for schema, channel, message in reader.iter_messages():
                if not schema.name in schema_dicts:
                    schema_dicts[schema.name] = writer.register_msgdef(
                        schema.name, schema.data.decode("utf-8")
                    )
                writer.write_message(
                    topic=channel.topic,
                    schema=schema_dicts[schema.name],
                    message=message,
                    log_time=message.log_time,
                    publish_time=message.publish_time,
                    sequence=message.sequence,
                )
        for annotation in annotation_data:
            annotation_json["annotations"].append(annotation.to_json())
        # Append annotation data
        annotation_schema = writer.register_msgdef(
            StringMessageSchema.name, StringMessageSchema.schema_text
        )
        annotation_schema.id = len(schema_dicts) + 1
        writer.write_message(
            topic=topic,
            schema=annotation_schema,
            message={"data": json.dumps(annotation_json)},
            sequence=0,
        )
        writer.finish()
        rosbag_file.close()
