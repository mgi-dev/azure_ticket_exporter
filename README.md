# Introduction 
You just passed from azure devops to Jira and have to copy and paste your entire backlog field by field ? 

Don't worry ! follow the readme !

It's not magic, but it save (some) time.

The script will export the tickets to a csv file.

# Configuring

Fill the variable ITEMS_TO_EXPORT in config.py file with ids of azure items to extract.
Any item will probably work (epic, feature, bug ...)

change FILE_NAME_EXTRACT value to change the ... file name of the extract. 
Don't forget to fill BASE_URL 

# Installation process
- Have python 3.7+ installed
- `pip install venv`
- `python -m venv venv`
- `source /venv/bin/activate`
- `pip install -r requirements.txt`
- edit the config.py file to your needs.
- `python azure_export.py` 
- Wait (The export is slow).
