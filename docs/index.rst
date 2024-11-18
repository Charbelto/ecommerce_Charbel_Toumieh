E-Commerce Microservices Documentation
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   services/customer
   services/sales
   services/inventory
   services/analytics
   services/auth

Architecture Overview
-------------------

This e-commerce platform is built using a microservices architecture with the following key components:

* Customer Service: Manages customer data and operations
* Sales Service: Handles purchase transactions
* Inventory Service: Manages product inventory
* Analytics Service: Provides business insights
* Auth Service: Handles authentication and authorization

Getting Started
-------------

To run the services locally:

.. code-block:: bash

   docker-compose up -d

API Documentation
---------------

Each service exposes its own REST API endpoints. See individual service documentation for details.

.. automodule:: customer_service
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: sales_service
   :members:
   :undoc-members:
   :show-inheritance: