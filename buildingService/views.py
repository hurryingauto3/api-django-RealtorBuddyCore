from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .utils import update_address_abbreviations
from .serializers import BuildingSerializer
from .models import Building, AddressAbbreviation
from django.db.models import Q
from .forms import BuildingForm

from logging import getLogger

logger = getLogger(__name__)


def index(request):
    return HttpResponse("Realtor Buddy - Building Service")


def updateAddressAbbreviations(request):

    abbr_dict = update_address_abbreviations()
    directions_mapping = {
        "n": ["north"],
        "s": ["south"],
        "e": ["east"],
        "w": ["west"],
        "ne": ["northeast"],
        "nw": ["northwest"],
        "se": ["southeast"],
        "sw": ["southwest"],
    }

    abbr_dict = {**abbr_dict, **directions_mapping}
    AddressAbbreviation.update_abbreviations(abbr_dict)
    return HttpResponse("Update Address Abbreviations")


class BuildingViewSet(viewsets.ModelViewSet):
    serializer_class = BuildingSerializer
    queryset = Building.objects.all()

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        type_ = self.request.query_params.get("type")
        if search is not None:
            if type_ and type_ == "elastic":
                logger.info("Searching with postgres full text search")
                vector = SearchVector(
                    "name", weight="A"
                )  # + SearchVector('address', weight='B') + SearchVector('city', weight='C') + SearchVector('state', weight='D')
                query = SearchQuery(search)
                queryset = (
                    queryset.annotate(rank=SearchRank(vector, query))
                    .filter(rank__gte=0.1)
                    .order_by("-rank")
                )

            else:
                logger.info("Searching with fuzzy search")
                queryset = queryset.filter(
                    Q(name__icontains=search)
                    | Q(address__icontains=search)
                    | Q(city__icontains=search)
                    | Q(state__icontains=search)
                )
        return queryset


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
