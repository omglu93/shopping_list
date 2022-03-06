# Shopping List

### Introduction

This readme will provide a short walkthrough of the REST API. The core of the application is the flask_restful library that allows the user to better structure the individual endpoints and their classes. The ORM library used is an extension of sqlalchemy called flask_sqlalchemy. It allows for faster implementation of individual SQL elements. Aside from that, it behaves like the normal ORM. In addition to this, flask_migrate is used to push the table structures onto PostgreSQL. The last major library is flask_mail which allows us to send e-mails from within flask functions.

### Local database setup

**Docker will do this for you, this is only if you want to test the database localy.**

First, create a db with the name task_db. After that run the below commands:

`python db db init`

`python db db migrate`

`python db db upgrade`


#### API Endpoints

| **URL Endpoint**                | **HTTP Method** | **Description**                                 | **Token** |
|---------------------------------|-----------------|-------------------------------------------------|-----------|
| /api/v1/create-user             | POST            | Creates user                                    | False     |
| /api/v1/login                   | GET             | Log in and generate token                       | False     |
| /api/v1/login/forgot-password   | GET             | Sends e-mail to adress in db                    | False     |
| /api/v1/login/forgot-password   | PUT             | Changes password of user                        | True      |
| /api/v1/edit-user               | PUT             | Changes user credentials                        | True      |
| /api/v1/shopping-lists          | POST            | Makes new shopping list with items              | True      |
| /api/v1/shopping-lists          | GET             | Returns all shopping lists of user              | True      |
| /api/v1/shopping-lists          | PUT             | Changes name of a selected shopping list        | True      |
| /api/v1/shopping-lists          | DELETE          | Deletes a selected shopping list                | True      |
| /api/v1/shopping-lists/items    | POST            | Creates items for the requested shopping list   | True      |
| /api/v1/shopping-lists/items    | GET             | Returns items of selected or all shopping lists | True      |
| /api/v1/shopping-lists/items    | PUT             | Change item attributes via given id             | True      |
| /api/v1/shopping-lists/items    | DELETE          | Deletes item by id                              | True      |
| /api/v1/shopping-lists/overview | GET             | Returns overview of items in given date range   | True      |
