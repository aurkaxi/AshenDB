import asyncio
import aiofiles.os as aios


async def main() -> None:
    """Valiadates ".ashendb" directory.

    Directory is created if it does not exist.

    Raises:
        Exception: If a file named ".ashendb" already exists.
    """
    exists = await aios.path.exists(".ashendb")
    if exists:
        is_dir = await aios.path.isdir(".ashendb")
        if not is_dir:
            raise Exception("A file named '.ashendb' already exists.")
    else:
        await aios.mkdir(".ashendb")


asyncio.run(main())

from .client import AshenDB
from .database import Database
from .collection import Collection
from .document import Document
import ashendb.exception as AshenDBException
