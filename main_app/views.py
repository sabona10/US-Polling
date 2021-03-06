from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from .forms import QuestionForm
from .forms import ResponseForm

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
  #cache for updating has_votes property
  userId = request.user
  
  hasVoted = poll.hasVoted.split('&')

  #cache for results
  try:
    poll_response = []
    responses = Response.objects.filter(poll=poll_id)
   
    for idx, x in enumerate(responses[0].response):
      yes = 0
      no = 0
      idc = 0
      for response in responses:
        question = response.response[idx]
        if question == '1': yes += 1
        if question == '2': no += 1
        if question == '0': idc += 1
      poll_response.append([yes, no, idc])
    # responses = poll_response
  except:
    responses = 'No Responses Yet'
  return render(request, 'polls/detail.html', {'poll': poll,'userId':str(userId.id),'hasVoted':hasVoted, 'poll_response':poll_response})

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

@login_required
def polls_publish(request, poll_id):
  poll = Poll.objects.get(id=poll_id)
  poll.published = True
  poll.save()
  return render(request, 'polls/detail.html', {'poll': poll})

@login_required
def submit_poll(request, poll_id):
  allresponse = ''
  poll = Poll.objects.get(id=poll_id)
  data = request.body.decode('utf-8').split('&')

  for idx, x in enumerate(data):
    if idx >0:
      allresponse += x.split('=')[1]

  new_response = ResponseForm().save(commit=False)
  new_response.response = allresponse
  new_response.poll_id = poll_id
  new_response.save() 

  poll.hasVoted += '&'+str(request.user.id)
  poll.save()
  #print(data[-1])
  print(allresponse)
  #print(request.body)
  return redirect('detail', poll_id = poll_id)

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
