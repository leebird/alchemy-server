from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from alchemy_server.forms import SearchPubMedForm
from .base_view import BaseView

class IndexView(BaseView):
    # index page
    template_name = BaseView.app_name + '/index.html'
    form_class = SearchPubMedForm

    def form_valid(self, form):
        query = form.cleaned_data['query']
        return redirect(SearchView.view_name,query)

    def form_invalid(self, form):
        return redirect("index")

    def get(self, request):
        self.request = request
        return super(IndexView, self).get(request)

    def get_context_data(self,**kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['top_form'] = False
        context['request'] = self.request
        context['post_url'] = reverse('handle_search')
        return context