import aiofiles.os as aios
from typing import Generator

from .database import Database
from .exception import *


# Client Class
class AshenDB:
    """
    Entry point for AshenDB. This class is used to create, get, and delete databases.

    """

    base: str = ".ashendb/"

    @classmethod
    async def get_db(cls, db_name: str) -> Database:
        """Get a single database from database name.

        Args:
            db_name: The name of the database.

        Raises:
            NotFound: If the database does not exist.

        Example:
            >>> db = await AshenDB.get_db("test")
            >>> db
            <Database: test>
        """
        db_name = str(db_name)
        for name in await aios.listdir(cls.base):
            if name == db_name:
                return Database(cls.base + name + "/")
        raise NotFound(f"Database '{db_name}' does not exist.")

    @classmethod
    async def get_dbs(cls, db_names: list[str] = None) -> list[Database]:
        """Get multiple databases from list of database names.

        If no list is provided or the list is empty, all databases are returned.

        Args:
            db_names: The names of the databases.

        Raises:
            InvalidArgumentType: If the argument is not a list.
            NotFound: If one of the databases does not exist.

        Example:
            >>> dbs = await AshenDB.get_dbs(["test", "test2"])
            >>> dbs
            [<Database: test>, <Database: test2>]

            >>> dbs = await AshenDB.get_dbs()
            >>> dbs
            [<Database: test>, <Database: test2>, <Database: test3>]
        """
        final = []
        if db_names is None or len(db_names) == 0:
            for name in await aios.listdir(cls.base):
                final.append(Database(cls.base + name + "/"))
        elif isinstance(db_names, list) and len(db_names) > 0:
            for name in db_names:
                final.append(await cls.get_db(name))
        else:
            raise InvalidArgumentType(f"Expected list, got {type(db_names)}.")

        return final

    @classmethod
    async def iterate_dbs(cls, db_names: list[str]) -> Generator[Database, None, None]:
        """Iterate over multiple databases from list of database names.

        Args:
            db_names: The names of the databases.

        Raises:
            InvalidArgumentType: If the argument is not a list.
            NotFound: If one of the databases does not exist.

        Example:
            >>> async for db in AshenDB.iterate_dbs(["test", "test2"]):
            ...     print(db)
            <Database: test>
            <Database: test2>

            >>> dbs = [db async for db in AshenDB.iterate_dbs()]
            >>> dbs
            [<Database: test>, <Database: test2>, <Database: test3>]
        """
        if db_names is None or len(db_names) == 0:
            for name in await aios.listdir(cls.base):
                yield Database(cls.base + name + "/")
        elif isinstance(db_names, list) and len(db_names) > 0:
            for name in db_names:
                yield await cls.get_db(name)
        else:
            raise InvalidArgumentType(f"Expected list, got {type(db_names)}.")

    @classmethod
    async def create_db(cls, db_name: str or int) -> Database:
        """Creates a single database.

        Args:
            db_name: The name of the database.

        Raises:
            AlreadyExists: If the database already exists.

        Example:
            >>> db = await AshenDB.create_db("test")
            >>> db
            <Database: test>
        """
        db_name = str(db_name)
        path = cls.base + db_name
        if await aios.path.exists(path):
            raise AlreadyExists(f"Database '{db_name}' already exists.")
        else:
            await aios.mkdir(path)
            return Database(path + "/")

    @classmethod
    async def create_dbs(cls, db_names: list[str]) -> list[Database]:
        """Create multiple databases.

        Args:
            db_names: The names of the databases.

        Raises:
            AlreadyExists: If one of the databases already exists.
            InvalidArgumentType: If the argument is not a list or Empty or No Argument was passed.

        Example:
            >>> dbs = await AshenDB.create_dbs(["test", "test2"])
            >>> dbs
            [<Database: test>, <Database: test2>]
        """
        final = []
        if db_names is None or len(db_names) == 0 or not isinstance(db_names, list):
            raise InvalidArgumentType(f"Expected list, got {type(db_names)}.")

        for name in db_names:
            final.append(await cls.create_one(name))

        return final

    @classmethod
    async def iterate_create_dbs(
        cls, db_names: list[str]
    ) -> Generator[Database, None, None]:
        """Iterate over multiple databases from list of database names.

        Args:
            db_names: The names of the databases.

        Raises:
            AlreadyExists: If one of the databases already exists.
            InvalidArgumentType: If the argument is not a list or Empty or No Argument was passed.

        Example:
            >>> async for db in AshenDB.iterate_create_dbs(["test", "test2"]):
            ...     print(db)
            <Database: test>
            <Database: test2>

            >>> dbs = [db async for db in AshenDB.iterate_create_dbs()]
            >>> dbs
            [<Database: test>, <Database: test2>, <Database: test3>]
        """
        if db_names is None or len(db_names) == 0 or not isinstance(db_names, list):
            raise InvalidArgumentType(f"Expected list, got {type(db_names)}.")
        for name in db_names:
            yield await cls.create_one(name)

    @classmethod
    async def del_db(cls, db_name: str) -> None:
        """Delete a single database.

        Args:
            db_name: The name of the database.

        Raises:
            NotFound: If the database does not exist.

        Example:
            >>> await AshenDB.delete_db("test")

        """
        path = cls.base + db_name
        if await aios.path.exists(path):
            await aios.removedirs(path)
            return
        else:
            raise Exception(f"Database '{db_name}' does not exist.")

    @classmethod
    async def del_dbs(cls, db_names: list[str]) -> None:
        """Delete multiple databases.

        If no list is provided or the list is empty, all databases are deleted.

        Args:
            db_names: The names of the databases.

        Raises:
            NotFound: If one of the databases does not exist.

        Example:
            >>> await AshenDB.delete_dbs(["test", "test2"])
        """
        if db_names is None:
            for name in await aios.listdir(cls.base):
                await cls.delete_db(name)
            return
        for name in db_names:
            await cls.delete_db(name)
        return
