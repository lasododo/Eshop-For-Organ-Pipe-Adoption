# Setting up the application:

In order to start the application, you need to set up an environment for it. 

First, you will need to download python (python-3.9.6 is ***Recommended***) and then you need to install the required packages from the `requirements.txt`

After these packages are installed, you need to go to `eshop_for_organ_pipes/eshop_for_organ_pipes/constants.py` and set up the required constants.

In order to set them up, you need to create 2 accounts, on the Stripe website and one on Nordigen website. 

For stripe, you will need the:
- public key
- private key

For Noridgen you will need the:
- access token
- bank ID *[1]


*[1] This ID can be obtained after you log into the website and then you follow the quickstart guide (https://nordigen.com/en/account_information_documenation/integration/quickstart_guide/) from the 5th step.

(Example commands from Nordigen website)
```bash
curl -X GET "https://ob.nordigen.com/api/v2/requisitions/8126e9fb-93c9-4228-937c-68f0383c2df7/" 
-H  "accept: application/json" 
-H  "Authorization: Bearer ACCESS_TOKEN" 
```

```bash
{
  "id": "8126e9fb-93c9-4228-937c-68f0383c2df7",
  "status": "LN",
  "agreements": "2dea1b84-97b0-4cb4-8805-302c227587c8",
  "accounts": [
    "065da497-e6af-4950-88ed-2edbc0577d20" <---- Bank ID
  ],
  "reference": "124151",
}
```


# Running the application:

In order to run the app, please execute the following commands:

```bash
python manage.py makemigrations 
```
^ optional

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py runserver
```

# Setting up a website:

After the server is running, you need to log into the superuser you have created (Admin) and upload the eshop using the registry distibution, or you can just click `generate-e-shop`, that is going to generate the e-shop completely randomly if needed.

I strongly suggest using the `database_export.xlsx` or `database_export_v2.xlsx` for generating the e-shop.

### NOTE:
***Please do not use "Generate E-shop" unless it is necessary!***


## Additional commands:

If you want to run tests, you can use the following command:

```bash
python manage.py test
```

For running the cron job (immediately) you can run the following command:

```bash
python manage.py runcrons --force
```

For more information about cron jobs, please see the docs -> https://django-cron.readthedocs.io/en/latest/installation.html

## Test Coverage

Unfortunately, currently the test coverage is just for the basic functionality, you need to test the payment process by yourself

Additionally, without setting up the stripe key, the cart test WILL FAIL! (this is intentional, in order to not start the website without Stripe)

### Disclaimer for missing commits:
Since I was using my own GMAIL account and token, I have decided to remove my git history in order to secure this information. 