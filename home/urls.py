from django.urls import path,include 
from . import views

urlpatterns = [
    path("",views.home,name='home_page'),
    # path("about/",views.about,name='about_page'),  
    path("facultylogin/",views.faculty_login,name='fac_login'),
    path("adminlogin/",views.admin_login,name='ad_login'), 
    path("adminlogin/admin_page",views.admin_page,name='ad_page'), 
    path("adminlogin/admin_page/delete/<int:faculty_id>",views.delete_faculty,name='delete_faculty'), 
    path('adminlogin/admin_page/archive/', views.archive_data_view, name='archive_data_view'),
    path("adminlogin/admin_page/filter",views.admin_page_filter,name='ad_page_filter'),
    path("adminlogin/admin_page/archive/filter",views.archive_page_filter,name='archive_page_filter'),
    path('adminlogin/<int:faculty_id>/', views.set_faculty_session, name='set_faculty_session'),  
    path('create_signup',views.create_signup,name='create_signup'),
    path('success/', views.success_view, name='success_url'),
    # path('<str:username>/', views.generate_report, name='generate_report'),
    # path('update_academic_performance/<str:faculty_id>/', views.update_academic_performance, name='update_academic_performance'),

    path('adminlogin/<int:faculty_id>/admin_personal', views.admin_personal, name='admin_personal'),
    path('adminlogin/<int:faculty_id>/admin_academic', views.admin_academic, name='admin_academic'),
    path('adminlogin/<int:faculty_id>/admin_professional', views.admin_professional, name='admin_professional'),
    path('adminlogin/<int:faculty_id>/admin_professionalexp', views.admin_profexp, name='admin_profexp'),
    path('adminlogin/<int:faculty_id>/admin_coursestaught', views.admin_coursestaught, name='admin_coursestaught'), 
    path('adminlogin/<int:faculty_id>/admin_awards', views.admin_awards, name='admin_awards'), 





    path('<int:faculty_id>/admin_personal', views.admin_personal, name='admin_personal_ori'),
    path('<int:faculty_id>/admin_academic', views.admin_academic, name='admin_academic_ori'),
    path('<int:faculty_id>/admin_professional', views.admin_professional, name='admin_professional_ori'),
    path('<int:faculty_id>/admin_professionalexp', views.admin_profexp, name='admin_profexp_ori'),
    path('<int:faculty_id>/admin_coursestaught', views.admin_coursestaught, name='admin_coursestaught_ori'), 
    path('<int:faculty_id>/admin_awards', views.admin_awards, name='admin_awards_ori'), 




    path('<int:faculty_id>/', views.set_faculty_session, name='set_faculty_session'),

    # path('adminlogin/details', views.faculty_detail, name='faculty_detail'),
     # Other URL patterns...

]


