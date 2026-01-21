from django.urls import path

from library.usuarios.views import (
    ChangePasswordView,
    LoginView,
    ProfileEditView,
    RegisterView,
    dashboard,
    delete_account,
    logout_view,
    profile,
    remove_avatar,
    update_preferences,
    upload_avatar,
)

app_name = 'usuarios'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/preferences/', update_preferences, name='update_preferences'),
    path('profile/upload-avatar/', upload_avatar, name='upload_avatar'),
    path('profile/delete-account/', delete_account, name='delete_account'),
    path('profile/avatar/remove/', remove_avatar, name='remove_avatar'),
    path('update_profile/', ProfileEditView.as_view(), name='profile_edit'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
]
