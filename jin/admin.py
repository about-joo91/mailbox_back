from django.contrib import admin
from .models import Category as CategoryModel
from .models import Letter as LetterModel
from .models import Letter_Review as Letter_ReviewModel
from .models import Letter_Review_Like as Letter_Reivew_LikeModel
from .models import User_Letter_Target_User as User_Letter_Target_UserModel

admin.site.register(CategoryModel)
admin.site.register(LetterModel)
admin.site.register(Letter_ReviewModel)
admin.site.register(Letter_Reivew_LikeModel)
admin.site.register(User_Letter_Target_UserModel)
# Register your models here.
