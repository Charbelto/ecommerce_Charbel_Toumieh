E-Commerce Microservices Platform Documentation
============================================

Welcome to the E-Commerce Microservices Platform documentation. This platform consists of several microservices working together to provide a complete e-commerce solution.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   services/customer
   services/inventory
   services/sales
   services/reviews
   services/analytics
   services/auth
   utils/index

Architecture Overview
-------------------

The platform is built using a microservices architecture with the following key components:

* Customer Service: Manages customer data and operations
* Inventory Service: Handles product inventory management
* Sales Service: Processes sales transactions
* Reviews Service: Manages product reviews and ratings
* Analytics Service: Provides business insights
* Auth Service: Handles authentication and authorization

Each service is independently deployable and scalable, communicating via REST APIs.

Getting Started
-------------

Prerequisites:
^^^^^^^^^^^^^

* Python 3.9+
* Docker and Docker Compose
* PostgreSQL 13+

Installation:
^^^^^^^^^^^^

.. code-block:: bash

   git clone <repository-url>
   cd ecommerce-platform
   docker-compose up -d

API Documentation
---------------

Each service exposes its own REST API endpoints. Detailed documentation for each service can be found in their respective sections.

Error Handling
------------

The platform implements a centralized error handling system. See :ref:`error-handling` for details.

Monitoring and Profiling
----------------------

The platform includes comprehensive monitoring and profiling capabilities. See :ref:`monitoring` for details.