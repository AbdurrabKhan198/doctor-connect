from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Contact form endpoints
    path('api/contact/', views.contact_api, name='contact_api'),
    path('api/newsletter/', views.newsletter_api, name='newsletter_api'),
    path('api/quick-contact/', views.quick_contact_api, name='quick_contact_api'),
    
    # Dashboard (staff only)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/inquiry/<int:inquiry_id>/', views.inquiry_detail, name='inquiry_detail'),
]
