import aiofiles, json
import aiofiles.os as aios

from .helper import match_data
from .document import Document


class Collection:
    def __init__(self, path):
        self.path = path

    async def get_documents(self, query: dict):
        for file in await aios.scandir(self.path):
            async with aiofiles.open(file.path, "r") as f:
                data = json.loads(await f.read())
                if await match_data(data, query):
                    async with Document(file.path) as doc:
                        yield doc

    async def get_document(self, id: str or int = None, query: dict = None):
        if id:
            return Document(f"{self.path}/{id}.json")
        elif query:
            async for document in self.get_documents(query):
                return document
        else:
            raise ValueError("Either id or query must be provided")
