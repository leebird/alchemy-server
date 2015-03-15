from alchemy_server.forms import SearchPubMedForm
from .base_view import BaseView

class ContactView(BaseView):
    # contact page
    template_name = BaseView.app_name + '/contact.html'
    form_class = SearchPubMedForm

    def get(self, request):
        self.request = request
        return super(ContactView, self).get(request)

    def get_context_data(self,**kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['top_form'] = True
        context['request'] = self.request
        return context