from typing import Dict, List

from main_page.models import WorryCategory as WorryCategoryModel
from user.models import UserProfile as UserProfileModel


def get_category_of_profile_except_mine(user_id: int) -> List[Dict]:
    """
    내 프로필에 등록된 카테고리를 제외한 모든 카테고리 값을 가져오는 함수
    """
    user_profile = UserProfileModel.objects.filter(user_id=user_id).get()
    worry_category_ids_of_mine = [
        category.id for category in list(WorryCategoryModel.objects.filter(userprofile=user_profile))
    ]

    category_all_except_mine = list(WorryCategoryModel.objects.all().exclude(id__in=worry_category_ids_of_mine))
    categories = [{"id": cate.id, "cate_name": cate.cate_name} for cate in category_all_except_mine]
    return categories


def create_category_of_profile(user_id: int, categories: List) -> None:
    """
    내 프로필에 카테고리를 등록하는 함수
    """
    user_profile = UserProfileModel.objects.filter(user_id=user_id).get()
    user_profile.categories.add(*categories)


def delete_category_of_profile(user_id: int, p_category: int) -> None:
    """
    내 프로필의 카테고리를 제거하는 함수
    """
    worry_category = WorryCategoryModel.objects.filter(id=p_category).get()
    UserProfileModel.objects.filter(user_id=user_id).get().categories.remove(worry_category)
