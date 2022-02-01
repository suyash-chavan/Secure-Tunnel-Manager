# Server Side Configuration

Some server side cmponents are critical and need to be configured correctly to ensure security.

## Components

### **1. Dashboard**

    We have used Streamlit framework here to create Dashboard wherein we can easily scale for newer functionalities. 

### **2. Flask API**

    Flask API here ensures the data exchange between Database, Streamlit Server and Client.

## Dashboard Setup

* Streamlit server is to be run in python virtual environment, we have used `pipenv` and `python 3.8` to ensure all the dependencies are installed.
* All dependencies are included in `pipfile` and virtual environment chan be easily regenerated using **_pipenv shell_** command.

## Flask API Setup

* Flask API is pretty much easy to setup, just enter **_flask run_** in the _watchman_ directory by setting **_FLASK_APP_** env variable as `app.py`.

## Database Server

    db.createUser(
        {
        user: "admin",
        pwd: "iot123",
        roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
        }
    )

    db.createUser(
  {
    user: "watchman",
    pwd: "T86K3CC3nJzB8rCg",
    roles: [ { role: "readWrite", db: "watchman" },
             { role: "read", db: "reporting" } ]
  }
)