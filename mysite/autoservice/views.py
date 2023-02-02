from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Paslauga, Automobilis, Uzsakymas, UzsakymoEilute
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.views.generic.edit import FormMixin
from .forms import UzsakymasKomentarasForm, UserUpdateForm, ProfilisUpdateForm, UzsakymasCreateUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
# Create your views here.
def index(request):
    paslaugu_kiekis = Paslauga.objects.count()
    automobiliu_kiekis = Automobilis.objects.count()
    atliktu_uzsakymu_kiekis = Uzsakymas.objects.filter(status__exact='i').count()
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    kontekstas = {
        "paslaugu_kiekis": paslaugu_kiekis,
        "automobiliu_kiekis": automobiliu_kiekis,
        "atliktu_uzsakymu_kiekis": atliktu_uzsakymu_kiekis,
        "num_visits": num_visits,
    }
    return render(request, 'index.html', context=kontekstas)


def automobiliai(request):
    paginator = Paginator(Automobilis.objects.all(), 3)
    page_number = request.GET.get('page')
    paged_automobiliai = paginator.get_page(page_number)
    context = {
        'automobiliai': paged_automobiliai,
    }
    return render(request, 'automobiliai.html', context=context)


def automobilis(request, auto_id):
    automobilis = get_object_or_404(Automobilis, pk=auto_id)
    context = {
        'automobilis': automobilis,
    }
    return render(request, "automobilis.html", context=context)


class UzsakymasListView(generic.ListView):
    model = Uzsakymas
    paginate_by = 3
    template_name = "uzsakymai.html"
    context_object_name = "uzsakymai"


class UzsakymasDetailView(generic.DetailView, FormMixin):
    model = Uzsakymas
    template_name = "uzsakymas.html"
    context_object_name = "uzsakymas"
    form_class = UzsakymasKomentarasForm

    def get_success_url(self):   # nurodome, kur atsidursime komentaro sėkmės atveju.
        return reverse('uzsakymas', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):  # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):  # štai čia nurodome, kad knyga bus būtent ta, po kuria komentuojame, o vartotojas bus tas, kuris yra prisijungęs.
        form.instance.uzsakymas = self.object
        form.instance.vartotojas = self.request.user
        form.save()
        return super().form_valid(form)





def search(request):
    query = request.GET.get('query')
    search_results = Automobilis.objects.filter(
        Q(klientas__icontains=query) | Q(automobilio_modelis__marke__icontains=query) | Q(automobilio_modelis__modelis__icontains=query) | Q(valstybinis_nr__icontains=query) | Q(
            vin_kodas__icontains=query))
    return render(request, 'search.html', {'automobiliai': search_results, 'query': query})


class UserUzsakymasListView(generic.ListView):
    model = Uzsakymas
    paginate_by = 3
    template_name = "user_uzsakymai.html"
    context_object_name = "uzsakymai"

    def get_queryset(self):
        return Uzsakymas.objects.filter(vartotojas=self.request.user)

class UzsakymasCreateView(LoginRequiredMixin, generic.CreateView):
    model = Uzsakymas
    #fields = ['terminas', 'automobilis', "status"]
    success_url = "/autoservice/manouzsakymai/"
    template_name = 'uzsakymas_form.html'
    form_class = UzsakymasCreateUpdateForm


    def form_valid(self, form):
        form.instance.vartotojas = self.request.user
        return super().form_valid(form)

class UserUzsakymasUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Uzsakymas
    fields = ['terminas', 'automobilis', "status"]
    #success_url = "/autoservice/manouzsakymai/"
    template_name = 'uzsakymas_form.html'

    def get_success_url(self):
        return reverse ('uzsakymas', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        form.instance.vartotojas = self.request.user
        return super().form_valid(form)

    def test_func(self):
        uzsakymas = self.get_object()
        return self.request.user == uzsakymas.vartotojas

class UserUzsakymasDeleteView(LoginRequiredMixin,UserPassesTestMixin, generic.DeleteView):
    model = Uzsakymas
    fields = ['terminas', 'automobilis', "status"]
    success_url = "/autoservice/manouzsakymai/"
    template_name = 'user_uzsakymas_delete.html'
    context_object_name = 'uzsakymas'

    def test_func(self):
        uzsakymas = self.get_object()
        return self.request.user == uzsakymas.vartotojas

class UzsakymasEiluteCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = UzsakymoEilute
    fields = ['paslauga', 'kiekis']
    template_name = 'uzsakymoeilute_form.html'
    def get_success_url(self):
        return reverse ('uzsakymas', kwargs={'pk': self.kwargs['pk']})
    def form_valid(self, form):
        form.instance.uzsakymas = Uzsakymas.objects.get(pk= self.kwargs['pk'])
        form.save()
        return super().form_valid(form)

    def test_func(self):
        uzsakymas = Uzsakymas.objects.get(pk= self.kwargs['pk'])
        return self.request.user == uzsakymas.vartotojas


class UzsakymasEiluteUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = UzsakymoEilute
    fields = ['paslauga', 'kiekis']
    template_name = 'uzsakymoeilute_form.html'

    def form_valid(self, form):
        form.instance.uzsakymas = Uzsakymas.objects.get(pk= self.kwargs['uzsakymas_pk'])
        form.save()
        return super().form_valid(form)

    def test_func(self):
        uzsakymas = Uzsakymas.objects.get(pk=self.kwargs['uzsakymas_pk'])
        return self.request.user == uzsakymas.vartotojas

    def get_success_url(self):
        return reverse('uzsakymas', kwargs={'pk': self.kwargs['uzsakymas_pk']})

class UzsakymasEiluteDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = UzsakymoEilute
    template_name = 'uzsakymoeilute_delete.html'
    context_object_name = 'uzsakymoeilute'
    def get_success_url(self):
        return reverse('uzsakymas', kwargs={'pk': self.kwargs['uzsakymas_pk']})
    def test_func(self):
        uzsakymas = Uzsakymas.objects.get(pk=self.kwargs['uzsakymas_pk'])
        return self.request.user == uzsakymas.vartotojas





@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Vartotojo vardas {username} užimtas!')
                return redirect('register')
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
                    return redirect('register')
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(username=username, email=email, password=password)
                    messages.info(request, f'Vartotojas {username} užregistruotas!')
                    return redirect('login')
        else:
            messages.error(request, 'Slaptažodžiai nesutampa!')
            return redirect('register')
    return render(request, 'register.html')

@login_required
def profilis(request):
    return render(request, 'profilis.html')

@login_required
def profilis(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfilisUpdateForm(request.POST, request.FILES, instance=request.user.profilis)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profilis atnaujintas")
            return redirect('profilis')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfilisUpdateForm(instance=request.user.profilis)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'profilis.html', context)