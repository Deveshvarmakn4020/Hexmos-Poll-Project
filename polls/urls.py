from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path("", views.get_views, name="getviews"),
    path('<int:question_id>/', views.increment_poll_vote, name='increment_poll_vote'),
    path('detail/<int:question_id>/', views.get_poll_detail, name='get_poll_detail'),
    path('tags/', views.get_tags, name='get_tags'),
    path("filteredpoll/", views.get_filtered_polls, name='get_filtered_polls'),
    path("<int:question_id>/", views.get_views, name="detailview"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("create/", views.create_poll, name="createpoll"),
]

