from django.db import models


# Create your models here

class Banner(models.Model):
    banner_name = models.CharField(max_length=50, blank=True)
 
    is_active = models.BooleanField(default=True)
    set=models.BooleanField(default=False)

    def __str__(self):
        return self.banner_name
    
class BannerImage(models.Model):
    banner=models.ForeignKey(Banner,on_delete=models.CASCADE,related_name='images')  
    images = models.ImageField(upload_to='banneer_images/', blank=True) 
    
    def __str__(self):
        return self.banner.banner_name


    
