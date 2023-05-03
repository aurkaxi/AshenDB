.. image:: https://raw.githubusercontent.com/aurkaxi/AshenDB/master/docs/source/AshenDB_Logo.png

.. image:: https://readthedocs.org/projects/ashendb/badge/?version=latest
    :target: https://ashendb.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
      
AshenDB
=======

**AshenDB** is a another stupid library for using json as Database. It mimics MongoDB functionalities.


Why AshenDB?
------------
- **MongoDB** : Needs a server to run. `You can clone your MongoDB to AshenDB <https://ashendb.readthedocs.io/en/latest/ashendb.client.html#ashendb.client.AshenDB.from_mongo>`_. AshenDB is highly inspired from MongoDB, it uses MongoDB like syntax, which makes it easy to use for beginners as well as for MongoDB users.

- **TinyDB** : Too simple. Query and Update Operators such as ``$set``, ``$inc`` are not supported. `Check all the supported Operators in AshenDB <https://ashendb.readthedocs.io/en/latest/ashendb.helper.html>`_.  Also it is not thread safe. 

- **JsonDB** : It is not thread safe. Neither it supports mongodb like syntax.

Why not AshenDB?
----------------
It is immature. It doesn't use separate server but uses json as a database. Which may be good for small or medium projects but for large and scalable projects it is recommended to use MongoDB with Redis as a cache.

Installation
------------
It is available on PyPI. You can install it using pip.

.. code-block:: bash

    pip install ashendb

Usage
-----

.. code-block:: python

    >>> from ashendb import AshenDB
    # Assuming you are inside a async function
    >>> db = await AshenDB.get_db('test')
    >>> db
    <AshenDB: test>
    >>> coll = await db.get_coll('users')
    >>> coll
    <Collection: users>
    >>> doc = await coll.get_doc('user1')
    >>> doc
    <Document: user1>
    >>> print(doc)
    {'_id': 'user1'}


Documentation
=============
Documentation is available at `Read the Docs <https://ashendb.readthedocs.io/en/latest/>`_.

Contributing
============
- Open an issue.
- Fork the repository -> New Branch -> Make Changes -> Open a Pull Request.


