from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    file2 = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ProcessedData(models.Model):
    guest_name = models.CharField(max_length=255,null=True,blank=True)
    is_matched = models.BooleanField(default=False,null=True,blank=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    rate_amd = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    difference = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)

    def __str__(self):
        return self.guest_name
    
class VendorTemplate(models.Model):
    template_name = models.CharField(max_length=255, null=True, blank=True)
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    is_merged = models.BooleanField(default=False, null=True, blank=True)
    arr_date_name = models.CharField(max_length=255, null=True, blank=True)
    dept_date_name = models.CharField(max_length=255, null=True, blank=True)
    arr_dept_date_name = models.CharField(max_length=255, null=True, blank=True)
    amount_name = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if is_merged is True
        if self.is_merged:
            # Clear arr_date_name and dept_date_name fields
            self.arr_date_name = None
            self.dept_date_name = None
        else:
            # Clear arr_date_name and dept_date_name fields
            self.arr_dept_date_name = None
        super().save(*args, **kwargs)  # Call the parent save method

    def __str__(self):
        return self.template_name


class ArrivalTemplate(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    is_merged = models.BooleanField(default=False,null=True,blank=True)
    arr_date_name = models.CharField(max_length=255,null=True,blank=True)
    dept_date_name = models.CharField(max_length=255,null=True,blank=True)
    arr_dept_date_name = models.CharField(max_length=255,null=True,blank=True)
    rate_amt_name_name = models.CharField(max_length=255,null=True,blank=True)
    
    def save(self, *args, **kwargs):
        # Check if is_merged is True
        if self.is_merged:
            # Clear arr_date_name and dept_date_name fields
            self.arr_date_name = None
            self.dept_date_name = None
        else:
            # Clear arr_date_name and dept_date_name fields
            self.arr_dept_date_name = None
        super().save(*args, **kwargs)  # Call the parent save method

    def __str__(self):
        return self.name
