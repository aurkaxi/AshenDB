import aiofiles
import json


class Document(dict):
    def __init__(self, filepath):
        self.filepath = filepath

    async def __ainit__(self):
        async with aiofiles.open(self.filepath, mode="r") as f:
            contents = await f.read()
            super().__init__(json.loads(contents))

    async def __aenter__(self):
        async with aiofiles.open(self.filepath, mode="r") as f:
            contents = await f.read()
            super().__init__(json.loads(contents))
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        async with aiofiles.open(self.filepath, mode="w") as f:
            contents = json.dumps(self)
            await f.write(contents)
        self.update(json.loads(contents))

    async def save(self):
        async with aiofiles.open(self.filepath, mode="w") as f:
            contents = json.dumps(self)
            await f.write(contents)
