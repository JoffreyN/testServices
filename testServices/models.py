from django.db import models

# class UserInfo(models.Model):
# 	username = models.CharField(max_length=32)
# 	password = models.CharField(max_length=64)

class ViewXY(models.Model):
	username=models.CharField(max_length=32)
	xy=models.CharField(max_length=255)

	class Meta:
		db_table='view_xy'
