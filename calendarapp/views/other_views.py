# cal/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
import calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from calendarapp.models import EventMember, Event
from myadmin.models import ClientRecord, ClientRole, CourtType, Case, Invoice, CaseAttachment
from myadmin.forms import AddClientForm, AddClientRole, AddCourtType, CaseForm
from calendarapp.utils import Calendar
from calendarapp.forms import EventForm, AddMemberForm
from django.views.decorators.csrf import csrf_exempt

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


class CalendarView(LoginRequiredMixin, generic.ListView):
    login_url = "signin"
    model = Event
    template_name = "calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        return context


#@login_required(login_url="signup")
# def create_event(request):

#     if request.POST:
#         return HttpResponseRedirect(reverse("calendar"))
#     return render(request, "event.html", {})

@login_required(login_url="signup")
def create_event(request):
    form = EventForm(request.POST or None)
    if request.POST and form.is_valid():
        title = form.cleaned_data["title"]
        description = form.cleaned_data["description"]
        start_time = form.cleaned_data["start_time"]
        end_time = form.cleaned_data["end_time"]
        Event.objects.get_or_create(
            user=request.user,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
        )
        return HttpResponseRedirect(reverse("calendar"))
    return render(request, "event.html", {"form": form})


class EventEdit(generic.UpdateView):
    model = Event
    fields = ["title", "description", "start_time", "end_time"]
    template_name = "event.html"


@login_required(login_url="signup")
def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    eventmember = EventMember.objects.filter(event=event)
    context = {"event": event, "eventmember": eventmember}
    return render(request, "event-details.html", context)


def add_eventmember(request, event_id):
    forms = AddMemberForm()
    if request.method == "POST":
        forms = AddMemberForm(request.POST)
        if forms.is_valid():
            member = EventMember.objects.filter(event=event_id)
            event = Event.objects.get(id=event_id)
            if member.count() <= 9:
                user = forms.cleaned_data["user"]
                EventMember.objects.create(event=event, user=user)
                return redirect("calendar")
            else:
                print("--------------User limit exceed!-----------------")
    context = {"form": forms}
    return render(request, "add_member.html", context)


class EventMemberDeleteView(generic.DeleteView):
    model = EventMember
    template_name = "event_delete.html"
    success_url = reverse_lazy("calendar")

# class CalendarViewNew(LoginRequiredMixin, generic.View):
#     login_url = "signin"
#     template_name = "calendarapp/calendar.html"
#     form_class = EventForm

#     def get(self, request, *args, **kwargs):
#         forms = self.form_class()
#         events = Event.objects.get_all_events(user=request.user)
#         events_month = Event.objects.get_running_events(user=request.user)
#         #"case_id":event.case_id,
#         event_list = []
#         # start: '2020-09-16T16:00:00'
#         for event in events:
#             event_list.append(
#                 {   "id": event.id,
#                     "title": event.title,

#                     "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
#                     "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
#                     "description": event.description,
#                 }
#             )

#         context = {"form": forms, "events": event_list,
#                   "events_month": events_month}
#         return render(request, self.template_name, context)

#     def post(self, request, *args, **kwargs):
#         # Need to work - Mani
#         forms = self.form_class(request.POST)
#         if forms.is_valid():
#             form = forms.save(commit=False)
#             form.user = request.user
#             form.save()
#             return redirect("calendar")
#         context = {"form": forms}
#         return render(request, self.template_name, context)



def CalendarViewNew(request):
    event_obj = []
    client_obj = []
    client_role_obj = []
    court_type_obj = []
    case_obj = []
    case_attachment = ""

    if request.method == "POST":
        # Event details
        title = request.POST.get("title")
        description = request.POST.get("description")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        event_obj = Event(user=request.user,
                            title=title,
                            description=description,
                            start_time=start_time,
                            end_time=end_time)
        event_obj.save()

        # Client Details
        full_name =  request.POST.get("full_name")
        alien_number =  request.POST.get("alien_number")
        identity =  request.POST.get("client_identity")
        gender =  request.POST.get("client_gender")
        phone_number =  request.POST.get("client_phone_number")
        email =  request.POST.get("client_email")
        address1 =  request.POST.get("client_address1")
        address2 =  request.POST.get("client_address2")
        city =  request.POST.get("client_city")
        postcode =  request.POST.get("client_postcode")
        state =  request.POST.get("client_state")
        country =  request.POST.get("client_country")
        remark =  request.POST.get("client_remark")
        agent_fullname =  request.POST.get("agent_fullname")
        agent_ph =  request.POST.get("agent_ph")
        agent_identity =  request.POST.get("agent_identity")
        latitude =  request.POST.get("agent_latitude")
        longitude =  request.POST.get("agent_longitude")

        client_obj = ClientRecord(full_name=full_name,
                                    alien_number=alien_number,
                                    identity=identity,
                                    gender=gender,
                                    phone_number=phone_number,
                                    email=email,
                                    address1=address1,
                                    address2=address2,
                                    city=city,
                                    postcode=postcode,
                                    state=state,
                                    country=country,
                                    remark=remark,
                                    agent_fullname=agent_fullname,
                                    agent_ph=agent_ph,
                                    agent_identity=agent_identity,
                                    latitude=latitude,
                                    longitude=longitude,
                                    event=event_obj)
        client_obj.save()

        # Client Role Details
        created_at = request.POST.get("client_role_created_at")
        client_role = request.POST.get("client_role")
        client_role_description = request.POST.get("client_role_description")

        client_role_obj = ClientRole(created_at=created_at,client_role=client_role,client_role_description=client_role_description)
        client_role_obj.save()

        # court Type Details
        created_at = request.POST.get("court_created_at")
        court_type = request.POST.get("court_type")
        court_description = request.POST.get("court_description")
        i_589_filed = request.POST.get("i_589_filed")
        # erop = models.request.POST.get("erop")
        e_28_filed = request.POST.get("e_28_filed")
        biometrics_filed = request.POST.get("biometrics_filed")
        foia_submitted = request.POST.get("foia_submitted")
        foia_uploaded = request.POST.get("foia_uploaded")
        work_permit_applied = request.POST.get("work_permit_applied")
        hearing_date =request.POST.get("hearing_date")
        hearing_location = request.POST.get("hearing_location")

        court_type_obj = CourtType(created_at=created_at,
                                    court_type=court_type,
                                    court_description=court_description,
                                    i_589_filed=i_589_filed,
                                    # erop=erop,
                                    e_28_filed=e_28_filed,
                                    biometrics_filed=biometrics_filed,
                                    foia_submitted=foia_submitted,
                                    foia_uploaded=foia_uploaded,
                                    work_permit_applied=work_permit_applied,
                                    hearing_date=hearing_date,
                                    hearing_location=hearing_location,
                                    event=event_obj)

        court_type_obj.save()


        # Case Details
        ref_no = request.POST.get("ref_no")
        respondent_name = request.POST.get("respondent_name")
        respondent_advocate = request.POST.get("respondent_advocate")
        case_type = request.POST.get("case_type")
        case_description = request.POST.get("case_description")
        sense_of_urgent = request.POST.get("sense_of_urgent")
        court_no = request.POST.get("court_no")
        # court_type = request.POST.get("court_type")
        judge_name = request.POST.get("judge_name")
        court_remark = request.POST.get("court_remark")

        case_obj =  Case(ref_no = ref_no,
                        respondent_name = respondent_name,
                        client_role=client_role_obj,
                        clients=client_obj,
                        respondent_advocate = respondent_advocate,
                        case_type = case_type,
                        case_description = case_description,
                        sense_of_urgent = sense_of_urgent,
                        court_type = court_type_obj,
                        judge_name = judge_name,
                        court_remark = court_remark)
        case_obj.save()

        # Handling attachments

        for file_att in request.FILES.getlist('attachment'):
            print("attachment_file12======",file_att)

            case_attachment = CaseAttachment(upload=file_att, case_att_id=case_obj)
            case_attachment.save()

    all_events = Event.objects.all()
    out = []
    context = {}
    for event in all_events:

        out.append({
                    "id": event.id,
                    "title": event.title,
                    "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "description": event.description,

        })
    '''
    Description:
    Alien Number:
    Identity:
    Ref No:
    Respondent Name:
    '''
    context["events"] = out
    # context["Description"] =
    # context["Alien Number"] =
    # context["Identity"] =
    # context["Ref No"] =
    # context["Respondent Name"] =


    return render(request, 'calendarapp/calendar.html', context)


def get_event_details(request, event_id):

    try:
        event = Event.objects.get(pk=event_id)

        client_ob = ClientRecord.objects.get(event__id=event.id)
        case_ob = Case.objects.get(clients__id=client_ob.id)

        data = {

                'description': event.description,
                'alien_number':client_ob.alien_number,
                'identity':client_ob.identity,
                'ref_no':case_ob.ref_no,
                'event_id':event.id


        }
        return JsonResponse(data)
    except Exception:
        pass


def get_client_record_details(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
        client_ob = ClientRecord.objects.get(event__id=event.id)
        case_ob = Case.objects.get(clients__id=client_ob.id)

        data = {

            'description': event.description,
            'alien_number': client_ob.alien_number,
            'full_name': client_ob.full_name,
            'identity': client_ob.identity,
            'gender': client_ob.gender,
            'phone_number': client_ob.phone_number,
            'email': client_ob.email,
            'address1': client_ob.address1,
            'address2': client_ob.address2,
            'city': client_ob.city,
            'postcode': client_ob.postcode,
            'state': client_ob.state,
            'country': client_ob.country,
            'remark': client_ob.remark,

            'agent_fullname': client_ob.agent_fullname,
            'agent_ph': client_ob.agent_ph,
            'agent_identity': client_ob.agent_identity,
            'agent_latitude': client_ob.latitude,
            'agent_longitude': client_ob.longitude,
            # 'client_role_created_at': client_ob.created_at,
            # 'client_role': client_ob.client_role,
            # 'client_role_description': client_ob.client_role_description,
            # 'ref_no': case_ob.ref_no,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_case_details(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
        client_ob = ClientRecord.objects.get(event__id=event.id)
        court_type_ob = CourtType.objects.get(event__id=event.id)
        case_ob = Case.objects.get(clients__id=client_ob.id)

        data = {
            "court_created_at": event.created_at,
            "court_type": court_type_ob.court_type,
            "court_description": court_type_ob.court_description,
            "i_589_filed": court_type_ob.i_589_filed,
            "e_28_filed": court_type_ob.e_28_filed,
            "biometrics_filed": court_type_ob.biometrics_filed,
            "foia_submitted": court_type_ob.foia_submitted,
            "foia_uploaded": court_type_ob.foia_uploaded,
            "work_permit_applied": court_type_ob.work_permit_applied,
            "hearing_date": court_type_ob.hearing_date,
            "hearing_location": court_type_ob.hearing_location,
            "ref_no": case_ob.ref_no,
            "respondent_name": case_ob.respondent_name,
            "respondent_advocate": case_ob.respondent_advocate,
            "case_type": case_ob.case_type,
            "case_description": case_ob.case_description,
            "sense_of_urgent": case_ob.sense_of_urgent,
            "court_no": case_ob.court_no,
            "judge_name": case_ob.judge_name,
            "court_remark": case_ob.court_remark,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def update_client_record(request, event_id):
    if request.method == 'POST':
        try:
            event = Event.objects.get(pk=event_id)
            client_ob = ClientRecord.objects.get(event__id=event.id)
            case_ob = Case.objects.get(clients__id=client_ob.id)

            # Update client record with new data
            client_ob.alien_number = request.POST.get('alien_number')
            client_ob.full_name = request.POST.get('full_name')
            client_ob.identity = request.POST.get('identity')
            client_ob.gender = request.POST.get('gender')
            client_ob.phone_number = request.POST.get('phone_number')
            client_ob.email = request.POST.get('email')
            client_ob.address1 = request.POST.get('address1')
            client_ob.address2 = request.POST.get('address2')
            client_ob.city = request.POST.get('city')
            client_ob.postcode = request.POST.get('postcode')
            client_ob.state = request.POST.get('state')
            client_ob.country = request.POST.get('country')
            client_ob.remark = request.POST.get('remark')
            client_ob.agent_fullname = request.POST.get('agent_fullname')
            client_ob.agent_ph = request.POST.get('agent_ph')
            client_ob.agent_identity = request.POST.get('agent_identity')
            client_ob.agent_latitude = request.POST.get('agent_latitude')
            client_ob.agent_longitude = request.POST.get('agent_longitude')
            # client_ob.client_role_created_at = request.POST.get('client_role_created_at')
            # client_ob.client_role = request.POST.get('client_role')
            # client_ob.client_role_description = request.POST.get('client_role_description')
            client_ob.save()

            # Update case record with new data
            # case_ob.ref_no = request.POST.get('ref_no')
            # case_ob.save()

            return JsonResponse({'message': 'Client record updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



@csrf_exempt
def update_case_details(request, event_id):
    if request.method == 'POST':
        try:
            event = Event.objects.get(pk=event_id)
            client_ob = ClientRecord.objects.get(event__id=event.id)
            court_type_ob = CourtType.objects.get(event__id=event.id)
            case_ob = Case.objects.get(clients__id=client_ob.id)

            # Update court type
            court_type_ob.type = request.POST.get('court_type')
            court_type_ob.description = request.POST.get('court_description')
            court_type_ob.save()

            # Update case
            case_ob.i_589_filed = request.POST.get('i_589_filed')
            case_ob.e_28_filed = request.POST.get('e_28_filed')
            case_ob.biometrics_filed = request.POST.get('biometrics_filed')
            case_ob.foia_submitted = request.POST.get('foia_submitted')
            case_ob.foia_uploaded = request.POST.get('foia_uploaded')
            case_ob.work_permit_applied = request.POST.get('work_permit_applied')
            # case_ob.hearing_date = request.POST.get('hearing_date'e)
            case_ob.hearing_location = request.POST.get('hearing_location')
            # case_ob.ref_no = request.POST.get('ref_no')
            case_ob.respondent_name = request.POST.get('respondent_name')
            case_ob.respondent_advocate = request.POST.get('respondent_advocate')
            case_ob.case_type = request.POST.get('case_type')
            case_ob.case_description = request.POST.get('case_description')
            case_ob.sense_of_urgent = request.POST.get('sense_of_urgent')
            case_ob.judge_name = request.POST.get('judge_name')
            case_ob.court_remark = request.POST.get('court_remark')
            case_ob.save()

            return JsonResponse({'message': 'Case details updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)





# def get_event_details(request, event_id):
#     try:
#         event = Event.objects.get(pk=event_id)
#         client_record = ClientRecord.objects.get(event=event)
#         case = Case.objects.get(event=event)


#         data = {
#             'event': {
#                 'id': event.id,
#                 'title': event.title,
#                 'description': event.description,
#                 'start_time': event.start_time.strftime('%Y-%m-%dT%H:%M:%S'),
#                 'end_time': event.end_time.strftime('%Y-%m-%dT%H:%M:%S'),

#             },
#             'client_record': {
#                 'full_name': client_record.full_name,
#                 'alien_number': client_record.alien_number,
#                 'identity': client_record.identity,

#             },
#             'case': {
#                 'ref_no': case.ref_no,
#                 'respondent_name': case.respondent_name,
#                 'respondent_advocate': case.respondent_advocate,

#             }
#         }
#         return JsonResponse(data)
#     except (Event.DoesNotExist, ClientRecord.DoesNotExist, Case.DoesNotExist):
#         return JsonResponse({'error': 'Data not found'}, status=404)



def all_events(request):
    all_events = Event.objects.all()
    out = []
    for event in all_events:
        out.append({
            'title': event.title,
            'id': event.id,
            "description": event.description,
            'start_time': event.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
            'end_time': event.end_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })

    return JsonResponse(out, safe=False)





class CalendarViewNewsLatest(LoginRequiredMixin, generic.View):
    login_url = "signin"
    template_name = "calendarapp/calendar.html"
    event_form_class = EventForm
    # client_record_form_class = AddClientForm
    # case_form_class = CaseForm


    def get(self, request, *args, **kwargs):
        forms = self.event_form_class()
        events = Event.objects.get_all_events(user=request.user)
        events_month = Event.objects.get_running_events(user=request.user)
        #"case_id":event.case_id,
        event_list = []
        # start: '2020-09-16T16:00:00'
        for event in events:
            event_list.append(
                {   "id": event.id,
                    "title": event.title,

                    "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "description": event.description,
                }
            )

        context = {"form": forms, "events": event_list,
                  "events_month": events_month}
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        print("Test=====",self)
        event_data = {
            "title": request.POST.get("title"),
            "description":request.POST.get("description"),
            "start_time":request.POST.get("start_time"),
            "end_time":request.POST.get("end_time"),
        }
        client_record_data = {
            "full_name": request.POST.get("full_name"),
            "alien_number": request.POST.get("alien_number"),
            "identity": request.POST.get("client_identity"),
            "gender": request.POST.get("client_gender"),
            "phone_number": request.POST.get("client_phone_number"),
            "email": request.POST.get("client_email"),
            "address1": request.POST.get("client_address1"),
            "address2": request.POST.get("client_address2"),
            "city": request.POST.get("client_city"),
            "postcode": request.POST.get("client_postcode"),
            "state": request.POST.get("client_state"),
            "country": request.POST.get("client_country"),
            "remark": request.POST.get("client_remark"),
            "agent_fullname": request.POST.get("agent_fullname"),
            "agent_ph": request.POST.get("agent_ph"),
            "agent_identity": request.POST.get("agent_identity"),
        }
        case_data = {
            "ref_no": request.POST.get("ref_no"),
            "respondent_name": request.POST.get("respondent_name"),
            "respondent_advocate": request.POST.get("respondent_advocate"),
            "case_type": request.POST.get("case_type"),
            "case_description": request.POST.get("case_description"),
            "sense_of_urgent": request.POST.get("sense_of_urgent"),
            "court_no": request.POST.get("court_no"),
            "court_type": request.POST.get("court_type"),
            "judge_name": request.POST.get("judge_name"),
            "court_remark": request.POST.get("court_remark"),
        }



        event_form = self.event_form_class(event_data)
        client_record_form = self.client_record_form_class(client_record_data)
        case_form = self.case_form_class(case_data)

        if all([event_form.is_valid(), client_record_form.is_valid(), case_form.is_valid()]):
            event = event_form.save(commit=False)
            event.user = request.user
            event.save()

            client_record = client_record_form.save(commit=False)
            client_record.created_by = request.user
            client_record.save()

            case = case_form.save(commit=False)
            case.clients = client_record
            case.save()

            return redirect("calendar")

        context = {
            "event_form": event_form,
            "client_record_form": client_record_form,
            "case_form": case_form,
        }
        return render(request, self.template_name, context)



def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        return JsonResponse({'message': 'Event sucess delete.'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)

def next_week(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.id = None
        next.start_time += timedelta(days=7)
        next.end_time += timedelta(days=7)
        next.save()
        return JsonResponse({'message': 'Sucess!'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)

def next_day(request, event_id):

    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.id = None
        next.start_time += timedelta(days=1)
        next.end_time += timedelta(days=1)
        next.save()
        return JsonResponse({'message': 'Sucess!'})
    else:
        return JsonResponse({'message': 'Error!'}, status=400)
