Inventory Service
===============

.. module:: services.inventory.inventory_service

The Inventory Service manages product inventory, including stock management, product information, and category organization.

Models
------

Item Model
^^^^^^^^^

.. autoclass:: services.inventory.models.item.Item
   :members:
   :show-inheritance:

Schemas
-------

.. autoclass:: services.inventory.schemas.ItemBase
   :members:

.. autoclass:: services.inventory.schemas.ItemCreate
   :members:

.. autoclass:: services.inventory.schemas.ItemUpdate
   :members:

API Endpoints
-----------

Create Item
^^^^^^^^^^

.. autofunction:: create_item

Get Item
^^^^^^^

.. autofunction:: get_item

Update Item
^^^^^^^^^

.. autofunction:: update_item

Delete Item
^^^^^^^^^

.. autofunction:: delete_item

Search and Filtering
------------------

The service supports advanced search and filtering capabilities:

* Category-based filtering
* Price range filtering
* Stock availability filtering
* Text search in name and description

Caching
-------

The service implements Redis caching for frequently accessed items:

.. code-block:: python

   @cache_response(expire_time_seconds=300)
   async def get_item(item_id: int):
       # Implementation

Performance Optimization
---------------------

* Database indexing on frequently queried fields
* Composite indexes for common query patterns
* Query optimization for large datasets

Error Handling
------------

Common error scenarios and their handling:

* Item not found
* Invalid category
* Stock management errors
* Concurrent update conflicts

Dependencies
----------

.. literalinclude:: ../../services/inventory/requirements.txt
   :language: text