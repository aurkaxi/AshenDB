import aiofiles
import aiofiles.os as aios

from .collection import Collection


# Database Class
class Database(str):
    def __init__(self, db_path: str):
        super().__init__()
        self.path = db_path

    async def get_collection(self, collection_name: str):
        """
        Get a single collection.
        """
        for name in await aios.listdir(self.path):
            if name == collection_name:
                return Collection(self.path + name + "/")
        raise Exception(f"Collection '{collection_name}' does not exist.")

    async def get_collections(self, collection_names: list = None):
        """
        Get multiple collections. If no collections are specified then all collections will be returned.
        """
        final = []
        for name in collection_names:
            final.append(await self.get_collection(name))
        return final

    async def create_collection(self, collection_name: str):
        """
        Create a single collection.
        """
        path = self.path + collection_name
        if await aios.path.exists(path):
            raise Exception(f"Collection '{collection_name}' already exists.")
        else:
            await aios.mkdir(path)
            return Collection(path + "/")

    async def create_collections(self, collection_names: list):
        """
        Create multiple collections.
        """
        final = []
        for name in collection_names:
            final.append(await self.create_collection(name))
        return final

    async def get_and_delete_collection(self, collection_name: str):
        """
        Delete a single collection.
        """
        path = self.path + collection_name
        if await aios.path.exists(path):
            await aios.removedirs(path)
            return
        else:
            raise Exception(f"Collection '{collection_name}' does not exist.")

    async def get_and_delete_collections(self, collection_names: list):
        """
        Delete multiple collections.
        """
        if collection_names is None:
            for name in await aios.listdir(self.path):
                await aios.removedirs(self.path + name)
            return
        for name in collection_names:
            await self.get_and_delete_collection(name)
        return
