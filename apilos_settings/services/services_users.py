from abc import ABC, abstractmethod
from io import BytesIO

from django.contrib import messages
from django.http import HttpRequest

from conventions.forms import UploadForm
from conventions.services.upload_objects import BailleurListingProcessor
from conventions.services.utils import ReturnStatus
from users.forms import UserBailleurFormSet
from users.services import UserService


class BaseService(ABC):

    def __init__(self, request: HttpRequest):
        self.request: HttpRequest = request

    @abstractmethod
    def get(self) -> ReturnStatus:
        pass

    @abstractmethod
    def save(self) -> ReturnStatus:
        pass


class ImportBailleurUsersService(BaseService):
    def __init__(self, request: HttpRequest):
        super().__init__(request)

        self.upload_form = UploadForm()
        self.formset = UserBailleurFormSet()

    def get(self) -> ReturnStatus:
        return ReturnStatus.SUCCESS

    def save(self) -> ReturnStatus:
        if self.request.POST.get("Upload", False):
            return self._process_upload()
        else:
            return self._process_formset()

    def _process_upload(self) -> ReturnStatus:
        self.upload_form = UploadForm(self.request.POST, self.request.FILES)
        if self.upload_form.is_valid():
            processor = BailleurListingProcessor(filename=BytesIO(self.request.FILES['file'].read()))
            users = processor.process()
            self.formset = UserBailleurFormSet(self._build_formset_data(users))
            return ReturnStatus.SUCCESS

        return ReturnStatus.ERROR

    def _process_formset(self) -> ReturnStatus:
        self.formset = UserBailleurFormSet(self.request.POST)
        if self.formset.is_valid():
            for form_user_bailleur in self.formset:
                UserService.create_user_bailleur(
                    form_user_bailleur.cleaned_data['first_name'],
                    form_user_bailleur.cleaned_data['last_name'],
                    form_user_bailleur.cleaned_data['email'],
                    form_user_bailleur.cleaned_data['bailleur']
                )
            # TODO plan a welcome email
            messages.success(
                self.request,
                f"{len(self.formset)} utilisateurs bailleurs ont été correctement créés à partir du listing",
                extra_tags="Listing importé"
            )
            return ReturnStatus.SUCCESS

        return ReturnStatus.ERROR

    def _build_formset_data(self, results) -> dict:
        data = {
            'form-TOTAL_FORMS': len(results),
            'form-INITIAL_FORMS': len(results),
        }
        for index, user in enumerate(results):
            for key, value in user.items():
                data[f'form-{index}-{key}'] = value
        return data

