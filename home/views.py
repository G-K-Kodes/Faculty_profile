
# Create your views here.
from django.shortcuts import render,HttpResponse,redirect 
from django.contrib.auth.forms import UserCreationForm  
from .models import Faculty_Login,ProfessionalDetail,Award,AcademicPerformance,Professionalexp,Profile,Course,CoursesTaught,PersonalDetail
from django.contrib.auth.hashers import make_password,check_password   
from django.contrib.auth.models import User 
from django.contrib.auth.hashers import check_password
from django.urls import reverse  
from django.shortcuts import render, get_object_or_404 
from datetime import datetime  
# from .models import Archive




# posts=[{
#     'id':1,
#     'name':'karna', 
#     'context':'1st post'
# },
# {
#     'id':2,
#     'name':'jarna', 
#     'context':'2nt post'

# },
# { 
#     'id':3,
#     'name':'surna', 
#     'context':'3rt post'

# }
# ]

def home(request):
   
    return render(request,'home/home_kamesh.html')
# def about(request): 
#     content={'title':'about bro'}
#     return render(request,'home/about.html',content) 

def register(request):
    form=UserCreationForm() 
    return render(request,'') 



def faculty_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            faculty = Faculty_Login.objects.get(username=username)
        except Faculty_Login.DoesNotExist:
            return render(request, 'home/flogin.html', {'error_message': 'Invalid username or password'}) 
        
        print(password) 
        print(faculty.password)
        if faculty.deleted==False:
            if check_password(password, faculty.password):
                # Password matches, log the user in
                request.session['user_id'] = faculty.username
                # Redirect to a page after successful login
                return redirect(f'/{username}')  # Assuming 'about' is the name of the URL pattern for the about page
            else:
                # Password doesn't match
                return render(request, 'home/flogin.html', {'error_message': 'Invalid username or password'}) 
        else:
            return render(request, 'home/flogin.html', {'error_message': 'User no longer part of this institution'}) 

    
    return render(request, 'home/flogin.html')   




def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            admin = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'home/alogin.html', {'error_message': 'Invalid username or password'}) 
        
        print(password) 
        print(admin.password)
        
        if check_password(password, admin.password):
            # Password matches, log the user in
            request.session['user_id'] = admin.username
            # Redirect to a page after successful login
            return redirect('/adminlogin/admin_page')  # Assuming 'about' is the name of the URL pattern for the about page
        else:
            # Password doesn't match
            return render(request, 'home/alogin.html', {'error_message': 'Invalid username or password'})
    
    return render(request, 'home/alogin.html')  


from .models import Faculty_Login  


def admin_page(request): 

    # fac_objs = Faculty_Login.objects.all() 
    fac_objs = Faculty_Login.objects.filter(deleted=False)

    # Pass the queryset to the template context
    context = {
        'faculty_logins': list(fac_objs)
    }

    # Render the template with the context 
    print(context['faculty_logins'])
    return render(request,'home/admin_home_page.html',context) 





from django.shortcuts import render, redirect
from .models import Faculty_Login

def create_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            Faculty_Login.objects.create(username=username, password=password)
            return redirect('adminlogin/admin_page')  # Redirect to a success page
        else:
            return render(request, 'home/create_signup.html', {'error': 'Please provide both username and password.'})
    return render(request, 'home/create_signup.html')
    


# def faculty_detail(request):
#     # Retrieve faculty ID from session
#     faculty_id = request.session.get('faculty_id')
#     if faculty_id is None:
#         # Redirect or handle the case where no faculty ID is found in the session
#         pass

#     # Fetch faculty details by ID 
    
#     faculty = get_object_or_404(Faculty_Login, username=faculty_id)  
#     print(faculty)
    
#     return render(request, 'home/faculty_detail.html', {'faculty': faculty})

def set_faculty_session(request, faculty_id):
    # Store faculty ID in session
    request.session['faculty_id'] = faculty_id  
    faculty = get_object_or_404(Faculty_Login, username=faculty_id)  
    return render(request, 'home/faculty_info_page.html', {'faculty': faculty})  


from django.utils import timezone



def delete_faculty(request,faculty_id): 
    faculty = get_object_or_404(Faculty_Login, username=faculty_id) 
    faculty.deleted=True   
    p_details=get_object_or_404(ProfessionalDetail, user=faculty_id)  
    current_date = timezone.now().date() 
    p_details.leaving_date=current_date
    faculty.save()  # Save the changes to the faculty instance 
    p_details.save()
    return redirect('ad_page') 
    


def archive_data_view(request): 
    # archive_data=Archive.objects.all() 
    # print(archive_data) 

    fac_objs = Faculty_Login.objects.filter(deleted=True)

    # Pass the queryset to the template context
    context = {
        'faculty_logins': list(fac_objs)
    }

    return render(request, 'home/archive_data.html',context)



from django.contrib import messages


def admin_personal(request,faculty_id): 
    # username = request.session.get('username')  
    faculty = get_object_or_404(Faculty_Login, username=faculty_id) 
    context={'faculty':faculty}  
    if request.method=='POST': 
        digital_id = request.POST.get('digital_id')
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        dob = request.POST.get('dob')
        cno = request.POST.get('contact_number')
        acno = request.POST.get('alternate_contact_number')
        address = request.POST.get('address')
        email_id = request.POST.get('email')
        alt_email_id = request.POST.get('alternate_email')
        aicte_id = request.POST.get('aicte_id')
        anna_id = request.POST.get('anna_univ_faculty_id')
        blood_grp = request.POST.get('blood_group')  

        faculty.personaldetail.digital_id = digital_id
        faculty.personaldetail.first_name = fname
        faculty.personaldetail.last_name = lname
        faculty.personaldetail.dob = dob
        faculty.personaldetail.contact_no = cno
        faculty.personaldetail.alternate_contact_no = acno
        faculty.personaldetail.address = address
        faculty.personaldetail.email_id = email_id
        faculty.personaldetail.alternate_email_id = alt_email_id
        faculty.personaldetail.aicte_id = aicte_id
        faculty.personaldetail.anna_univ_faculty_id = anna_id
        faculty.personaldetail.blood_grp = blood_grp

        # Save the changes to the database
        faculty.personaldetail.save() 

     

# Redirect to the admin_personal view with the faculty_id parameter
        return redirect('set_faculty_session', faculty_id=faculty.username)

    
    return render(request,'home/personal.html',context) 


        














def admin_academic(request,faculty_id):  
    faculty = get_object_or_404(Faculty_Login, username=faculty_id)   
    academic = AcademicPerformance.objects.filter(user=faculty) 
    context={'academic':academic,'faculty':faculty}
    return render(request,'home/academic_performance.html',context)

    
def admin_professional(request,faculty_id):
    faculty = get_object_or_404(Faculty_Login, username=faculty_id)  
    # pro_details = ProfessionalDetail.objects.filter(user=faculty) 
    context={'faculty':faculty}
    return render(request,'home/professional_details.html',context)

def admin_awards(request,faculty_id):
    faculty = get_object_or_404(Faculty_Login, username=faculty_id)   
    awards = Award.objects.filter(user=faculty) 
    print(awards)
    context={'awards':awards,'faculty':faculty} 
    return render(request,'home/awards.html',context)

def admin_profexp(request,faculty_id):
    faculty = get_object_or_404(Faculty_Login, username=faculty_id)  
    prof_exp = Professionalexp.objects.filter(user=faculty) 
    context={'faculty':faculty,'prof_exp':prof_exp}
    return render(request,'home/professional_experience.html',context)

def admin_coursestaught(request,faculty_id):
    faculty = get_object_or_404(Faculty_Login, username=faculty_id)   
    c_taughts = CoursesTaught.objects.filter(user=faculty)  
    print(c_taughts)
    context={'c_taughts':c_taughts,'faculty':faculty}
    return render(request,'home/courses_taught.html',context)


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


    








# Create your views here.
