import json
import subprocess
import urllib
from typing import Generator, Union
from uuid import uuid4

import aiofiles
import aiofiles.os as aios
import httpx

from .document import Document
from .exception import *
from .helper import match_data, update_data


def gen_id() -> str:
    """Generate a random id.

    Returns:
        A random id.
    """
    return str(uuid4())


class Collection:
    def __init__(self, path):
        self.path = path

    async def w3m(self) -> None:
        """Show the collection in w3m.

        Note:
            Your system must have w3m installed.
        """

        json_data = []
        for file in await aios.scandir(self.path):
            async with aiofiles.open(file.path, "r") as f:
                json_data.append(json.loads(await f.read()))

        safe_data = urllib.parse.quote(str(json_data).replace("'", '"'))
        safe_data = safe_data.replace("%20", "+")
        data = "jsonData=" + safe_data

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://tools.atatus.com/tools/json-to-html",
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
            )
            response.raise_for_status()

        subprocess.run(
            ["w3m", "-dump", "-T", "text/html", "-cols", "1000"],
            input=response.text.replace(
                "<table>", '<table  border="1" cellpadding="10">'
            ),
            encoding="utf-8",
        )
        return None

    async def get_doc(
        self,
        id: str | None = None,
        query: dict[str, list[dict[str, dict[str, str]]]] | None = None,
    ) -> Document:
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
                    document = json.loads(await f.read())
                    if await match_data(document, query):
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
            for file in await aios.scandir(self.path):
                doc = Document(file.path)
                await doc.__ainit__()
                final.append(doc)
            if len(final) == 0 or len(final[0]) == 0:
                raise NotFound("No documents found")
            return final

    async def iterate_docs(
        self, *, ids: list[str or int] = None, query: dict = None
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

            >>> docs = [doc async for doc in coll.iterate_docs([1, 2, 3])]
            >>> docs
            [<Document: 1>, <Document: 2>, <Document: 3>]
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
            for file in await aios.scandir(self.path):
                async with aiofiles.open(file.path, "r") as f:
                    data = json.loads(await f.read())
                    doc = Document(file.path)
                    await doc.__ainit__()
                    yield doc

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
            id = str(data["_id"])
        except KeyError:
            id = gen_id()
            data["_id"] = id
        # Check if already exist
        if await aios.path.exists(f"{self.path}/{id}.json"):
            raise AlreadyExists("Document already exist")
        async with aiofiles.open(f"{self.path}/{id}.json", "w") as f:
            await f.write(json.dumps(data))
        document = Document(f"{self.path}/{id}.json")
        await document.__ainit__()
        return document

    async def create_docs(self, datas: list[dict]) -> list[Document]:
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
            path = f"{self.path}/{id}.json"
            if not await aios.path.exists(path):
                raise NotFound("No document found")
            await aios.remove(path)
            return
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
                await self.del_doc(id)
        elif query:
            async for doc in self.get_docs(query=query):
                await doc.delete()
        else:
            raise ValueError("Either ids or query must be provided")

    async def update_doc(
        self, id: str or int = None, query: dict = None, data: dict = None
    ) -> Document:
        """Update a document.

        You can pass either an id or a query. If both are passed then the id will be tried first, if it fails then the query will be used.

        Note:
            Not all update operators are supported. See helper_module for more info.
        Args:
            id: The id of the document.
            query: A query to match the document.
            data: The data to update the document with.

        Raises:
            ValueError: If neither id nor query is passed.
            NotFound: If no document is found.

        Example:
            >>> old_doc = await coll.update_doc(query={"name": "test"}}
            >>> old_doc
            {"name": "test"}
            >>> await coll.update_doc(query={"name": "test"}, data={"$set":{"name": "test2"})}
            >>> new_doc = await coll.get_doc(query={"name": "test2"})
            >>> new_doc
            {"name": "test2"}
        """
        doc = await self.get_doc(id=id, query=query)
        new_doc = await update_data(doc, data)
        return new_doc

    async def count_docs(self) -> int:
        """Count the number of documents in the collection.

        Example:
            >>> await coll.count_docs()
            3
        """
        count = 0
        for _ in await aios.scandir(self.path):
            count += 1
        return count
