from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Poll
from .forms import QuestionForm

class PollCreate(LoginRequiredMixin, CreateView):
  model = Poll
  fields = ['title', 'abstract', 'content']

  def form_valid(self, form): 
    form.instance.user = self.request.user
    return super().form_valid(form)

class PollDelete(LoginRequiredMixin, DeleteView):
  model = Poll
  success_url = '/polls/'

def home(request):
  return render(request, 'home.html')

@login_required
def polls_index(request):
  polls = Poll.objects.all()
  return render(request, 'polls/index.html', {'polls': polls})

@login_required
def polls_detail(request, poll_id):
  poll = Poll.objects.get(id=poll_id)
  return render(request, 'polls/detail.html', {'poll': poll})

@login_required
def polls_edit(request, poll_id):
  poll = Poll.objects.get(id=poll_id)
    # toys_poll_doesnt_have = Toy.objects.exclude(id__in=poll.toys.all().values_list('id'))
  question_form = QuestionForm()
  return render(request, 'polls/edit.html', {
    # pass the poll and question_form as context
    'poll': poll, 'question_form': question_form
    # 'toys': toys_poll_doesnt_have
  })

  return render(request, 'polls/edit.html', {'poll': poll})

@login_required
def add_question(request, poll_id):
	# create the ModelForm using the data in request.POST
  form = QuestionForm(request.POST)
  # validate the form
  if form.is_valid():
    # don't save the form to the db until it
    # has the poll_id assigned
    new_question = form.save(commit=False)
    new_question.poll_id = poll_id
    new_question.save()
  return redirect('edit', poll_id=poll_id)




def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('home')
    else:
      error_message = 'Failed to sign up'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)
