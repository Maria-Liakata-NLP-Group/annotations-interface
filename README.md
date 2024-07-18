# LongiText: An annotations interface to for capturing pantheoretical concepts from clinical psychology

New iteration of the Annotations Interface tool.
This repo builds upon the [Moments of Change annotations interface](https://github.com/Maria-Liakata-NLP-Group/MoC-annotation-interface).
It generalises to different types of text datasets: clinical psychology sessions and social media threads (work in progress).

## Software

<img width="760" alt="Screenshot 2024-07-18 at 11 44 22" src="https://github.com/user-attachments/assets/f4a8e41b-6200-4c07-a525-d357d2e7983a">

## Current capabilities

- User registration and login
- Supports standard and admin users
- Dataset upload and storage in SQL database
- Detailed annotations of dialog between patient and therapist
  - Custom segmentation/pagination of speech turns
  - Separate annotation forms for Patient/Therapist/Dyad
  - Annotations apply at the segment level, but can target specific speech turns (e.g. Moments of Change)

<img width="456" alt="Screenshot 2024-07-18 at 11 49 48" src="https://github.com/user-attachments/assets/36753d68-706a-4aaf-a174-5c8ae11479b0">

<img width="827" alt="Screenshot 2024-07-18 at 11 23 51" src="https://github.com/user-attachments/assets/05ec5fe8-0071-48bb-ab07-d7e25fd207bc">

<img width="787" alt="Screenshot 2024-07-18 at 11 24 30" src="https://github.com/user-attachments/assets/b91af42a-47d6-4908-a579-1c82302070de">


## Getting started

1. Clone the repo: `git clone git@github.com:Maria-Liakata-NLP-Group/annotations-interface.git`
2. `cd annotations-interface`
3. Create a Python virtual environment: `python -m venv .env`, and activate it `source .env/bin/activate`
4. Install the requirements: `pip install -r requirements.txt`
5. Create a `.flaskenv` file in the repo root directory containing the following:
  ```
  FLASK_APP=annotations_interface.py
  SECRET_KEY="you-will-never-guess"  # replace this with a randomized password
  APP_ADMIN="['admin@example.com']"  # replace this with the admin's email address
  ```
6. Run `flask db upgrade` to create the database and apply all the migrations. This will generate a SQLite `app.db` file in the repo root directory.
7. Run `flask clear-db`
8. Run `flask create-annotation-schema`
9. To run the Flask in a development server, run `flask run`. You should then be able to access the app on http://127.0.0.1:5000

## Relational database

To see the SQL database schema, visit the [WWW SQL Designer](https://sql.toad.cz/) tool.

- If you have saved the schema in the browser, go to Save/Load > LOAD FROM BROWSER. Enter `long-nlp-annotations-interface` when prompted for the keyword.
- If you are checking the schema for the first time, copy the contents of `sql-schema.xml`, go to Save/Load, paste the XML data under Input/Output and click on `LOAD XML`.
