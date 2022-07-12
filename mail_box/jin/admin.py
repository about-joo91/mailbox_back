from django.contrib import admin
from .models import Category as CategoryModel
from . models import Letter as LetterModel
from .models import User_Letter_Target_User as User_Letter_Taget_User_Model
from .models import Letter_Review as Letter_Review_Model
from .models import Letter_Review_Like as Letter_Review_Like_Model
# Register your models here.
admin.site.register(CategoryModel)
admin.site.register(LetterModel)
admin.site.register(User_Letter_Taget_User_Model)
admin.site.register(Letter_Review_Model)
admin.site.register(Letter_Review_Like_Model)
# Register your models here.)