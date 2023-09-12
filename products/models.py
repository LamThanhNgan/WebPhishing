# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
# ctr + k + c: comment, ctr + k + u: uncomment
from django.db import models
from django.contrib.auth.models import User


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has on_delete set to the desired behavior.
#   * Remove managed = False lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
# ctr + k + c: comment, ctr + k + u: uncomment
from django.db import models
from django.contrib.auth.models import User

class static_result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    status = models.TextField()
    prediction = models.TextField()
    conf_score = models.TextField()
class dynamic_result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    status = models.TextField()
    brand_name = models.TextField()
    prediction = models.TextField()
    conf_score = models.TextField()

class final_result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    url_id = models.AutoField(primary_key=True)
    url = models.TextField() 
    finalurl = models.TextField(blank=True)
    time = models.DateTimeField(auto_now_add=True)
    status = models.TextField()
    prediction_final = models.TextField()
    conf_score = models.TextField()
    img_path = models.ImageField(upload_to ='media/predicts/')
    loc_path = models.ImageField(blank=True)
    vt_score = models.TextField(default="None")
    host = models.TextField(blank=True)
    host_country = models.TextField(blank=True)
    num_open_ports = models.TextField(blank=True)
    open_ports = models.TextField(blank=True)
    nameServerwhois = models.TextField(blank=True)
    HTMLinfo = models.TextField(blank=True)
    connection_speed = models.TextField(blank=True)
    isp = models.TextField(blank=True)
    registration_date = models.TextField(blank=True)
    expiration_date = models.TextField(blank=True)
    last_updates_dates = models.TextField(blank=True)
    intended_life_span = models.TextField(blank=True)
    life_remaining = models.TextField(blank=True)
    is_live = models.TextField(blank=True)
    brand_name = models.TextField(blank=True)
    scheme = models.TextField(blank=True)
    subdomains = models.TextField(blank=True)
    
    get_asn = models.TextField(blank=True)
    headers = models.TextField(blank=True)
    status_code = models.TextField(blank=True)
    hostnames = models.TextField(blank=True)
    ttl = models.TextField(blank=True)
    tld = models.TextField(blank=True)
    suspecious_tld = models.TextField(blank=True)
    has_port_in_string = models.TextField(blank=True)
    ip = models.TextField(blank=True)






