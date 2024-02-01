import json
import asyncio
from copy import deepcopy
from typing import Optional

from models import AccountInfo


class Storage:

    def __init__(self, filename: str):
        self.filename = filename
        self.data = {}
        self.lock = asyncio.Lock()

    def init(self):
        with open(self.filename, 'r', encoding='utf-8') as file:
            if len(file.read().strip()) == 0:
                self.data = {}
                return
        with open(self.filename, 'r', encoding='utf-8') as file:
            converted_data = json.load(file)
        self.data = {a: AccountInfo.from_dict(i) for a, i in converted_data.items()}

    def get_final_account_info(self, address: str) -> Optional[AccountInfo]:
        info = self.data.get(address)
        if info is None:
            return None
        return deepcopy(info)

    def set_final_account_info(self, address: str, info: AccountInfo):
        self.data[address] = deepcopy(info)

    def remove(self, address: str):
        if address in self.data:
            self.data.pop(address)

    async def get_account_info(self, address: str) -> Optional[AccountInfo]:
        async with self.lock:
            return self.get_final_account_info(address)

    async def set_account_info(self, address: str, info: AccountInfo):
        async with self.lock:
            self.set_final_account_info(address, info)

    async def async_save(self):
        async with self.lock:
            self.save()

    def save(self):
        converted_data = {a: i.to_dict() for a, i in self.data.items()}
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(converted_data, file)
