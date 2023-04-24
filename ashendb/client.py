import aiofiles
import aiofiles.os as aios
from typing import Generator

from .database import Database
from .exception import *


# Client Class
class AshenDB(str):
    """
    Entry point for AshenDB. This class is used to create, get, and delete databases.

    Attributes:
        base: The path. Which is always ".ashendb/". You are not supposed to change this.
    """

    base: str = ".ashendb/"

    @classmethod
    async def get_db(cls, db_name: str) -> Database:
        """Get a single database from database name.

        Args:
            db_name: The name of the database.

        Raises:
            NotFound: If the database does not exist.
        """
        for name in await aios.listdir(cls.base):
            if name == db_name:
                return Database(cls.base + name + "/")
        raise NotFound(f"Database '{db_name}' does not exist.")

    @classmethod
    async def get_dbs(
        cls, db_names: list[str] = None
    ) -> Generator[Database, None, None]:
        """Get multiple databases.

        From a list of database names. If no list is provided or the list is empty, all databases are returned.

        Args:
            db_names: A list of database names.

        Raises:
            NotFound: If a database does not exist.
            InvalidArgumentType: If the argument is not a list.

        Yields:
            Database: A database.

        Example:
            >>> async for db in AshenDB.get_dbs(["db1", "db2"]):
            >>>     print(db.name)
            db1
            db2

            >>> async for db in AshenDB.get_dbs():
            >>>     print(db.name)
            db1
            db2
            db3
            ...

            >>> async for db in AshenDB.get_dbs([]):
            >>>     print(db.name)
            db1
            db2
            db3
            ...

            >>> dbs = [db async for db in AshenDB.get_dbs()]
            >>> print(dbs)
            [db1, db2, db3, ...]


        Notes:
            This is a generator. You must use a for loop to iterate through it. If you want to get a list, use list comprehension. See the last example.
        """

        if db_names is None or len(db_names) == 0:
            for name in await aios.listdir(cls.base):
                yield Database(cls.base + name + "/")
        elif isinstance(db_names, list) and len(db_names) > 0:
            for name in db_names:
                yield await cls.get_db(name)
        else:
            raise InvalidArgumentType(f"Expected list, got {type(db_names)}.")
        return

    @classmethod
    async def create_db(cls, db_name: str) -> Database:
        """Creates a single database.

        Args:
            db_name: The name of the database.

        Raises:
            AlreadyExists: If the database already exists.
        """
        path = cls.base + db_name
        if await aios.path.exists(path):
            raise AlreadyExists(f"Database '{db_name}' already exists.")
        else:
            await aios.mkdir(path)
            return Database(path + "/")

    @classmethod
    async def create_dbs(cls, db_names: list):
        """
        Create multiple databases.
        """
        for name in db_names:
            yield await cls.create_one(name)

    @classmethod
    async def get_and_delete_db(cls, db_name: str):
        """
        Delete a single database.
        """
        path = cls.base + db_name
        if await aios.path.exists(path):
            await aios.removedirs(path)
            return
        else:
            raise Exception(f"Database '{db_name}' does not exist.")

    @classmethod
    async def get_and_delete_dbs(cls, db_names: list):
        """
        Delete multiple databases.
        """
        if db_names is None:
            for name in await aios.listdir(cls.base):
                await cls.get_and_delete_one(name)
            return
        for name in db_names:
            await cls.get_and_delete_one(name)
        return
