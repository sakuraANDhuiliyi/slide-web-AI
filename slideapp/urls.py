# slideapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_slide, name='create_slide'),
    path('edit/<int:slide_id>/', views.edit_slide, name='edit_slide'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('delete/<int:slide_id>/', views.delete_slide, name='delete_slide'),
    path('toggle_lock/<int:slide_id>/', views.toggle_lock, name='toggle_lock'),
    path('toggle_public/<int:slide_id>/', views.toggle_public, name='toggle_public'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('public/', views.public_slides, name='public_slides'),
    path('public/edit/<int:slide_id>/', views.public_edit_slide, name='public_edit_slide'),
    path('ai_generate/', views.ai_generate_slide, name='ai_generate_slide'),
    path('import_document/', views.import_document, name='import_document'),
    path('add_image_to_slide/', views.add_image_to_slide, name='add_image_to_slide'),
    path('export/<int:slide_id>/pptx/', views.export_to_pptx, name='export_to_pptx'),
]