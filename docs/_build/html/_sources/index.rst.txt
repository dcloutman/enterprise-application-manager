Enterprise Application Tracker Documentation
=============================================

Welcome to the Enterprise Application Tracker - an experimental application inventory system designed for tracking enterprise software application installations and their supporting infrastructure relationships within server-side environments.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   user-guide/index
   api-reference/index
   security/index
   deployment/index
   administration/index
   development/index
   appendices/index

Quick Start
-----------

1. **Installation**: See :doc:`installation` for deployment options
2. **User Guide**: Read :doc:`user-guide/getting-started` for basic usage  
3. **API Reference**: Explore :doc:`api-reference/overview` for programmatic access
4. **Administration**: Consult :doc:`administration/index` for system management

System Overview
---------------

The Enterprise Application Tracker provides basic capabilities for:

**Core Features**
- **Application Management**: Track business applications with basic metadata
- **Server Tracking**: Simple server inventory with application relationships
- **Database Inventory**: Basic database and data store tracking
- **Role-Based Access Control**: Five-tier permission system
- **REST API**: Programmatic interface for data access and manipulation
- **Audit Logging**: Basic activity tracking for compliance requirements

**Current Limitations**
- This is an experimental system in early development
- Limited reporting and analytics capabilities
- Basic security features implemented
- No physical asset tracking capabilities
- Minimal integration features

**Architecture Overview**

.. code-block::

    ┌─────────────────────────────────────────────────────────────┐
    │                    Web Interface                            │
    │          SvelteKit Frontend with TypeScript                 │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API  
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                   Backend Services                          │
    │    Django 4.2+ with Django REST Framework                  │
    │    ├── Role-Based Access Control                           │
    │    ├── Basic Audit Logging                                 │  
    │    ├── Data Validation                                     │
    │    └── API Authentication                                  │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    Data Layer                               │
    │  ┌─────────────┐                  ┌─────────────────────┐ │
    │  │   MySQL     │                  │   File Storage      │ │
    │  │  Database   │                  │   (Static Files)    │ │
    │  │  (Primary)  │                  │                     │ │
    │  └─────────────┘                  └─────────────────────┘ │
    └─────────────────────────────────────────────────────────────┘

**Development Status**

- **Version**: 0.0.1 (Experimental)
- **Development Started**: July 26, 2025
- **Current Status**: Active development, experimental features

**Test User Accounts**

- **admin** (Application Admin) - Full system access
- **sysmanager** (Systems Manager) - Technical data access  
- **technician** (Technician) - Limited write access
- **bizmanager** (Business Manager) - Business data read access
- **bizuser** (Business User) - Basic read access

**Deployment Options**

- **Docker Compose**: Development and testing deployments
- **Docker Swarm**: Multi-container orchestration  
- **Manual Installation**: Traditional server deployment

Getting Help
------------

**Documentation Structure**

- :doc:`user-guide/index`: Basic user documentation for each role
- :doc:`api-reference/index`: REST API endpoint reference
- :doc:`administration/index`: System administration procedures
- :doc:`development/index`: Developer setup and contribution information
- :doc:`security/index`: Security implementation details

**Support Channels**

- **Documentation**: Start with the relevant guide section
- **API Issues**: Consult :doc:`api-reference/overview` for endpoint details
- **Technical Support**: Contact your system administrator

License and Version
--------------------

- **Version**: 0.0.1 (Experimental)
- **License**: Enterprise License (contact your organization)
- **Documentation Updated**: July 2025

.. note::
   This documentation is for version 0.0.1 of the Enterprise Application Tracker. 
   This is an experimental release and features may change significantly in future versions.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
