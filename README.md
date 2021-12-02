## Water Mate Backend

This is the backend API for Water Mate.

### Setting up and Running this API

Using your command shell:

1. Make sure you have at least **python-3.9.2** installed on your machine as well as **pip3**. Check using `python3 --version` and `pip3 --version`.
2. Download the sourcecode `git checkout https://github.com/awildstone/Water-Mate-backend.git`.
3. CD into the project directory for **/Water-Mate-backend** and create a python virtual environment: `python3 -m venv /venv`.
4. Activate the python virtual environment: `source venv/bin/activate`.
5. Install the project dependencies from requirements.txt: `pip3 install -r requirements.txt`.

Water Mate uses a PostgreSQL server:

1. Create a new database named `water_mate_react`. You can use the `createdb water_mate_react` command.
2. Open the newly created database in your command shell `psql water_mate_react` the database should be empty with no tables.

To seed the database:

1. Its easiest to run the script in a Python shell like iPython. Install iPython `pip3 install ipython`.
2. In the same directory as **app.py** make sure the virtual environment is enabled and enter `ipython` into the shell to enable iPython.
3. Type `%run app.py` then `%run seed.py` to seed the database.
4. In a new command shell enter `psql water_mate_react` then `/dt` to confirm the database was seeded with tables and data.

To start the server:

1. Close iPython (Ctrl + D), then enter `flask run`. 
2. You can visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to make sure the API server is running. You should see the message: 
```
{
  "msg": "Welcome to Water Mate!"

}
```

### External API's in Use

[MapQuest Geocoding API](https://developer.mapquest.com/documentation/geocoding-api/) for getting and saving a user's current geolocation lat/long coordinates.

[Sunset and sunrise times API](https://sunrise-sunset.org/api) for gathering solar data in a user's location.

### Database Schema

[https://app.quickdatabasediagrams.com/#/d/mxfbkG](https://app.quickdatabasediagrams.com/#/d/mxfbkG)

![](https://user-images.githubusercontent.com/11568530/143668498-8e84f1b1-f65a-49e2-9cc2-423ccc572cf8.png)