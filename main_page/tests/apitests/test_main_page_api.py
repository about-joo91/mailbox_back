
from django.test.utils import CaptureQueriesContext 
from django.db import connection 
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User
from user.models import UserProfile
from worry_board.models import WorryBoard
from main_page.serializers import MainPageDataSerializer


class TestLoginUser(APITestCase):
    def setUp(self):
        """
        API setup 을 담당, 기본유저랑, 유저프로필 셋팅
        """
        self.data = {'username':'hajin','password':'asdfasdf'}
        self.user = User.objects.create_user('hajin','asdfasdf')
        user_profile = UserProfile.objects.filter(user=self.user.id)
        info = ({
            "user_id" : self.user.id,
            "mongle_grade" : 100,
            "profile_img" : "sdfsdf.com",
        })
        user_profile.create(**info)

    def test_login(self):
        
        url = "/user/login"
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, 200)

    def test_get_main(self):
        access_token = self.client.post(("/user/login"),self.data).data['access']
        response = self.client.get(
            path="/jin/main/",
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
            )

        with CaptureQueriesContext(connection) as ctx:
            user_profile_data = MainPageDataSerializer(self.user).data
            my_worry_get = WorryBoard.objects.select_related("letter").filter(author=self.user)
        # self.assertEqual(response.status_code, 200)
        self.assertEqual({"user_profile_data":user_profile_data},{"user_profile_data":user_profile_data})

        