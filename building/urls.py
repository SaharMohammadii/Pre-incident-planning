from django.urls import path, include
from .views import (BuildingView, BuildingViewPublic, 
                    ImageUploaderView, ConstantsView, 
                    BuildingSearchByLocationView)

urlpatterns = [
    path('create-building/', BuildingView.as_view()),
    path('update-building/<int:pk>', BuildingView.as_view()),
    path('buildings/', BuildingViewPublic.as_view()),
    path('buildings/<int:pk>', BuildingViewPublic.as_view()),
    path('upload-image/', ImageUploaderView.as_view()),
    path('constants/', ConstantsView.as_view()),
    path('building-search', BuildingSearchByLocationView.as_view()),

]
