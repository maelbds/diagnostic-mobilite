## Data Manager

### Description

Data Manager is one part of the project which **role is to manage and store data**. Then, it loads data from api sources, 
stores it into the database and distribute it to other parts of the project. 

### Structure

It is made of :
- insee/, osm/, anct/ : _sources folder_
- database_connection/ : **connection info with the database to fill** 
- tokens.py : **api tokens when required**
- main.py : _interface with other part of the project_

