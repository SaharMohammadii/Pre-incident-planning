from django.urls import path
from .views import (FireStationManagementView, 
                    AccountUserByManagementView, 
                    InspectionManagementView, 
                    InspectionStaffView,
                    ConstantsView,
                    LocationView)

urlpatterns = [
    path('fire-station-info/', FireStationManagementView.as_view()),
    path('modify-fire-station-info/', FireStationManagementView.as_view()),
    path('add-member/', FireStationManagementView.as_view()),
    path('staff-info/<int:pk>/', AccountUserByManagementView.as_view()),
    path('create-staff/', AccountUserByManagementView.as_view()),
    path('modify-staff-status/', AccountUserByManagementView.as_view()),
    path('inspections/', InspectionManagementView.as_view()),
    path('inspections/<int:pk>', InspectionManagementView.as_view()),
    path('create-inspection/', InspectionManagementView.as_view()),
    path('review-inspection/<int:pk>/', InspectionManagementView.as_view()),
    path('staff-inspection/', InspectionStaffView.as_view()),
    path('modify-inspection/', InspectionStaffView.as_view()),
    path('create-location/', LocationView.as_view()),
    


    path('report-info', ConstantsView.as_view())

    
]
