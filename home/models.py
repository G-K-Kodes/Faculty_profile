from django.db import models 
from django.utils import timezone 
from django.contrib.auth.models import User  
from django.contrib.auth.hashers import make_password 
from django.core.validators import MinLengthValidator, MaxLengthValidator  
from django.contrib.postgres.fields import ArrayField   
from datetime import datetime




# Ce.reate your models her
# class Archive(models.Model): 
#     print('hi')
#     model_name = models.CharField(max_length=100, primary_key=True) 
#     archived_data = models.JSONField() 
#     print('bye')
#     deleted_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.model_name} - {self.deleted_at}" 


class Faculty_Login(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=100)  # Store the hashed password 
    deleted = models.BooleanField(default=False)  # Added deleted column
    edit_granted = models.BooleanField(default=False)  # Added edit_granted column
    edit_request_time = models.DateTimeField(default=None, null=True, blank=True)
    edit_grant_time = models.DateTimeField(default=None, null=True, blank=True)
    edit_expiry_time = models.DateTimeField(default=None, null=True, blank=True)
    
    # Other attributes of the Faculty model
    
    def save(self, *args, **kwargs):
        # Hash the password before saving
        self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username   

    def set_password(self,passw):
        self.password=passw  
    
    def delete(self, *args, **kwargs):  

        self.deleted = True
        self.save()
        # archived_data = {}

        # if hasattr(self, 'personaldetail'):
        #     personal_detail_data = {
        #         'first_name': self.personaldetail.first_name,
        #         'last_name': self.personaldetail.last_name,
        #         'contact_no': self.personaldetail.contact_no,
        #         'address': self.personaldetail.address,
        #         'email_id': self.personaldetail.email_id,
        #         'aicte_id': self.personaldetail.aicte_id,
        #         'blood_grp': self.personaldetail.blood_grp,
        #         # Add other fields as needed
        #     }
        #     archived_data['personaldetail'] = personal_detail_data 
        # if hasattr(self, 'professionaldetail'):   
        #     if not self.professionaldetail.leaving_date: 
        #         self.professionaldetail.leaving_date=datetime.now()

                
        #     professional_detail_data = {
        #         'designation': self.professionaldetail.designation,
        #         'highest_qualification': self.professionaldetail.highest_qualification,
        #         'joining_date': self.professionaldetail.joining_date.strftime("%Y-%m-%d %H:%M:%S"),
        #         'leaving_date': self.professionaldetail.leaving_date.strftime("%Y-%m-%d %H:%M:%S"),
        #         'languages_known': self.professionaldetail.languages_known,
        #         'programming_languages': self.professionaldetail.programming_languages,
        #         # Add other fields as needed
        #     }
            

        #     archived_data['professionaldetail'] = professional_detail_data

        # if self.professionalexp_set.exists(): 
        #     print(type(self.professionalexp_set.exists())) 
        #     data=list(self.professionalexp_set.all().values())  
        #     final_data=[]
        #     for prof_exp in data: 
        #         print('exp data')  
        #         print(prof_exp)
        #         exp_data={
        #             'designation':prof_exp['designation'],
        #             'institution_code':prof_exp['institution_code'],
        #             'from_date':prof_exp['from_date'].strftime("%Y-%m-%d %H:%M:%S"),
        #             'to_date':prof_exp['to_date'].strftime("%Y-%m-%d %H:%M:%S")
        #         } 
        #         final_data.append(exp_data)
        #     archived_data['professionalexp']=final_data

        # if self.academicperformance_set.exists():
        #     data = list(self.academicperformance_set.all().values()) 
        #     final_data=[]
        #     for acad_per in data: 
        #         acad_data={
        #             'degree':acad_per['degree'],
        #             'institution_code':acad_per['institution_code'],
        #             'year_of_completion':acad_per['year_of_completion'].strftime("%Y-%m-%d %H:%M:%S"),
        #             'remark':acad_per['remark']
        #         } 
        #         final_data.append(acad_data)
        #     archived_data['academicperformance']=final_data

        # if self.award_set.exists():
        #     data = list(self.award_set.all().values()) 
        #     final_data=[]
        #     for award in data: 
        #         award_data={
        #             'awardname':award['awardname'],
        #             'year_of_rec':award['year_of_rec'].strftime("%Y-%m-%d %H:%M:%S")
        #         } 
        #         final_data.append(award_data)
        #     archived_data['awards']=final_data

        # if self.coursestaught_set.exists():
        #     data = list(self.coursestaught_set.all().values()) 
        #     final_data=[]
        #     for taught_course in data:  
        #         print(taught_course)
        #         taught_course_data={
        #             'course_id':taught_course['course_id_id']
        #         } 
        #         final_data.append(taught_course_data)
        #     archived_data['coursestaught']=final_data

        # print('as')  
        # print(archived_data)
        # Archive.objects.create(model_name=self.username, archived_data=archived_data) 
        # print('of')
        # super().delete(*args, **kwargs)

    # Add other related models' data to archived_data as needed
    
class PersonalDetail(models.Model):
    DIGITAL_ID_MAX_LENGTH = 50
    FIRST_NAME_MAX_LENGTH = 100
    LAST_NAME_MAX_LENGTH = 100
    ADDRESS_MAX_LENGTH = 255
    EMAIL_ID_MAX_LENGTH = 100
    AICTE_ID_MAX_LENGTH = 50
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('B+', 'B+'),
        ('AB+', 'AB+'),
        ('O+', 'O+'),
        ('A-', 'A-'),
        ('B-', 'B-'),
        ('AB-', 'AB-'),
        ('O-', 'O-'),
    ]
    # sno = models.AutoField(primary_key=True)
    digital_id = models.CharField(max_length=DIGITAL_ID_MAX_LENGTH,primary_key=True)  
    dob=models.DateField(null=True)
    first_name = models.CharField(max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=LAST_NAME_MAX_LENGTH)
    contact_no = models.CharField(max_length=100)  # Assuming contact number as string
    address = models.CharField(max_length=ADDRESS_MAX_LENGTH)
    email_id = models.EmailField(max_length=EMAIL_ID_MAX_LENGTH)
    aicte_id = models.CharField(max_length=AICTE_ID_MAX_LENGTH)
    blood_grp = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    faculty_login = models.OneToOneField(Faculty_Login, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.faculty_login.username}-{self.first_name} {self.last_name}"


class Course(models.Model):
    course_type_choices=[('Theory','Theory'), ('Practical', 'Practical'), ('Theory-Cum-Practical', 'Theory-Cum-Practical')]
    course_id = models.CharField(max_length=50,primary_key=True)
    course_name = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)
    course_type = models.CharField(max_length=40, choices=course_type_choices, default='Theory')

    def __str__(self):
        return f"{self.course_id} - {self.course_name}" 
    
class Professionalexp(models.Model):
    SSN_ID_MAX_LENGTH = 50
    DESIGNATION_MAX_LENGTH = 100
    INSTITUTION_CODE_MAX_LENGTH = 50 

    sno = models.AutoField(primary_key=True)
    user = models.ForeignKey(Faculty_Login, on_delete=models.CASCADE)  
    designation = models.CharField(max_length=DESIGNATION_MAX_LENGTH)
    institution_code = models.CharField(max_length=INSTITUTION_CODE_MAX_LENGTH)
    from_date = models.DateField()
    to_date = models.DateField()

    @property
    def total_years(self):
        if self.from_date and self.to_date:
            return (self.to_date - self.from_date).days // 365
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.designation} -({self.institution_code})" 

class CoursesTaught(models.Model): 
    sno=models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(Faculty_Login, on_delete=models.CASCADE)


class AcademicPerformance(models.Model): 
    sno=models.AutoField(primary_key=True)
    user = models.ForeignKey(Faculty_Login, on_delete=models.CASCADE)
    DEGREE_MAX_LENGTH = 100
    INSTITUTION_CODE_MAX_LENGTH = 50

    degree = models.CharField(max_length=DEGREE_MAX_LENGTH)
    institution_code = models.CharField(max_length=INSTITUTION_CODE_MAX_LENGTH)
    year_of_completion = models.DateField()
    remark = models.CharField(max_length=255)  


    def __str__(self):
        return f"{self.user.username} - {self.degree} ({self.year_of_completion})" 
    

 

    # class Meta:
    #     # Define unique constraint on user and degree combination
    #     unique_together = [['user', 'degree']]

    

class Award(models.Model): 
    sno=models.AutoField(primary_key=True)
    user = models.ForeignKey(Faculty_Login, on_delete=models.CASCADE)
    awardname = models.CharField(max_length=255)
    year_of_rec = models.DateField()  
    proof = models.FileField(upload_to='documents/',null=True)
    

    def __str__(self):
        return f"{self.user.username} - {self.awardname} ({self.year_of_rec.year})"    

    # class Meta:
    #     # Define unique constraint on user and awardname combination
    #     unique_together = [['user', 'awardname']]
    
class ProfessionalDetail(models.Model):
    DESIGNATION_MAX_LENGTH = 100
    HIGHEST_QUALIFICATION_CHOICES = [
        ('Bachelor', 'Bachelor'),
        ('Master', 'Master'),
        ('PhD', 'PhD'),
        # Add more choices as needed
    ] 
    sno=models.AutoField(primary_key=True)
    designation = models.CharField(max_length=DESIGNATION_MAX_LENGTH)
    highest_qualification = models.CharField(max_length=20, choices=HIGHEST_QUALIFICATION_CHOICES)
    joining_date = models.DateField(default=timezone.now)
    leaving_date = models.DateField(blank=True, null=True)
    languages_known = models.CharField(max_length=255, blank=True, null=True)
    programming_languages = models.CharField(max_length=255, blank=True, null=True) 
    user = models.OneToOneField(Faculty_Login, on_delete=models.CASCADE)  

    @property
    def years_of_experience(self):
        if self.leaving_date:
            return self.leaving_date.year - self.joining_date.year
        else:
            return timezone.now().year - self.joining_date.year

    def __str__(self):
        return f"{self.user.username}-{self.designation} - {self.highest_qualification}"  
    

class Profile(models.Model): 
    user = models.OneToOneField(Faculty_Login, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'
    
class Notification(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    recipient = models.ForeignKey(Faculty_Login, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recipient.username} - {self.message}"