from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('rankings/', views.rankings_view, name='rankings'),

    # Chess API
    path('api/new-game/', views.api_new_game, name='api_new_game'),
    path('api/game-state/', views.api_game_state, name='api_game_state'),
    path('api/legal-moves/', views.api_legal_moves, name='api_legal_moves'),
    path('api/make-move/', views.api_make_move, name='api_make_move'),
]

