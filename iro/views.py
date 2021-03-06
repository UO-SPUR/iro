from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from iro.forms import *
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from iro.choices import *
# from weasyprint import HTML, CSS
from django.template.loader import get_template
from django.template import RequestContext
from iro.choices import *
from iro.forms import ApplicantForm

# Handle uploaded files
def handle_transcripts(file):
    with open('', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


# Create your views here.

def get_application(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ApplicantForm(request.POST, request.FILES, prefix="app")
        form2 = ReferenceLetterRequestForm(request.POST, prefix="ref1")
        form3 = ReferenceLetterRequestForm(request.POST, prefix="ref2")
        form4 = ReferenceLetterRequestForm(request.POST, prefix="ref3")

        application_is_valid = form.is_valid()
        ref_letter_1_is_valid = form2.is_valid()
        ref_letter_2_is_valid = form3.is_valid()
        ref_letter_3_is_valid = form4.is_valid()

        # check whether it's valid:
        if application_is_valid and ref_letter_1_is_valid and ref_letter_2_is_valid and ref_letter_3_is_valid:
            # process the data in form.cleaned_data as required
            # ...
            applicant = form.save()
            ref_letter_1 = form2.save(commit=False)
            ref_letter_2 = form3.save(commit=False)
            ref_letter_3 = form4.save(commit=False)

            # Set the Applicant to the save Application
            ref_letter_1.applicant = applicant
            ref_letter_2.applicant = applicant
            ref_letter_3.applicant = applicant

            # Save the ReferenceLetter
            ref_letter_1.save()
            ref_letter_2.save()
            ref_letter_3.save()

            # redirect to a new URL:
            return HttpResponseRedirect('/iro/thanks/?uuid=' + str(applicant.uuid))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ApplicantForm(prefix="app")
        form2 = ReferenceLetterRequestForm(prefix="ref1")
        form3 = ReferenceLetterRequestForm(prefix="ref2")
        form4 = ReferenceLetterRequestForm(prefix="ref3")

    return render(request, 'application.html', {'input_form': form, 'ref_letter_1': form2, 'ref_letter_2': form3,
                                                'ref_letter_3': form4})


def get_reference(request):
    # GET the uuid of the ReferenceLetter
    uuid = request.GET['uuid']
    reference_letter = ReferenceLetter.objects.get(uuid=uuid)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ReferenceLetterForm(request.POST, request.FILES, instance=reference_letter)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/iro/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ReferenceLetterForm(instance=reference_letter)

    return render(request, 'form-only.html', {'input_form': form})


def thanks(request):
    uuid = request.GET['uuid']
    applicant = Applicant.objects.get(uuid=uuid)
    exclude = ApplicantForm.Meta.exclude

    html_template = get_template('thanks.html')

    rendered_html = html_template.render(RequestContext(request, {'application': applicant, 'excluded_fields': exclude})).encode(encoding="UTF-8")
    http_response = HttpResponse(rendered_html)

    # Redirection page to say sign up was successful
    return http_response


# Views that are restricted based on group user is in

# Tests for the different groups

# Checks Intern:
def is_intern(function=None):
    """Use this decorator to restrict access to
    authenticated users who are in the "Intern" group."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.groups.filter(name=INTERN_GROUP_NAME).exists()
    )
    return actual_decorator(function)


def is_mentor(function=None):
    """Use this decorator to restrict access to
    authenticated users who are in the "Mentor" group."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.groups.filter(name=MENTOR_GROUP_NAME).exists()
    )
    return actual_decorator(function)


def is_faculty(function=None):
    """Use this decorator to restrict access to
    authenticated users who are in the "Faculty" group."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.groups.filter(name=FACULTY_GROUP_NAME).exists()
    )
    return actual_decorator(function)


def is_faculty_mentor(function=None):
    """Use this decorator to restrict access to
    authenticated users who are in the "Faculty" group."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and (
            u.groups.filter(name=FACULTY_GROUP_NAME).exists() or u.groups.filter(name=MENTOR_GROUP_NAME).exists())
    )
    return actual_decorator(function)


# Checks for User is part of Intern

@is_intern
def intern_survey(request):
    return render(request, 'form-only.html')


@is_intern
def progress_report_add(request):
    current_intern = request.user.intern
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProgressReportForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/iro/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProgressReportForm()

    return render(request, 'form-only.html', {'input_form': form})


@is_intern
def intern_abstract_edit(request):
    current_intern = request.user.intern
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AbstractForm(request.POST, instance=current_intern.abstract)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/iro/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AbstractForm(instance=current_intern.abstract)

    return render(request, 'form-only.html', {'input_form': form})


@is_intern
def intern_overview(request):
    current_intern = request.user.intern
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InternOverviewForm(request.POST, instance=current_intern)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            form.save()
            # redirect to a new URL:
            return render(request, 'intern-overview.html', {'input_form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InternOverviewForm(instance=current_intern)

    return render(request, 'intern-overview.html', {'input_form': form})


@is_intern
def intern_survey(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InternSurveyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/iro/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InternSurveyForm()

    return render(request, 'form-only.html', {'input_form': form})


# Checks for User is part of Mentor

@is_mentor
def mentor_overview(request):
    current_mentor = request.user.mentor
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = MentorForm(request.POST, instance=current_mentor)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            form.save()
            # redirect to a new URL:
            return render(request, 'mentor-overview.html', {'input_form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MentorForm(instance=current_mentor)

    return render(request, 'mentor-overview.html', {'input_form': form})


@is_mentor
def mentor_survey(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = MentorSurveyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/iro/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MentorSurveyForm()

    return render(request, 'form-only.html', {'input_form': form})


# Checks for User is part of Faculty

@is_faculty
def faculty_survey(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PISurveyForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/iro/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PISurveyForm()

    return render(request, 'form-only.html', {'input_form': form})


@is_faculty
def faculty_overview(request):
    current_faculty = request.user.faculty
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FacultyOverviewForm(request.POST, instance=current_faculty)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            form.save()
            # redirect to a new URL:
            return render(request, 'faculty-overview.html', {'input_form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = FacultyOverviewForm(instance=current_faculty)

    return render(request, 'faculty-overview.html', {'input_form': form})


@is_faculty
def faculty_application_overview(request):
    current_faculty = request.user.faculty
    assigned_applications = current_faculty.applicant_set.all()
    feedback = current_faculty.feedback_faculty_set.all()
    return render(request, 'faculty_overview.html', {
        'application_list': assigned_applications,
        'feedback_list': feedback
    })


'''
@is_faculty
def faculty_application_pdfs(request, applicant):
    # Get information from applicant
    filename = applicant.applicant_name + '.pdf'

    html_template = get_template('templates/applicant-pdf.html')

    rendered_html = html_template.render(RequestContext(request, {'application': applicant})).encode(encoding="UTF-8")

    pdf_file = HTML(string=rendered_html).write_pdf()

    http_response = HttpResponse(pdf_file, content_type='application/pdf')
    http_response['Content-Disposition'] = 'filename=' + filename

    return http_response
'''


# Faculty and Mentor views

# Non-PDF Applicant Info
@is_faculty_mentor
def application_view_html(request):
    uuid = request.GET['uuid']
    applicant = Applicant.objects.get(uuid=uuid)

    html_template = get_template('templates/applicant-pdf.html')

    rendered_html = html_template.render(RequestContext(request, {'application': applicant})).encode(encoding="UTF-8")
    http_response = HttpResponse(rendered_html)

    return http_response


# Admin Views

@permission_required('is_superuser')
def admin_reference_letter_view(request):
    uuid = request.GET['uuid']
    applicant = Applicant.objects.get(uuid=uuid)
    reference_letters = applicant.referenceletter_set.all()

    html_template = get_template('templates/admin-reference-letters.html')

    rendered_html = html_template.render(RequestContext(request, {'application': applicant,
                                                                  'letters_of_reference': reference_letters})).encode(
        encoding="UTF-8")
    http_response = HttpResponse(rendered_html)

    return http_response
