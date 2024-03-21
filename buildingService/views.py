from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from .utils import update_address_abbreviations
from .serializers import BuildingSerializer
from .models import Building, AddressAbbreviation
from .forms import BuildingForm

def index(request):
    return HttpResponse("Realtor Buddy - Building Service")


def updateAddressAbbreviations(request):

    abbr_dict = update_address_abbreviations()
    directions_mapping = {
        "n": ["north"],
        "s": ["south"],
        "e": ["east"],
        "w": ["west"],
        "ne":["northeast"],
        "nw":["northwest"],
        "se":["southeast"],
        "sw":["southwest"],
    }
    
    abbr_dict = {**abbr_dict, **directions_mapping}
    AddressAbbreviation.update_abbreviations(abbr_dict)
    return HttpResponse("Update Address Abbreviations")

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


# class BuildingListView(ListView):
#     model = Building
#     context_object_name = 'buildings'
#     template_name = 'buildingService/building_list.html'

# class BuildingDetailView(DetailView):
#     model = Building
#     context_object_name = 'building'
#     template_name = 'buildingService/building_detail.html'

# class BuildingCreateView(CreateView):
#     model = Building
#     form_class = BuildingForm
#     template_name = 'buildingService/building_form.html'

# class BuildingUpdateView(UpdateView):
#     model = Building
#     form_class = BuildingForm
#     template_name = 'buildingService/building_form.html'

# class BuildingDeleteView(DeleteView):
#     model = Building
#     success_url = reverse_lazy('building-list')
#     template_name = 'buildingService/building_confirm_delete.html'
