.. AshenDB documentation master file, created by
   sphinx-quickstart on Sun Apr 23 12:18:25 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

AshenDB's documentation!
=================================

**AshenDB** is an asynchronous Python library to use json as a database in your workspace with similar functionality to MongoDB.

**Features**

- Located in user's workspace
- MongoDB like syntax
- Asynchronous


Introduction
------------

To use AshenDB, first Intall it using pip:

.. code-block:: console

   $ pip install -U ashendb

Then, import it in your project. 

.. code-block:: python
    
   from ashendb import AshenDB

This will automatically create ``.ashendb`` folder in your project directory.

**Database Structure**

.. literalinclude:: folder_structure.txt


Manuals
--------

.. toctree::
   :maxdepth: 1

   ashendb.client
   ashendb.collection
   ashendb.database
   ashendb.document
   ashendb.exception
   ashendb.helper


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
