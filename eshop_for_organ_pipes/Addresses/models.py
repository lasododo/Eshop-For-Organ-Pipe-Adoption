from django.db import models

from billing.models import BillingProfile

DEFAULT_COUNTRY = "Czech Republic"
ADDRESS_TYPES = (
    ('billing', 'Billing'),
    # ('shipping', 'Shipping')  <--- for future purposes
)


class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.DO_NOTHING)
    address_type = models.CharField(max_length=120, choices=ADDRESS_TYPES)
    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120, default=DEFAULT_COUNTRY)
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=120)

    def __str__(self):
        return str(self.billing_profile)

    def get_address(self):

        return f"""
                                        <li class="list-group-item" style="background-color:black;">
                                            <i class="fas fa-address-card text-primary" aria-hidden="true"></i>
                                            {self.address_line_1}
                                        </li>
                                        <li class="list-group-item" style="background-color:#0d0d0d;">
                                            <i class="fa fa-bookmark text-primary mr-2" aria-hidden="true"></i>
                                            {self.address_line_2}
                                        </li>
                                        <li class="list-group-item" style="background-color:black;">
                                            <i class="fa fa-bell text-primary mr-2" aria-hidden="true"></i> 
                                            {self.city}
                                        </li>
                                        <li class="list-group-item" style="background-color:#0d0d0d;">
                                            <i class="fa fa-life-ring text-primary mr-2" aria-hidden="true"></i> 
                                            {self.country}
                                        </li>
                                        <li class="list-group-item" style="background-color:black;">
                                            <i class="fa fa-paper-plane text-primary mr-2" aria-hidden="true"></i> 
                                            {self.state}
                                        </li>
                                        <li class="list-group-item" style="background-color:#0d0d0d;">
                                            <i class="fa fa-life-ring text-primary mr-2" aria-hidden="true"></i>
                                            {self.postal_code}
                                        </li>
        """

    get_address.allow_tags = True
