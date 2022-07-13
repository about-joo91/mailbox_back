from django.contrib import admin
from .models import WorryCategory as WorryCategoryModel
from .models import Letter as LetterModel
from .models import LetterReview as LetterReviewModel
from .models import LetterReviewLike as LetterReivewLikeModel
from .models import UserLetterTargetUser as UserLetterTargetUserModel


admin.site.register(WorryCategoryModel)
admin.site.register(LetterModel)
admin.site.register(LetterReviewModel)
admin.site.register(LetterReivewLikeModel)
admin.site.register(UserLetterTargetUserModel)
# Register your models here.
