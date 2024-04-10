from django.contrib import admin

# Register your models here.
from .models import Faculty_Login  
  
from .models import Profile
from .models import Professionalexp
from .models import PersonalDetail
from .models import ProfessionalDetail 
from .models import Award
from .models import AcademicPerformance 
from .models import Course 
from .models import CoursesTaught




# admin.site.register(Faculty_Login)
# from .models import Faculty_Login 

admin.site.register(Faculty_Login)
admin.site.register(Profile)
admin.site.register(Professionalexp)
admin.site.register(PersonalDetail)
admin.site.register(ProfessionalDetail)
admin.site.register(Award)
admin.site.register(AcademicPerformance)
admin.site.register(Course)
admin.site.register(CoursesTaught)