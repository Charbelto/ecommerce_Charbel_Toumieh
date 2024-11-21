Customer Service
==============

.. module:: services.customer.customer_service

The Customer Service manages all customer-related operations including profile management, wallet operations, and customer analytics.

Models
------

Customer Model
^^^^^^^^^^^^^

.. autoclass:: services.customer.models.customer.Customer
   :members:
   :show-inheritance:

API Endpoints
-----------

Create Customer
^^^^^^^^^^^^^

.. autofunction:: create_customer

Get Customer
^^^^^^^^^^

.. autofunction:: get_customer

Update Customer
^^^^^^^^^^^^

.. autofunction:: update_customer

Delete Customer
^^^^^^^^^^^^

.. autofunction:: delete_customer

Wallet Operations
--------------

.. autofunction:: charge_wallet

.. autofunction:: deduct_from_wallet

Schemas
-------

.. automodule:: services.customer.schemas
   :members:
   :show-inheritance:

Database
--------

The service uses PostgreSQL for data persistence. Database configuration and session management are handled through SQLAlchemy.

.. code-block:: python

   SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@customer_db:5432/customer_db"

Error Handling
------------

The service implements comprehensive error handling for various scenarios:

* Username/email already exists
* Invalid credentials
* Insufficient wallet balance
* Resource not found

See :class:`utils.exceptions.BaseServiceException` for details.

Dependencies
----------

.. literalinclude:: ../../services/customer/requirements.txt
   :language: text