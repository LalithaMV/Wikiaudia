from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from wa.models import User, Language, Book, Paragraph, UserHistory, Document
from wa.forms import DocumentForm
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.contrib.auth.forms import UserCreationForm
from forms import CustomUserCreationForm
from django.shortcuts import render

from wa.tasks import soundProcessingWithAuphonicTask
from django.core.urlresolvers import reverse
# Create your views here.

def error_processor(request):
	if 'error' in request.session:
		return {'msg': request.session['error']}
	else:
		return {}
	
def front(request):
	c=RequestContext(request,{'foo':'bar',},[error_processor])
	if 'error' in request.session:
		del request.session['error']
	return render_to_response('wa/session/front.html',c)
	
def logout(request):
	auth.logout(request)
	#return render_to_response('WikiApp/session/front.html')	
	return HttpResponseRedirect('/wa')
	
def auth_view(request):
	username= request.POST.get('username','')
	password= request.POST.get('password','')
	user= auth.authenticate(username=username, password=password)
	if user is not None:
		auth.login(request, user)
		return HttpResponseRedirect('/wa/home')
	else:
		request.session['error'] = "Username and Password do not match.Try Again!"
		return HttpResponseRedirect('/wa')
#Have not done auth.logout(request)	
def home(request):
	return render_to_response('wa/session/home.html', {'full_name':request.user.first_name,'languages_known':request.user.languages_known})
	#return render_to_response('WikiApp/session/home.html', {'full_name':request.user.userprofile.Languages})

def register_user(request):
	if request.method == 'POST':
		form=CustomUserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/wa/register_success')
	else:
		form= CustomUserCreationForm()
	return render(request,  'wa/session/register.html', {
		'form': form,
	})
def register_success(request):
	return render_to_response('wa/session/register_success.html')
	
def digitize(request):
	return render_to_response('wa/AudioDigi/Digitize.html')
def audio(request):
    #languages = Language.objects.all()
	#context = {'all_languages' : all_languages}
    #return render(request, 'wa/audio.html', context)
    #return HttpResponse("You're looking at the results of poll ")
    langs = Language.objects.all()
    context = {'langs': langs}
    return render(request, 'wa/audio.html', context)

def audioUpload(request):
    # Handle file upload
    '''
    Add additional inputs to post to figure out the book and 
    the paragraph number so that the upload takes place in that folder
    Current working : Saves the file with a fixed name and the file sent for API processing is fixed as well. 
    Both of these should be made dynamic 
    '''
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.docfile.save('Ashu.wav',request.FILES['docfile'])
            #soundProcessWithAuphonic('documents/Ashu.wav')
            soundProcessingWithAuphonicTask.delay('../documents/ashu.mp3')
            return HttpResponseRedirect(reverse('wa.views.audio'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'wa/audioUpload.html',
        {'documents': documents, 'form': form},
       
        context_instance=RequestContext(request)
    )
