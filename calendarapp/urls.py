from django.urls import path

from . import views


# app_name = "calendarapp"


urlpatterns = [
    # path("", views.CalendarViewNew.as_view(), name="calendar"),
    path("", views.CalendarViewNew, name="calendar"),
    path("calenders/", views.CalendarView.as_view(), name="calendars"),
    path('all_events/', views.all_events, name='all_events'),

    path('get_event_details/<int:event_id>/', views.get_event_details, name='get_event_details'),

    path('get_client_record_details/<int:event_id>/', views.get_client_record_details, name='get_client_record_details'),

    path('update_client_record/<int:event_id>/', views.update_client_record, name='update_client_record'),

    path('get_case_details/<int:event_id>/', views.get_case_details, name='get_case_details'),
    path('update_case_details/<int:event_id>/', views.update_case_details, name='update_case_details'),


    path('get_payment_details/<int:event_id>/', views.get_payment_details, name='get_payment_details'),
    path('update_payment_details/<int:event_id>/', views.update_payment_details, name='update_payment_details'),

    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('next_week/<int:event_id>/', views.next_week, name='next_week'),
    path('next_day/<int:event_id>/', views.next_day, name='next_day'),
    path("event/new/", views.create_event, name="event_new"),
    path("event/edit/<int:pk>/", views.EventEdit.as_view(), name="event_edit"),
    path("event/<int:event_id>/details/", views.event_details, name="event-detail"),
    path(
        "add_eventmember/<int:event_id>", views.add_eventmember, name="add_eventmember"
    ),
    path(
        "event/<int:pk>/remove",
        views.EventMemberDeleteView.as_view(),
        name="remove_event",
    ),
    path("all-event-list/", views.AllEventsListView.as_view(), name="all_events"),
    path(
        "running-event-list/",
        views.RunningEventsListView.as_view(),
        name="running_events",
    ),
]
