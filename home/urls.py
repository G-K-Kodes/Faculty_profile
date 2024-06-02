from django.urls import path,include 
from . import views

urlpatterns = [
    path("", views.home, name='home_page'),
    path("login/", views.FacultyLoginView.as_view(), name='fac_login'),
    path('logout/', views.logout_view, name='logout'),
    path("adminlogin/admin_page/", views.AdminPageView.as_view(), name='ad_page'),
    path('adminlogin/courses/', views.CoursesView.as_view(), name='courses_view'),
    path('adminlogin/courses/archive/', views.ArchiveCoursesView.as_view(), name='archive_courses_view'),
    path("adminlogin/courses/delete/<str:course_id>", views.DeleteCourseView.as_view(), name='delete_course'),
    path("adminlogin/admin_page/delete/<int:faculty_id>", views.DeleteFacultyView.as_view(), name='delete_faculty'), 
    path('adminlogin/admin_page/archive/', views.ArchiveDataView.as_view(), name='archive_data_view'),
    path('adminlogin/admin_page/archive/filter', views.archive_page_filter, name='archive_page_filter'),
    path("adminlogin/admin_page/filter",views.admin_page_filter,name='ad_page_filter'),
    path('adminlogin/courses/filter', views.course_page_filter, name='course_page_filter'),
    path('adminlogin/courses/archive/filter', views.archive_course_filter, name='archive_course_filter'),
    path("adminlogin/admin_page/archive/filter", views.AdminPageView.as_view(), name='archive_page_filter'),
    path('adminlogin/<int:faculty_id>', views.SetFacultySessionView.as_view(), name='set_faculty_session_admin'),  
    path('create_signup', views.CreateSignupView.as_view(), name='create_signup'),
    path('<str:username>/report', views.generate_report, name='generate_report'),
    
    path('adminlogin/<int:faculty_id>/admin_personal', views.AdminPersonalView.as_view(), name='admin_personal'),
    path('adminlogin/<int:faculty_id>/admin_academic', views.AdminAcademicView.as_view(), name='admin_academic'),
    path('adminlogin/<int:faculty_id>/admin_professional', views.AdminProfessionalView.as_view(), name='admin_professional'),
    path('adminlogin/<int:faculty_id>/admin_professionalexp', views.AdminProfessionalExpView.as_view(), name='admin_profexp'),
    path('adminlogin/<int:faculty_id>/admin_coursestaught', views.AdminCoursesTaughtView.as_view(), name='admin_coursestaught'), 
    path('adminlogin/<int:faculty_id>/admin_awards', views.AdminAwardsView.as_view(), name='admin_awards'), 





    path('<int:faculty_id>/admin_personal', views.AdminPersonalView.as_view(), name='faculty_personal'),
    path('<int:faculty_id>/admin_academic', views.AdminAcademicView.as_view(), name='faculty_academic'),
    path('<int:faculty_id>/admin_professional', views.AdminProfessionalView.as_view(), name='faculty_professional'),
    path('<int:faculty_id>/admin_professionalexp', views.AdminProfessionalExpView.as_view(), name='faculty_profexp'),
    path('<int:faculty_id>/admin_coursestaught', views.AdminCoursesTaughtView.as_view(), name='faculty_coursestaught'), 
    path('<int:faculty_id>/admin_awards', views.AdminCoursesTaughtView.as_view(), name='faculty_awards'), 




    path('<int:faculty_id>/', views.SetFacultySessionView.as_view(), name='set_faculty_session'),

    # path('adminlogin/details', views.faculty_detail, name='faculty_detail'),
     # Other URL patterns...

]
