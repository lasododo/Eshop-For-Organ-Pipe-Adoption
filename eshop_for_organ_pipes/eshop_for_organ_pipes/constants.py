
# https://nordigen.com/en/
NORDIGEN_TOKEN = ""
NORDIGEN_BANK_ID = ""

# https://stripe.com/en-cz
STRIPE_SECRET_API_KEY = "sk_test_....."
STRIPE_PUB_KEY = 'pk_test_....'

# Currency for payments (does not affect website's design!!)
CURRENCY = "CZK"

# EMAIL SETUP
DEFAULT_FROM_EMAIL = '------@gmail.com'
EMAIL_HOST_USER = '------@gmail.com'
EMAIL_HOST_PASSWORD = '#########'

# change this, if you want to use something else than GMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
