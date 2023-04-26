import aiofiles, json
import aiofiles.os as aios
from typing import Generator
from uuid import uuid4

from .helper import match_data
from .document import Document
from .exception import *


def gen_id() -> str:
    """Generate a random id.

    Returns:
        A random id.
    """
    return str(uuid4())


class Collection:
    def __init__(self, path):
        self.path = path

    async def get_doc(self, *, id: str or int = None, query: dict = None) -> Document:
        """Get a single document.

        You can pass either an id or a query. If both are passed then the id will be used.

        Args:
            id: The id of the document.
            query: A query to match the document.

        Raises:
            ValueError: If neither id nor query is passed.
            NotFound: If no document is found.

        Example:
            >>> doc = await coll.get_doc(1)
            >>> doc
            <Document: 1>

            >>> doc = await coll.get_doc(query={"name": "test"})
            >>> print(doc)
            {"name": "test"}
        """
        if id:
            # check if the "{self.path}/{id}.json" file exists
            path = f"{self.path}/{id}.json"
            if not await aios.path.exists(path):
                raise NotFound("No document found")
            doc = Document(path)
            await doc.__ainit__()
            return doc
        elif query:
            for file in await aios.scandir(self.path):
                async with aiofiles.open(file.path, "r") as f:
                    data = json.loads(await f.read())
                    if await match_data(data, query):
                        doc = Document(file.path)
                        await doc.__ainit__()
                        return doc
            raise NotFound("No document found")
        else:
            raise ValueError("Either id or query must be provided")

    async def get_docs(
        self, ids: list[str or int] = None, query: dict = None
    ) -> list[Document]:
        """Get multiple documents.

        You can pass either a list of ids or a query. If both are passed then the ids will be used.

        Args:
            ids: The ids of the documents.
            query: A query to match the documents.

        Raises:
            ValueError: If neither ids nor query is passed.
            NotFound: If no documents are found.

        Example:
            >>> docs = await coll.get_docs([1, 2, 3])
            >>> docs
            [<Document: 1>, <Document: 2>, <Document: 3>]

            >>> docs = await coll.get_docs(query={"name": "test"})
            >>> docs
            [<Document: 1>, <Document: 2>, <Document: 3>]
        """
        final = []
        if ids:
            for id in ids:
                final.append(await self.get_doc(id=id))
            return final
        elif query:
            for file in await aios.scandir(self.path):
                async with aiofiles.open(file.path, "r") as f:
                    data = json.loads(await f.read())
                    if await match_data(data, query):
                        doc = Document(file.path)
                        await doc.__ainit__()
                        final.append(doc)
            if len(final) == 0 or len(final[0]) == 0:
                raise NotFound("No documents found")
            return final
        else:
            raise ValueError("Either ids or query must be provided")

    async def iterate_docs(
        self, ids: list[str or int], query: dict = None
    ) -> Generator[Document, None, None]:
        """Iterate over multiple documents.

        You can pass either a list of ids or a query. If both are passed then the ids will be used.

        Args:
            ids: The ids of the documents.
            query: A query to match the documents.

        Raises:
            ValueError: If neither ids nor query is passed.
            NotFound: If no documents are found.

        Example:
            >>> async for doc in coll.iterate_docs([1, 2, 3]):
            ...     print(doc)
            {"name": "test1"}
            {"name": "test2"}
            {"name": "test3"}

            >>> async for doc in coll.iterate_docs(query={"name": "test"}):
            ...     print(doc)
            {"name": "test1"}
            {"name": "test2"}
            {"name": "test3"}
        """
        if ids:
            for id in ids:
                yield await self.get_doc(id=id)
        elif query:
            for file in await aios.scandir(self.path):
                async with aiofiles.open(file.path, "r") as f:
                    data = json.loads(await f.read())
                    if await match_data(data, query):
                        doc = Document(file.path)
                        await doc.__ainit__()
                        yield doc
        else:
            raise ValueError("Either ids or query must be provided")

    async def create_doc(self, data: dict) -> Document:
        """Create a document.

        Args:
            data: The data to be stored in the document.

        Raises:
            TypeError: If data is not a dict.

        Example:
            >>> doc = await coll.create_doc({"name": "test"})
            >>> doc
            <Document: 1>
        """
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict")

        try:
            id = str(data.get("_id"))
        except:
            id = gen_id()

        async with aiofiles.open(f"{self.path}/{id}.json", "w") as f:
            await f.write(json.dumps(data))
        return Document(f"{self.path}/{id}.json")

    async def create_doc(self, datas: list[dict]) -> list[Document]:
        """Create multiple documents.

        Args:
            datas: The data to be stored in the documents.

        Raises:
            TypeError: If datas is not a list.

        Example:
            >>> docs = await coll.create_docs([{"name": "test1"}, {"name": "test2"}])
            >>> docs
            [<Document: 1>, <Document: 2>]
        """
        if not isinstance(datas, list):
            raise TypeError("Datas must be a list")

        final = []
        for data in datas:
            final.append(await self.create_doc(data))
        return final

    async def del_doc(self, id: str or int = None, query: dict = None) -> None:
        """Delete a document.

        You can pass either an id or a query. If both are passed then the id will be used.

        Args:
            id: The id of the document.
            query: A query to match the document.

        Raises:
            ValueError: If neither id nor query is passed.
            NotFound: If no document is found.

        Example:
            >>> await coll.delete_doc(1)
        """
        if id:
            doc = await self.get_doc(id)
            await doc.delete()
        elif query:
            doc = await self.get_doc(query=query)
            await doc.delete()
        else:
            raise ValueError("Either id or query must be provided")

    async def del_docs(self, ids: list[str or int] = None, query: dict = None) -> None:
        """Delete multiple documents.

        You can pass either a list of ids or a query. If both are passed then the ids will be used.

        Args:
            ids: The ids of the documents.
            query: A query to match the documents.

        Raises:
            ValueError: If neither ids nor query is passed.
            NotFound: If no documents are found.

        Example:
            >>> await coll.delete_docs([1, 2, 3])
        """
        if ids:
            for id in ids:
                await self.delete_doc(id)
        elif query:
            for doc in await self.get_docs(query=query):
                await doc.delete()
        else:
            raise ValueError("Either ids or query must be provided")
