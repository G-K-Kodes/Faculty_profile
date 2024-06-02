
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from django.views import View
from datetime import datetime, timedelta
from django.contrib.auth.hashers import check_password
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import get_template
from xhtml2pdf import pisa
from.models import Faculty_Login,ProfessionalDetail,Award,AcademicPerformance,Professionalexp,Profile,Course,CoursesTaught,PersonalDetail,Notification
from django.conf import settings
from django.contrib.staticfiles import finders
import os

def home(request):
    if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('/adminlogin/admin_page')
            return redirect(f'{request.user.username}/',faculty_id=request.user.username)
    return render(request, 'home/home_kamesh.html')

def logout_view(request):
    logout(request)
    # Redirect to the appropriate page after logout
    return redirect(home)

class StaffRequiredMixin:
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return staff_member_required(view)

class FacultyLoginView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        faculty_exists = Faculty_Login.objects.filter(username=username).exists()
        admin_exists = User.objects.filter(username=username).exists() 
        if faculty_exists:
            faculty=Faculty_Login.objects.get(username=username)
            if faculty.deleted==False:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    # Check if user is already logged in from another session
                    active_sessions = Session.objects.filter(expire_date__gte=timezone.now(), session_key__contains=user.id)
                    for session in active_sessions:
                        # Delete the session if found
                        session.delete()

                    # Login user
                    login(request, user)
                    return redirect(f'{request.user.username}/',faculty_id=request.user.username)   # Assuming 'about' is the name of the URL pattern for the about page
                else:
                    # Password doesn't match
                    return render(request, 'home/login.html', {'error_message': 'Invalid username or password'}) 
            else:
                return render(request, 'home/login.html', {'error_message': 'User no longer part of this institution'})
        elif admin_exists:
            admin = User.objects.get(username=username)
            if check_password(password, admin.password):
                # Password matches, log the user in
                active_sessions = Session.objects.filter(expire_date__gte=timezone.now(), session_key__contains=admin.id)
                
                for session in active_sessions:
                    # Delete the session if found
                    session.delete()

                # Log the user in
                login(request, admin)

                # Redirect to a page after successful login
                return redirect('/adminlogin/admin_page')
            else:
                # Password doesn't match
                return render(request, 'home/login.html', {'error_message': 'Invalid username or password'})
        else:
            return render(request, 'home/login.html', {'error_message': 'Invalid username or password'})
        
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('/adminlogin/admin_page')
            return redirect(f'{request.user.username}/',faculty_id=request.user.username)
        return render(request, 'home/login.html')

class AdminPageView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        if not request.user.is_staff:
             return render(request, 'home/forbidden.html', status=403)
        
        fac_objs = Faculty_Login.objects.filter(deleted=False)

        notifications = Notification.objects.order_by('-created_at')[:20]

        # Pass the queryset to the template context
        context = {
            'faculty_logins': list(fac_objs),
            'notifications': list(notifications)
        }

        return render(request,'home/admin_home_page.html',context)

class CreateSignupView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        return render(request, 'home/create_signup.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username.isdigit():
            return render(request, 'home/create_signup.html', {'error_message': 'Digital ID must be a number.'})
        if not len(username)>=8:
            return render(request, 'home/create_signup.html', {'error_message': 'The password should have 8 characters or more.'})
        
        if username and password:
            Faculty_Login.objects.create(username=username, password=password)
            User.objects.create(username=username, password=password, is_staff=False)
            # create professionaldetail obj
            return redirect('adminlogin/admin_page')  # Redirect to a success page
        else:
            return render(request, 'home/create_signup.html', {'error': 'Please provide both username and password.'})

class SetFacultySessionView(LoginRequiredMixin, View):
    def get(self, request, faculty_id):
        request.session['faculty_id'] = faculty_id
        faculty = get_object_or_404(Faculty_Login, username=faculty_id)
        if request.user.is_staff:
            notification_exists = Notification.objects.filter(recipient=faculty_id).exists()
            return render(request, 'home/faculty_info_page.html', {'faculty': faculty, 'notification_exists': notification_exists})
        return render(request, 'home/faculty_info_page.html', {'faculty': faculty})
        
    def post(self, request, faculty_id):
        request.session['faculty_id'] = faculty_id
        faculty = get_object_or_404(Faculty_Login, username=faculty_id)
        if 'request_edit_access' in request.POST:
            try:
                if not faculty.edit_granted:
                    # Check if edit access is not already granted
                    if not faculty.edit_request_time:
                        # Check if there's no previous request time
                        faculty.edit_request_time = timezone.now()
                        faculty.save()
                        messages.success(request, 'Edit access request sent successfully.')
                        
                        # Create a notification for the admin about the edit access request
                        Notification.objects.create(
                            message=f"Edit access requested by {faculty.personaldetail.first_name} {faculty.personaldetail.last_name}.",
                            recipient = faculty
                        )
                    else:
                        messages.error(request, 'Edit access request already sent. Please wait for admin response.')
                else:
                    messages.error(request, 'Edit access already granted.')

                # Handle other form submissions if needed
                return redirect('set_faculty_session', faculty_id=faculty_id)
            except:
                messages.error(request, 'Failed to update data')
        
        
        elif "handle_pending_request" in request.POST:
            try:
                # Retrieve the notification object
                notification = Notification.objects.get(recipient=faculty_id)
                
                # Retrieve the associated faculty login object
                faculty_login = notification.recipient
                
                # Update the faculty login object (example: grant edit permission)
                faculty_login.edit_granted = True
                faculty_login.edit_request_time=None
                faculty_login.edit_grant_time=timezone.now()
                expiry_delta = timedelta(hours=23, minutes=59, seconds=59)
                expiry_time = timezone.now() + expiry_delta
                faculty_login.edit_expiry_time = expiry_time
                faculty_login.save()

                # Delete the notification since the request has been handled
                notification.delete()
                messages.success(request, 'Edit access request accepted successfully.')
                return redirect('set_faculty_session', faculty_id=faculty_id)

            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(request, 'Failed to update data')
                return redirect('set_faculty_session_admin', faculty_id=faculty_id)
            
        elif 'profile_photo' in request.FILES:
            try:
                # Get or create profile for the faculty
                profile, created = Profile.objects.get_or_create(user=faculty)

                # Update profile picture
                profile.image = request.FILES['profile_photo']
                profile.save()
                messages.success(request, 'Profile picture updated successfully.')
                print("Profile after update:", profile.image)
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')  # Redirect to the profile page after successful upload
            if 'adminlogin' in request.path:
                return redirect('set_faculty_session_admin', faculty_id=faculty_id)
            return redirect('set_faculty_session', faculty_id=faculty_id)
            

class DeleteFacultyView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, faculty_id):
        if not request.user.is_staff:
             return render(request, 'home/forbidden.html', status=403)
        faculty = get_object_or_404(Faculty_Login, username=faculty_id) 
        faculty.deleted=True   
        p_details=get_object_or_404(ProfessionalDetail, user=faculty_id)  
        current_date = timezone.now().date() 
        p_details.leaving_date=current_date
        faculty.save()  # Save the changes to the faculty instance 
        p_details.save()
        return redirect('ad_page')

class ArchiveDataView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        if not request.user.is_staff:
            # If the user is not a staff member, return the forbidden page
            return render(request, 'home/forbidden.html', status=403)
        fac_objs = Faculty_Login.objects.filter(deleted=True)
        notifications = Notification.objects.order_by('-created_at')[:20]

        # Pass the queryset to the template context
        context = {
            'faculty_logins': list(fac_objs),
            'notifications': list(notifications)
        }
        return render(request, 'home/archive_data.html',context)

class AdminPersonalView(LoginRequiredMixin, View):
    def get(self, request, faculty_id):
        faculty = get_object_or_404(Faculty_Login, username=faculty_id) 
        context={'faculty':faculty}
        return render(request,'home/personal.html',context)

    def post(self, request, faculty_id):
        faculty = get_object_or_404(Faculty_Login, username=faculty_id) 
        context={'faculty':faculty}
        digital_id = request.POST.get('digital_id')
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        dob = request.POST.get('dob')
        cno = request.POST.get('contact_number')
        # acno = request.POST.get('alternate_contact_number')
        address = request.POST.get('address')
        email_id = request.POST.get('email')
        # alt_email_id = request.POST.get('alternate_email')
        aicte_id = request.POST.get('aicte_id')
        # anna_id = request.POST.get('anna_univ_faculty_id')
        blood_grp = request.POST.get('blood_group')  

        if not all([digital_id, fname, lname, dob, cno, address, email_id, aicte_id, blood_grp]):
            # If any required field is missing, return to the form page with an error message
            context['error_message'] = "Please fill in all the required fields."
            return render(request, 'home/personal.html', context)

        try:
            faculty.personaldetail.digital_id = digital_id
            faculty.personaldetail.first_name = fname
            faculty.personaldetail.last_name = lname
            faculty.personaldetail.dob = dob
            faculty.personaldetail.contact_no = cno
            # faculty.personaldetail.alternate_contact_no = acno
            faculty.personaldetail.address = address
            faculty.personaldetail.email_id = email_id
            # faculty.personaldetail.alternate_email_id = alt_email_id
            faculty.personaldetail.aicte_id = aicte_id
            # faculty.personaldetail.anna_univ_faculty_id = anna_id
            faculty.personaldetail.blood_grp = blood_grp 
            faculty.personaldetail.faculty_login=faculty
            # Create a new PersonalDetail object if it doesn't exist 
        except:
            faculty.personaldetail = PersonalDetail.objects.create(
                digital_id=digital_id,
                first_name=fname,
                last_name=lname,
                dob=dob,
                contact_no=cno,
                # alternate_contact_no=acno,
                address=address,
                email_id=email_id,
                # alternate_email_id=alt_email_id,
                aicte_id=aicte_id,
                # anna_univ_faculty_id=anna_id,
                blood_grp=blood_grp, 
                faculty_login=faculty
            ) 
        # Save the changes to the database
        faculty.personaldetail.save()
        messages.success(request, 'Personal details updated successfully')
        if 'adminlogin' in request.path:
            return redirect('admin_personal', faculty_id=faculty_id)
        return redirect('faculty_personal', faculty_id=faculty_id)

class AdminAcademicView(LoginRequiredMixin, View):
    def get(self, request, faculty_id):
        faculty = Faculty_Login.objects.get(username=faculty_id)
        academic = AcademicPerformance.objects.filter(user=faculty)
        context = {'academic': academic, 'faculty': faculty}
        return render(request, 'home/academic_performance.html', context)

    def post(self, request, faculty_id):
        try:
            faculty = Faculty_Login.objects.get(username=faculty_id)
            existing_records = AcademicPerformance.objects.filter(user=faculty)
            existing_records.order_by('sno')
            # Loop through the submitted data to update or create AcademicPerformance instances
            for key, value in request.POST.items():
                if key.startswith('degree') and value:
                    # Extract the counter from the field name
                    counter = key.replace('degree', '')
                    try:
                        existing_record=list(existing_records)[int(counter)-1]
                        existing_record.degree = request.POST.get('degree' + counter)
                        existing_record.institution_code=request.POST.get('institution-code' + counter)
                        existing_record.year_of_completion = request.POST.get('year-of-completion' + counter)
                        existing_record.remark = request.POST.get('remark' + counter)
                        existing_record.save()
                    except:
                        AcademicPerformance.objects.create(
                            user=faculty,
                            degree=request.POST.get('degree' + counter),
                            institution_code=request.POST.get('institution-code' + counter),
                            year_of_completion=request.POST.get('year-of-completion' + counter),
                            remark=request.POST.get('remark' + counter)
                        )
            messages.success(request, 'Academic performance details updated successfully')

            return redirect('admin_academic', faculty_id=faculty_id)
        except:
            messages.error(request, 'Failed to update data')

class AdminProfessionalView(LoginRequiredMixin, View):
    def get(self, request, faculty_id):
        faculty = get_object_or_404(Faculty_Login, pk=faculty_id)
        context = {'faculty': faculty}
        return render(request, 'home/professional_details.html', context)

    def post(self, request, faculty_id):
        faculty = get_object_or_404(Faculty_Login, pk=faculty_id)
        try:
            # Assuming you are passing the username in the POST data
            username = request.POST.get('username')
            
            # Check if the username matches the faculty's username
            if faculty.username == username:
                # Check if professionaldetail exists
                if hasattr(faculty, 'professionaldetail') and faculty.professionaldetail:
                    # Update the professional details
                    faculty.professionaldetail.designation = request.POST.get('designation')
                    faculty.professionaldetail.highest_qualification = request.POST.get('highest_qualification')
                    faculty.professionaldetail.joining_date = request.POST.get('joining_date')
                    
                    # Parse the leaving date properly
                    leaving_date = request.POST.get('leaving_date')
                    if leaving_date:
                        try:
                            faculty.professionaldetail.leaving_date = datetime.strptime(leaving_date, '%Y-%m-%d').date()
                        except ValueError:
                            # Handle invalid date format
                            return HttpResponse("Invalid leaving date format. Please use YYYY-MM-DD format.")
                    else:
                        # If leaving date is empty, set it to None
                        faculty.professionaldetail.leaving_date = None
                    
                    faculty.professionaldetail.languages_known = request.POST.get('languages_known')
                    faculty.professionaldetail.programming_languages = request.POST.get('programming_languages')
                    faculty.professionaldetail.save()
                else:
                    # Create a new professional detail instance
                    professional_detail = ProfessionalDetail.objects.create(
                        user=faculty,
                        designation=request.POST.get('designation'),
                        highest_qualification=request.POST.get('highest_qualification'),
                        joining_date=request.POST.get('joining_date'),
                        leaving_date=None if not request.POST.get('leaving_date') else datetime.strptime(request.POST.get('leaving_date'), '%Y-%m-%d').date(),
                        languages_known=request.POST.get('languages_known'),
                        programming_languages=request.POST.get('programming_languages')
                    )
                messages.success(request, 'Professional details updated successfully')
                # Redirect to some URL after updating professional details
                return redirect('admin_professional', faculty_id=faculty_id)
            else:
                # Handle the case where the provided username does not match the faculty's username
                return HttpResponse("Username does not match faculty's username.")
        except:
            messages.error(request, 'Failed to update data')

class AdminAwardsView(LoginRequiredMixin, View):
    def get(self, request, faculty_id):
        faculty = get_object_or_404(Faculty_Login, username=faculty_id)
        awards = Award.objects.filter(user=faculty)
        context = {'awards': awards, 'faculty': faculty}
        return render(request, 'home/awards.html', context)

    def post(self, request, faculty_id):
        faculty = get_object_or_404(Faculty_Login, username=faculty_id)
        try:
            # Process the form data
            for key, value in request.POST.items():
                if key.startswith('award-name') and value.strip():
                    # Extract the award number from the key
                    award_number = int(key.split('award-name')[1])

                    awards = Award.objects.filter(user=faculty, sno=award_number)

                    if awards.exists():
                        award = awards.first()  # Get the first matching award
                    else:
                        award = Award(user=faculty, sno=award_number)  # Create a new award object

                    # Update the award attributes
                    award.awardname = request.POST.get(f'award-name{award_number}')
                    award.year_of_rec = request.POST.get(f'year-of-rec{award_number}') 
                    award.proof = request.FILES.get(f'proof{award_number}')
                    award.save()

            messages.success(request, 'Award details updated successfully')
            # Redirect back to the awards page after saving
        except:
            messages.error(request, 'Failed to update data')
        return redirect('admin_awards', faculty_id=faculty_id)

class AdminProfessionalExpView(LoginRequiredMixin, View):
    def get(self, request, faculty_id):
        faculty = get_object_or_404(Faculty_Login, username=faculty_id)  
        prof_exp = Professionalexp.objects.filter(user=faculty) 
        context = {'faculty': faculty, 'prof_exp': prof_exp}
        return render(request, 'home/professional_experience.html', context)

    def post(self, request, faculty_id):
        try:
            # If the request is a POST, it means the form was submitted
            faculty = get_object_or_404(Faculty_Login, username=faculty_id)
            existing_records=Professionalexp.objects.filter(user=faculty)
            existing_records.order_by('sno')

            # Loop through the submitted data to update professional experience instances
            for key, value in request.POST.items():
                if key.startswith('designation') and value:
                    # Extract the counter from the field name
                    counter = key.split('-')[1]

                    try:
                        existing_record=list(existing_records)[int(counter)-1]
                        existing_record.institution_code=request.POST.get(f'institution-code-{counter}')
                        existing_record.designation=request.POST.get(f'designation-{counter}')
                        existing_record.from_date=request.POST.get(f'from-date-{counter}')
                        existing_record.to_date=request.POST.get(f'to-date-{counter}')
                        existing_record.save()
                    except:
                        Professionalexp.objects.create(
                            user=faculty,
                            designation=value,
                            institution_code=request.POST.get(f'institution-code-{counter}'),
                            from_date=request.POST.get(f'from-date-{counter}'),
                            to_date=request.POST.get(f'to-date-{counter}')
                        )
            messages.success(request, 'Academic performance details updated successfully')

            # Redirect back to the admin_profexp view after updating
            return redirect('admin_profexp', faculty_id=faculty_id)
        except:
            messages.error(request, 'Failed to update data')

class AdminCoursesTaughtView(LoginRequiredMixin, View):
    def get(self, request, faculty_id):
        faculty = get_object_or_404(Faculty_Login, username=faculty_id)   
        c_taughts = CoursesTaught.objects.filter(user=faculty)
        context={'c_taughts':c_taughts,'faculty':faculty}
        return render(request,'home/courses_taught.html',context)

    def post(self, request, faculty_id):
        try:
            # If the request is a POST, it means the form was submitted
            faculty = get_object_or_404(Faculty_Login, username=faculty_id)
            for key, value in request.POST.items():
                if key.startswith('course-id') and value:
                    # Extract the counter from the field name
                    counter = int(key.split('course-id')[1])

                    course=request.POST.get(f'course-id{counter}')
                    course_exists=Course.objects.filter(course_id=course).exists()

                    c_taughts = CoursesTaught.objects.filter(user=faculty, sno=counter)
                    
                    if c_taughts.exists():
                        c_taught = c_taughts.first()  # Get the first matching c_taught
                    else:
                        c_taught = CoursesTaught(user=faculty, sno=counter)  # Create a new c_taught object

                    # Update the award attributes
                    if course_exists:
                        c_taught.course_id=request.POST.get(f'course-id{counter}')
                        c_taught.save()
                    else:
                        messages.error(request, 'Course does not exist')
            messages.success(request, 'Courses updated successfully')
            return redirect('admin_coursestaught',faculty_id=faculty_id)
        except:
            messages.error(request, 'Failed to update data')

@login_required
def admin_page_filter(request):
    if request.method == 'POST': 
        all_faculty = ProfessionalDetail.objects.all()
        # Assuming your form fields are 'designation', 'doj', 'dob', and 'experience'
        designation = request.POST.get('designation')
        doj = request.POST.get('doj')
        dol = request.POST.get('dol')
        dob = request.POST.get('dob')
        experience = request.POST.get('experience')

        faculty_details1=faculty_details2=experienced_faculty=None
        

        # Assuming UserDetails model has fields: designation, doj, dob, experience
        # Querying the database for matching user details 
        if designation:
            user_details1 = ProfessionalDetail.objects.filter(designation=designation) 
            faculty_details1 = [detail.user for detail in user_details1 if not detail.user.deleted] 
        # if doj:
        #     user_details2=ProfessionalDetail.objects.filter(joining_date__gte=doj)
        # if dol:
        #     user_details2=ProfessionalDetail.objects.filter(joining_date__lte=dol)
        # faculty_details2 = [detail.user for detail in user_details2 if not detail.user.deleted] 
        if doj:
            if dol:
                # user_details2 = ProfessionalDetail.objects.filter(joining_date__gte=doj)  
                user_details2_1 = ProfessionalDetail.objects.filter(joining_date__lte=dol)  
                user_details2_2 = ProfessionalDetail.objects.filter(leaving_date__gte=doj)  
                user_details2_3 = ProfessionalDetail.objects.filter(leaving_date__lte=dol)   
                combined_user_details = user_details2_1.union(user_details2_2,user_details2_3)
                faculty_details2 = [detail.user for detail in combined_user_details if not detail.user.deleted] 
            else:
                user_details2 = ProfessionalDetail.objects.filter(joining_date__gte=doj)
                user_details2_1 = ProfessionalDetail.objects.filter(leaving_date__gte=doj) 
                user_details2_2 = ProfessionalDetail.objects.filter(leaving_date__isnull=True)

                combined_user_details = user_details2.union(user_details2_1,user_details2_2)
                faculty_details2 = [detail.user for detail in combined_user_details if not detail.user.deleted] 
          

    # Calculate today's date
        from datetime import date

# Get today's date

        today_date = date.today() 
        if experience:
            all_faculty = ProfessionalDetail.objects.all()

            # List to store experienced faculty members
            experienced_faculty = []

            # Traverse through each faculty member and calculate experience
            for faculty in all_faculty:
                # Calculate experience
                if faculty.leaving_date:
                    # If date of leaving is provided, calculate experience till leaving date
                    calc_experience = (faculty.leaving_date - faculty.joining_date).days / 365.25
                else:
                    # If date of leaving is not provided, calculate experience till today
                    calc_experience = (today_date - faculty.joining_date).days / 365.25
                
                # Check if the experience meets a certain threshold (e.g., 5 years)
                if calc_experience >=  int(experience) and not faculty.user.deleted:
                    # Add experienced faculty member to the list
                    experienced_faculty.append(faculty.user) 
        if faculty_details1!=None and faculty_details2!=None and experienced_faculty!=None:
            lists = [faculty_details1,faculty_details2,experienced_faculty]
        elif faculty_details1==None and faculty_details2==None and experienced_faculty==None:
            lists = []
        elif faculty_details1!=None and faculty_details2!=None and experienced_faculty==None:
            lists = [faculty_details1,faculty_details2]
        elif faculty_details1!=None and faculty_details2==None and experienced_faculty!=None:
            lists = [faculty_details1,experienced_faculty]
        elif faculty_details1==None and faculty_details2!=None and experienced_faculty!=None:
            lists = [faculty_details2,experienced_faculty]
        elif faculty_details1!=None and faculty_details2==None and experienced_faculty==None:
            lists = [faculty_details1]
        elif faculty_details1==None and faculty_details2!=None and experienced_faculty==None:
            lists = [faculty_details2]
        elif faculty_details1==None and faculty_details2==None and experienced_faculty!=None:
            lists = [experienced_faculty]

# Convert each list into a set
        sets = [set(lst) for lst in lists]

# Find the common elements using intersection
        common_elements = set.intersection(*sets)

# Convert the common elements back to a list if needed
        common_elements_list = list(common_elements)




        
        if common_elements_list:
            # If user details are found, render a template with the details
            return render(request, 'home/admin_home_page.html', {'faculty_logins': common_elements_list})
        else:
            # If user details are not found, render a template with a message
            return render(request, 'home/details_not_found.html') 

def admin_page_filter(request):
    if request.method == 'POST': 
        all_faculty = ProfessionalDetail.objects.all()
        # Assuming your form fields are 'designation', 'doj', 'dob', and 'experience'
        designation = request.POST.get('designation')
        doj = request.POST.get('doj')
        dol = request.POST.get('dol')
        dob = request.POST.get('dob')
        experience = request.POST.get('experience')
         
        print(designation) 
        print(doj) 
        print(dol) 
        print(experience)   
        faculty_details1=faculty_details2=experienced_faculty=None
        

        # Assuming UserDetails model has fields: designation, doj, dob, experience
        # Querying the database for matching user details 
        if designation:
            user_details1 = ProfessionalDetail.objects.filter(designation=designation) 
            faculty_details1 = [detail.user for detail in user_details1 if not detail.user.deleted] 
        # if doj:
        #     user_details2=ProfessionalDetail.objects.filter(joining_date__gte=doj)
        # if dol:
        #     user_details2=ProfessionalDetail.objects.filter(joining_date__lte=dol)
        # faculty_details2 = [detail.user for detail in user_details2 if not detail.user.deleted] 
        if doj:
            if dol:
                # user_details2 = ProfessionalDetail.objects.filter(joining_date__gte=doj)  
                user_details2_1 = ProfessionalDetail.objects.filter(joining_date__lte=dol)  
                user_details2_2 = ProfessionalDetail.objects.filter(leaving_date__gte=doj)  
                user_details2_3 = ProfessionalDetail.objects.filter(leaving_date__lte=dol)   
                combined_user_details = user_details2_1.union(user_details2_2,user_details2_3)
                faculty_details2 = [detail.user for detail in combined_user_details if not detail.user.deleted] 
            else:
                user_details2 = ProfessionalDetail.objects.filter(joining_date__gte=doj)
                user_details2_1 = ProfessionalDetail.objects.filter(leaving_date__gte=doj) 
                user_details2_2 = ProfessionalDetail.objects.filter(leaving_date__isnull=True)

                combined_user_details = user_details2.union(user_details2_1,user_details2_2)
                faculty_details2 = [detail.user for detail in combined_user_details if not detail.user.deleted] 
          

    # Calculate today's date
        from datetime import date

# Get today's date

        today_date = date.today() 
        if experience:
            all_faculty = ProfessionalDetail.objects.all()

            # List to store experienced faculty members
            experienced_faculty = []

            # Traverse through each faculty member and calculate experience
            for faculty in all_faculty:
                # Calculate experience
                if faculty.leaving_date:
                    # If date of leaving is provided, calculate experience till leaving date
                    calc_experience = (faculty.leaving_date - faculty.joining_date).days / 365.25
                else:
                    # If date of leaving is not provided, calculate experience till today
                    calc_experience = (today_date - faculty.joining_date).days / 365.25
                
                # Check if the experience meets a certain threshold (e.g., 5 years)
                if calc_experience >=  int(experience) and not faculty.user.deleted:
                    # Add experienced faculty member to the list
                    experienced_faculty.append(faculty.user) 
        if faculty_details1!=None and faculty_details2!=None and experienced_faculty!=None:
            lists = [faculty_details1,faculty_details2,experienced_faculty]
        elif faculty_details1==None and faculty_details2==None and experienced_faculty==None:
            lists = []
        elif faculty_details1!=None and faculty_details2!=None and experienced_faculty==None:
            lists = [faculty_details1,faculty_details2]
        elif faculty_details1!=None and faculty_details2==None and experienced_faculty!=None:
            lists = [faculty_details1,experienced_faculty]
        elif faculty_details1==None and faculty_details2!=None and experienced_faculty!=None:
            lists = [faculty_details2,experienced_faculty]
        elif faculty_details1!=None and faculty_details2==None and experienced_faculty==None:
            lists = [faculty_details1]
        elif faculty_details1==None and faculty_details2!=None and experienced_faculty==None:
            lists = [faculty_details2]
        elif faculty_details1==None and faculty_details2==None and experienced_faculty!=None:
            lists = [experienced_faculty]

# Convert each list into a set
        sets = [set(lst) for lst in lists]

# Find the common elements using intersection
        common_elements = set.intersection(*sets)

# Convert the common elements back to a list if needed
        common_elements_list = list(common_elements)

        if common_elements_list:
            # If user details are found, render a template with the details
            return render(request, 'home/admin_home_page.html', {'faculty_logins': common_elements_list})
        else:
            # If user details are not found, render a template with a message
            return render(request, 'home/details_not_found.html') 
        



def archive_page_filter(request):
    if request.method == 'POST': 
        all_faculty = ProfessionalDetail.objects.all()
        # Assuming your form fields are 'designation', 'doj', 'dob', and 'experience'
        designation = request.POST.get('designation')
        doj = request.POST.get('doj')
        dol = request.POST.get('dol')
        dob = request.POST.get('dob')
        experience = request.POST.get('experience')
         
        print(designation) 
        print(doj) 
        print(dol) 
        print(experience)   
        faculty_details1=faculty_details2=experienced_faculty=None
        

        # Assuming UserDetails model has fields: designation, doj, dob, experience
        # Querying the database for matching user details 
        if designation:
            user_details1 = ProfessionalDetail.objects.filter(designation=designation) 
            faculty_details1 = [detail.user for detail in user_details1 if  detail.user.deleted] 
        if doj:
            if dol:
                # user_details2 = ProfessionalDetail.objects.filter(joining_date__gte=doj)  
                user_details2_1 = ProfessionalDetail.objects.filter(joining_date__lte=dol)  
                user_details2_2 = ProfessionalDetail.objects.filter(leaving_date__gte=doj)  
                user_details2_3 = ProfessionalDetail.objects.filter(leaving_date__lte=dol)   
                combined_user_details = user_details2_1.union(user_details2_2,user_details2_3)
                faculty_details2 = [detail.user for detail in combined_user_details if  detail.user.deleted] 
            else:
                user_details2 = ProfessionalDetail.objects.filter(joining_date__gte=doj)
                user_details2_1 = ProfessionalDetail.objects.filter(leaving_date__gte=doj) 
                user_details2_2 = ProfessionalDetail.objects.filter(leaving_date__isnull=True)

                combined_user_details = user_details2.union(user_details2_1,user_details2_2)
                faculty_details2 = [detail.user for detail in combined_user_details if  detail.user.deleted] 
          

    # Calculate today's date
        from datetime import date

# Get today's date

        today_date = date.today() 
        if experience:
            all_faculty = ProfessionalDetail.objects.all()

            # List to store experienced faculty members
            experienced_faculty = []

            # Traverse through each faculty member and calculate experience
            for faculty in all_faculty:
                # Calculate experience
                if faculty.leaving_date:
                    # If date of leaving is provided, calculate experience till leaving date
                    calc_experience = (faculty.leaving_date - faculty.joining_date).days / 365.25
                else:
                    # If date of leaving is not provided, calculate experience till today
                    calc_experience = (today_date - faculty.joining_date).days / 365.25
                
                # Check if the experience meets a certain threshold (e.g., 5 years)
                if calc_experience >=  int(experience) and  faculty.user.deleted:
                    # Add experienced faculty member to the list
                    experienced_faculty.append(faculty.user) 
        if faculty_details1!=None and faculty_details2!=None and experienced_faculty!=None:
            lists = [faculty_details1,faculty_details2,experienced_faculty]
        elif faculty_details1==None and faculty_details2==None and experienced_faculty==None:
            lists = []
        elif faculty_details1!=None and faculty_details2!=None and experienced_faculty==None:
            lists = [faculty_details1,faculty_details2]
        elif faculty_details1!=None and faculty_details2==None and experienced_faculty!=None:
            lists = [faculty_details1,experienced_faculty]
        elif faculty_details1==None and faculty_details2!=None and experienced_faculty!=None:
            lists = [faculty_details2,experienced_faculty]
        elif faculty_details1!=None and faculty_details2==None and experienced_faculty==None:
            lists = [faculty_details1]
        elif faculty_details1==None and faculty_details2!=None and experienced_faculty==None:
            lists = [faculty_details2]
        elif faculty_details1==None and faculty_details2==None and experienced_faculty!=None:
            lists = [experienced_faculty]

# Convert each list into a set
        sets = [set(lst) for lst in lists]

# Find the common elements using intersection
        common_elements = set.intersection(*sets)

# Convert the common elements back to a list if needed
        common_elements_list = list(common_elements)
        
        if common_elements_list:
            # If user details are found, render a template with the details
            return render(request, 'home/archive_data.html', {'faculty_logins': common_elements_list})
        else:
            # If user details are not found, render a template with a message
            return render(request, 'home/details_not_found.html')


class CoursesView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        if not request.user.is_staff:
             return render(request, 'home/forbidden.html', status=403)
        
        courses = Course.objects.filter(deleted=False)
        notifications = Notification.objects.order_by('-created_at')[:20]
        # Pass the queryset to the template context
        context = {
            'courses': list(courses),
            'notifications' : list(notifications)
        }
        return render(request,'home/course_view.html',context)
    
    def post(self, request):
        course_id=request.POST.get('course_id')
        course_name=request.POST.get('course_name')
        course_type=request.POST.get('course_type')
        if course_id and course_name and course_type:
            Course.objects.create(course_id=course_id, course_name=course_name, course_type=course_type)
        return redirect('courses_view')

class DeleteCourseView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, course_id):
        if not request.user.is_staff:
             return render(request, 'home/forbidden.html', status=403)
        course = get_object_or_404(Course, course_id=course_id) 
        course.deleted=True
        course.save()  # Save the changes to the faculty instance 
        return redirect('courses_view')

class ArchiveCoursesView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        if not request.user.is_staff:
            # If the user is not a staff member, return the forbidden page
            return render(request, 'home/forbidden.html', status=403)
        courses = Course.objects.filter(deleted=True)
        notifications = Notification.objects.order_by('-created_at')[:20]

        # Pass the queryset to the template context
        context = {
            'courses': list(courses),
            'notifications': list(notifications)
        }
        return render(request, 'home/archive_courses.html',context)
@login_required
def course_page_filter(request):
    if request.method=='POST':
        course_type=request.POST.get('course-type')
        filtered_courses=Course.objects.filter(course_type=course_type)
        filtered_courses_list=list(filtered_courses)
        if filtered_courses_list:
            return render(request,'home/course_view.html', {'courses':filtered_courses_list})
        else:
            # If user details are not found, render a template with a message
            return render(request, 'home/details_not_found.html')
@login_required
def archive_course_filter(request):
    if request.method=='POST':
        course_type=request.POST.get('course-type')
        filtered_courses=Course.objects.filter(course_type=course_type)
        filtered_courses_list=list(filtered_courses)
        if filtered_courses_list:
            return render(request,'home/archive_courses.html', {'courses':filtered_courses_list})
        else:
            # If user details are not found, render a template with a message
            return render(request, 'home/details_not_found.html')
        
def generate_report(request, username):
    def link_callback(uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        result = finders.find(uri)
        if result:
                if not isinstance(result, (list, tuple)):
                        result = [result]
                result = list(os.path.realpath(path) for path in result)
                path=result[0]
        else:
                sUrl = settings.STATIC_URL        # Typically /static/
                sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                mUrl = settings.MEDIA_URL         # Typically /media/
                mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                if uri.startswith(mUrl):
                        path = os.path.join(mRoot, uri.replace(mUrl, ""))
                elif uri.startswith(sUrl):
                        path = os.path.join(sRoot, uri.replace(sUrl, ""))
                else:
                        return uri

        # make sure that file exists
        if not os.path.isfile(path):
                raise RuntimeError(
                        'media URI must start with %s or %s' % (sUrl, mUrl)
                )
        return path
    faculty = get_object_or_404(Faculty_Login, username=username)
    
    # Fetch professional experience and academic performance
    professional_experiences = Professionalexp.objects.filter(user=faculty)
    academic_performances = AcademicPerformance.objects.filter(user=faculty)
    
    report_data = {
        'faculty': {
            'username': faculty.username,
            'personaldetail': {
                'first_name': faculty.personaldetail.first_name,
                'last_name': faculty.personaldetail.last_name,
                'dob': faculty.personaldetail.dob,
                'contact_no': faculty.personaldetail.contact_no,
                'address': faculty.personaldetail.address,
                'email_id': faculty.personaldetail.email_id,
                'aicte_id': faculty.personaldetail.aicte_id,
                'blood_grp': faculty.personaldetail.get_blood_grp_display(),
            },
            'professionaldetail': {
                'designation': faculty.professionaldetail.designation,
                'highest_qualification': faculty.professionaldetail.get_highest_qualification_display(),
                'joining_date': faculty.professionaldetail.joining_date,
                'years_of_experience': faculty.professionaldetail.years_of_experience,
                'languages_known': faculty.professionaldetail.languages_known,
                'programming_languages': faculty.professionaldetail.programming_languages,
            },
            'professional_experiences': professional_experiences,
            'academic_performances': academic_performances,
        }
    }

    template_file='home/report_template.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_file)
    html = template.render(report_data)

    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ssn_{faculty.personaldetail.first_name}_{faculty.personaldetail.last_name}_report.pdf"'

     # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response