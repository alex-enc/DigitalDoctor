# DigitalDoctor
## User Guide
### Setting Up
After downloading the project zip file or cloning the git project:

Install requirements:
```
pip3 install -r requirements.txt
```

Make migrations:
```
python3 manage.py makemigrations

python3 manage.py migrate

python3 manage.py showmigrations
```

To run server: python3 manage.py runserver

### Using the website
**Note: make sure to only click once when selecting buttons:**
  - 'Next'
  - 'See Articles'
  - 'New Chat'
  - 'DigiDoc'


This is to ensure that no duplications may arise and that no _Internal Errors_ may arise further down the consultation. 

You will then be greeted by the Home page.

On this page, you can select to view the site in any of the 4 available languages.

By clicking on start, the page will be redirected to the on\_boarding page.

Depending on how many initial symptoms are provided, the next page may differ. 

If only 1 symptom is provided}
The system will ask whether the user would prefer an assessment or information on the symptom that they are experiencing.

By selecting information, the user will be directed to a page containing relevant articles.

If the user selects Assessment, the page will direct the user to pages with more questions. The number of further questions required by the system will vary depending on each consultation, and what information the user provides.

Once the API symptom checker has reached a conclusion on the possible conditions the user has, it will produce a report.

This page has clickable cards to access more information about the possible conditions the user may have, and will trigger a modal to appear.

There is also a section where the user can view the information they have provided within the consultation.

If the user had provided more than 1 iniitial symptom on the on_boarding phase, then the page will be directed straight to the 'Assessment' pathway.

At any point of the consultation, the user is able to start a new chat/consultation by clicking on the _'New Chat'_ button on the navigation bar or the _'DigiDoc'_ and the page will subsequently be directed back to the _'Home'_ page.
