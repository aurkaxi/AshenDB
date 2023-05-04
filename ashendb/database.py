import aiofiles
import aiofiles.os as aios
from typing import Generator

from .collection import Collection
from .exception import *


# Database Class
class Database:
    def __init__(self, db_path: str):
        super().__init__()
        self.path = db_path

    async def get_coll(self, collection_name: str) -> Collection:
        """Get a single collection.

        Args:
            collection_name: The name of the collection.

        Raises:
            NotFound: If the collection does not exist.

        Example:
            >>> coll = await db.get_coll("test")
            >>> coll
            <Collection: test>
        """
        for name in await aios.listdir(self.path):
            if name == collection_name:
                return Collection(self.path + name + "/")
        raise NotFound(f"Collection '{collection_name}' does not exist.")

    async def get_colls(self, collection_names: list[str] = None) -> list[Collection]:
        """Get multiple collections.

        If no collections are specified then all collections will be returned.

        Args:
            collection_names: The names of the collections.

        Raises:
            InvalidArgumentType: If the argument is not a list.
            NotFound: If one of the collections does not exist.

        Example:
            >>> colls = await db.get_colls(["test", "test2"])
            >>> colls
            [<Collection: test>, <Collection: test2>]

            >>> colls = await db.get_colls()
            >>> colls
            [<Collection: test>, <Collection: test2>, <Collection: test3>]
        """
        final = []
        if collection_names is None or len(collection_names) == 0:
            for name in collection_names:
                final.append(await self.get_coll(name))
            return final
        elif isinstance(collection_names, list) and len(collection_names) > 0:
            for name in await aios.listdir(self.path):
                final.append(Collection(self.path + name + "/"))
            return final
        else:
            raise InvalidArgumentType(f"Expected list, got {type(collection_names)}.")

    async def iterate_colls(
        self, collection_names: list[str] = None
    ) -> Generator[Collection, None, None]:
        """Iterate over multiple collections.

        If no collections are specified then all collections will be returned.

        Args:
            collection_names: The names of the collections.

        Raises:
            InvalidArgumentType: If the argument is not a list.
            NotFound: If one of the collections does not exist.

        Example:
            >>> async for coll in db.iterate_colls(["test", "test2"]):
            ...     print(coll)
            <Collection: test>
            <Collection: test2>

            >>> async for coll in db.iterate_colls():
            ...     print(coll)
            <Collection: test>
            <Collection: test2>
            <Collection: test3>

            >>> colls = [coll async for coll in db.iterate_colls()]
            >>> colls
            [<Collection: test>, <Collection: test2>, <Collection: test3>]
        """
        if collection_names is None or len(collection_names) == 0:
            for name in await aios.listdir(self.path):
                yield Collection(self.path + name + "/")
        elif isinstance(collection_names, list) and len(collection_names) > 0:
            for name in collection_names:
                yield await self.get_coll(name)
        else:
            raise InvalidArgumentType(f"Expected list, got {type(collection_names)}.")

    async def create_coll(self, collection_name: str) -> Collection:
        """Create a single collection.

        Args:
            collection_name: The name of the collection.

        Raises:
            AlreadyExists: If the collection already exists.

        Example:
            >>> coll = await db.create_coll("test")
            >>> coll
            <Collection: test>
        """
        path = self.path + collection_name
        if await aios.path.exists(path):
            raise AlreadyExists(f"Collection '{collection_name}' already exists.")
        else:
            await aios.mkdir(path)
            return Collection(path + "/")

    async def create_colls(self, collection_names: list[str]) -> list[Collection]:
        """Create multiple collections.

        Args:
            collection_names: The names of the collections.

        Raises:
            AlreadyExists: If one of the collections already exists.
            InvalidArgumentType: If the argument is not a list or Empty or No Argument was passed.

        Example:
            >>> colls = await db.create_colls(["test", "test2"])
            >>> colls
            [<Collection: test>, <Collection: test2>]
        """
        if (
            collection_names is None
            or len(collection_names) == 0
            or not isinstance(collection_names, list)
        ):
            raise InvalidArgumentType(
                f"Expected list, got {type(collection_names)} or Empty or No Argument was passed."
            )
        final = []
        for name in collection_names:
            final.append(await self.create_collection(name))
        return final

    async def iteeate_create_colls(
        self, collection_names: list[str]
    ) -> Generator[Collection, None, None]:
        """Create multiple collections.

        Args:
            collection_names: The names of the collections.

        Raises:
            AlreadyExists: If one of the collections already exists.
            InvalidArgumentType: If the argument is not a list or Empty or No Argument was passed.

        Example:
            >>> async for coll in db.iterate_create_colls(["test", "test2"]):
            ...     print(coll)
            <Collection: test>
            <Collection: test2>

            >>> colls = [coll async for coll in db.iterate_create_colls(["test", "test2"])]
            >>> colls
            [<Collection: test>, <Collection: test2>]
        """
        if (
            collection_names is None
            or len(collection_names) == 0
            or not isinstance(collection_names, list)
        ):
            raise InvalidArgumentType(
                f"Expected list, got {type(collection_names)} or Empty or No Argument was passed."
            )
        for name in collection_names:
            yield await self.create_collection(name)

    async def del_coll(self, collection_name: str) -> None:
        """Delete a single collection.

        Args:
            collection_name: The name of the collection.

        Raises:
            NotFound: If the collection does not exist.

        Example:
            >>> await db.delete_coll("test")
        """
        path = self.path + collection_name
        if await aios.path.exists(path):
            await aios.removedirs(path)
            return
        else:
            raise NotFound(f"Collection '{collection_name}' does not exist.")

    async def del_colls(self, collection_names: list[str]) -> None:
        """Delete multiple collections.

        If no collections are specified then all collections will be deleted.

        Args:
            collection_names: The names of the collections.

        Raises:
            NotFound: If one of the collections does not exist.

        Example:
            >>> await db.delete_colls(["test", "test2"])

            >>> await db.delete_colls()
        """
        if collection_names is None:
            for name in await aios.listdir(self.path):
                await aios.removedirs(self.path + name)
            return
        for name in collection_names:
            await self.get_and_delete_collection(name)
        return
