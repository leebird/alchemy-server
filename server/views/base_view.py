from django.views.generic.edit import FormView

class BaseView(FormView):
    # make app name visible for all child classes
    app_name = 'django_annotation'

    def get_context_data(self,**kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        context['app_name'] = self.app_name
        context['top_form'] = True
        return context