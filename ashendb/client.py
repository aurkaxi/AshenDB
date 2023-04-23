import aiofiles
import aiofiles.os as aios

from .database import Database


# Client Class
class AshenDB(str):
    """
    Entry point for AshenDB. This class is used to create, get, and delete databases.

    Args:
        base: The path. Which is always ".ashendb/".
    """

    base: str = ".ashendb/"

    @classmethod
    async def get_db(cls, db_name: str) -> Database:
        """Get a single database from database name.

        Args:
            db_name: The name of the database.
        """
        for name in await aios.listdir(cls.base):
            if name == db_name:
                return Database(cls.base + name + "/")
        raise Exception(f"Database '{db_name}' does not exist.")

    @classmethod
    async def get_dbs(cls, db_names: list = None):
        """
        Get multiple databases. If no databases are specified then all databases will be returned.
        """
        final = []
        if db_names is None:
            for name in await aios.listdir(cls.base):
                final.append(Database(cls.base + name + "/"))
            return final

        for name in db_names:
            final.append(await cls.get_db(name))
        return final

    @classmethod
    async def create_db(cls, db_name: str):
        """
        Create a single database.
        """
        path = cls.base + db_name
        if await aios.path.exists(path):
            raise Exception(f"Database '{db_name}' already exists.")
        else:
            await aios.mkdir(path)
            return Database(path + "/")

    @classmethod
    async def create_dbs(cls, db_names: list):
        """
        Create multiple databases.
        """
        final = []
        for name in db_names:
            final.append(await cls.create_one(name))
        return final

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
