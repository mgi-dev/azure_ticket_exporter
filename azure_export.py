import csv
import json
import subprocess
from enum import Enum
from typing import List, Dict, Optional
from markdownify import markdownify

import config


class ItemTypeEnum(Enum):
    BUG = "bug"
    PRODUCT_BACKLOG_ITEM = "product backlog item"
    TASK = "task"
    EPIC = "epic"
    FEATURE = "feature"


class WorkItemDetail:
    id: int
    title: str
    type: ItemTypeEnum
    tags: List[str]
    status: str
    description: str
    azure_url: str
    parent: Optional[str]

    def __init__(self, raw_azure_item: dict):
        self.id = raw_azure_item.get("fields").get("System.Id")
        self.title = raw_azure_item.get("fields").get("System.Title")
        self.type = self._get_work_item_type(raw_azure_item)
        self.tags = self._get_work_item_tags(raw_azure_item)
        self.status = raw_azure_item.get("fields").get("System.State")
        self.description = raw_azure_item.get("fields").get("System.Description")
        self.azure_url = raw_azure_item.get("url")
        self.parent = None

    @staticmethod
    def _get_work_item_tags(details_work_item: Dict) -> List[str]:
        return [
            tag.lower().strip()
            for tag in details_work_item.get("fields").get("System.Tags", "").split(";")
        ]

    @staticmethod
    def _get_work_item_type(work_item_detail: Dict) -> ItemTypeEnum:
        return ItemTypeEnum(work_item_detail.get("fields").get("System.WorkItemType", "").lower().strip())

    def as_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type.value,
            "tags": self.tags,
            "status": self.status,
            "description": markdownify(self.description) if self.description else None,
            "azure_url": self.azure_url,
            "parent": self.parent if self.parent else None
        }


def exec_cmd(cmd: str):
    """Wrapper to run shell commands in a python script."""
    try:
        res = subprocess.run(cmd, shell=True, check=True, capture_output=True)

    except subprocess.CalledProcessError as err:
        raise Exception(err.stderr.decode().strip())
    else:
        return res.stdout.decode().strip()


def get_raw_work_item(work_item_id: int) -> Dict:
    cmd = f"az boards work-item show --organization {config.BASE_URL} --id {work_item_id}"
    try:
        details_str = exec_cmd(cmd)
        details = json.loads(details_str)
        return details
    except Exception as e:
        print(e.args)
        raise


def get_parent(raw_work_item: Dict) -> Optional[WorkItemDetail]:
    parent_id = raw_work_item.get("fields").get("System.Parent")
    if parent_id:
        return WorkItemDetail(get_raw_work_item(parent_id))


def export_to_csv(work_items: List[WorkItemDetail], path: str):
    with open(path, "w") as csv_file:
        fieldnames = list(work_items[0].as_dict().keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for work_item in work_items:
            writer.writerow(work_item.as_dict())


def main():
    work_item_ids_to_extract = config.ITEMS_TO_EXPORT
    work_items = []
    for work_item_id in work_item_ids_to_extract:
        raw_work_item = get_raw_work_item(work_item_id)
        work_item = WorkItemDetail(raw_work_item)
        parent = get_parent(raw_work_item)
        work_item.parent = parent.title if parent else None
        work_items.append(work_item)
    export_to_csv(work_items, config.FILE_NAME_EXTRACT)


if __name__ == '__main__':
    main()



