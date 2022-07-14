from django.contrib import admin

from worry_board.models import WorryBoard as WorryBoardModel

from .models import Letter as LetterModel
from .models import LetterReview as LetterReviewModel
from .models import LetterReviewLike as LetterReivewLikeModel
from .models import UserLetterTargetUser as UserLetterTargetUserModel
from .models import WorryCategory as WorryCategoryModel

admin.site.register(WorryCategoryModel)
admin.site.register(LetterModel)
admin.site.register(LetterReviewModel)
admin.site.register(LetterReivewLikeModel)
admin.site.register(UserLetterTargetUserModel)
admin.site.register(WorryBoardModel)
# Register your models here.
