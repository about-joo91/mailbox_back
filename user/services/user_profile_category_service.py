from typing import Dict, List

from jin.models import WorryCategory as WorryCategoryModel
from user.models import User as UserModel
from user.models import UserProfile


def get_category_of_profile(user_id: int) -> List[Dict]:
    category_all_except_mine = WorryCategoryModel.objects.all().exclude(
        id__in=UserModel.objects.filter(id=user_id)
        .select_related("userprofile")
        .get()
        .userprofile.categories.all()
    )
    categories = [
        {"id": cate.id, "cate_name": cate.cate_name}
        for cate in category_all_except_mine
    ]
    return categories


def create_category_of_profile(user_id: int, categories: List) -> None:
    user_profile = UserProfile.objects.filter(user__id=user_id).get()
    user_profile.categories.add(*categories)
