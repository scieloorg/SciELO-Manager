Sponsors API
============

List all sponsors
-----------------

Request:

  **API version 1**

  *GET /api/v1/sponsors*

  **API version 2**

  *GET /api/v2/sponsors*

Parameters:

  **--**

Optional Parameters:

  **callback**

    *String* of the callback identifier to be returned when using JSONP.

  **format**

    *String* of the desired output format. The options are **xml, json,
    yml**.

Response:

  **API version 1**::

    {
      "meta": {
        "limit": 20,
        "next": "/api/v1/sponsors/?offset=20&limit=20&format=json",
        "offset": 0,
        "previous": null,
        "total_count": 157
      },
      "objects": [
        {
          "acronym": "",
          "address": "",
          "address_complement": "",
          "address_number": "",
          "cel": "",
          "city": "",
          "complement": "",
          "country": "",
          "created": "2012-07-24T21:47:05.463276",
          "email": "",
          "fax": "",
          "id": "264",
          "is_trashed": false,
          "name": "ANPEd, CNPq, UNESCO",
          "phone": "",
          "resource_uri": "/api/v1/sponsors/264/",
          "state": "",
          "updated": "2012-07-24T21:47:05.463312",
          "zip_code": null
        }
      ]
    }


  **API version 2**::

    {
      "meta": {
        "limit": 20,
        "next": "/api/v1/sponsors/?offset=20&limit=20&format=json",
        "offset": 0,
        "previous": null,
        "total_count": 157
      },
      "objects": [
        {
          "acronym": "",
          "address": "",
          "address_complement": "",
          "address_number": "",
          "cel": "",
          "city": "",
          "complement": "",
          "country": "",
          "created": "2012-07-24T21:47:05.463276",
          "email": "",
          "fax": "",
          "id": "264",
          "is_trashed": false,
          "name": "ANPEd, CNPq, UNESCO",
          "phone": "",
          "resource_uri": "/api/v1/sponsors/264/",
          "state": "",
          "updated": "2012-07-24T21:47:05.463312",
          "zip_code": null
        }
      ]
    }


Get a single sponsor
--------------------

Request:

  **API version 1**

  *GET /api/v1/sponsors/:id/*

  **API version 2**

  *GET /api/v2/sponsors/:id/*


Parameters:

  **--**

Optional Parameters:

  **callback**

    *String* of the callback identifier to be returned when using JSONP.

  **format**

    *String* of the desired output format. The options are **xml, json,
    yml**.

Response:

  **API version 1**::

    {
      "acronym": "",
      "address": "",
      "address_complement": "",
      "address_number": "",
      "cel": "",
      "city": "",
      "complement": "",
      "country": "",
      "created": "2012-07-24T21:47:05.463276",
      "email": "",
      "fax": "",
      "id": "264",
      "is_trashed": false,
      "name": "ANPEd, CNPq, UNESCO",
      "phone": "",
      "resource_uri": "/api/v1/sponsors/264/",
      "state": "",
      "updated": "2012-07-24T21:47:05.463312",
      "zip_code": null
    }

  **API version 2**::

    {
      "acronym": "",
      "address": "",
      "address_complement": "",
      "address_number": "",
      "cel": "",
      "city": "",
      "complement": "",
      "country": "",
      "created": "2012-07-24T21:47:05.463276",
      "email": "",
      "fax": "",
      "id": "264",
      "is_trashed": false,
      "name": "ANPEd, CNPq, UNESCO",
      "phone": "",
      "resource_uri": "/api/v1/sponsors/264/",
      "state": "",
      "updated": "2012-07-24T21:47:05.463312",
      "zip_code": null
    }
