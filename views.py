from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect
from OTS.models import*
import random

def welcome(request):
    template=loader.get_template('welcome.html')
    return HttpResponse(template.render())

def candidateRegistrationForm(request):
    res=render(request,'registration_form.html')
    return res
def candidateRegistration(request):
    if request.method=='POST':
        username=request.POST['username']  #dict of post name and keys are the form name attributes such as username,password,
      #checkif the user already existed
        if(len(Candidate.objects.filter(username=username))):
          userStatus=1
        else:
            candidate=Candidate()#we have made an object of the model
            candidate.username=username
            candidate.password=request.POST['password'] # it is the data that we are getting from the form
            candidate.name=request.POST['name']
            candidate.save()
            userStatus=2
    else:
     userStatus=3 #if the method that we are getting from the form is not of type post
    context={
        'userStatus':userStatus
     }
    res=render(request,'registration.html',context)
    return res
def loginView(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        candidate=Candidate.objects.filter(username=username,password=password)#it will return the queryset matched with the specified attributes
        if len(candidate)==0:
            loginError="INVALID USERNAME OR PASSWORD"
            res=render(request,'login.html', {'loginError':loginError}) #here we have passed loginerror in the dictionary
        else:
            """login success we want to sustain the data until the logout then we make the session variables"""
            request.session['username']=candidate[0].username
            request.session['name']=candidate[0].name
            res=HttpResponseRedirect("home")
            return res
    else:
        res=render(request,'login.html')
    return res
def candidateHome(request):
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")
    else:
        res=render(request,'home.html')
    return res
def testPaper(request):
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login") 
    #fetch the question from the database table
    n=int(request.GET['n'])
    question_pool= list(Question.objects.all())
    random.shuffle(question_pool)
    questions_list=question_pool[:n]
    context={'questions':questions_list}
    res=render(request,'test_paper.html',context)
    return res
def calculateTestResult(request):
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")
    total_attempt = 0
    total_right = 0
    total_wrong = 0
    qid_list =[]
    for k in request.POST:
        if k.startswith('qno'):
            qid_list.append(int(request.POST[k]))
    for n in qid_list:
        question=Question.objects.get(qid=n)
        try:
            if question.ans==request.POST['q'+str(n)]:
              total_right+=1
            else:
                total_wrong+=1
            total_attempt+=1
        except:
            pass
    points = (total_right-total_wrong)/(len(qid_list))*10
    #to store result in result table
    result=Result()
    result.username=Candidate.objects.get(username=request.session['username'])
    result.attempt=total_attempt
    result.right=total_right
    result.wrong=total_wrong
    result.points=points
    result.save()
    #update candidate table
    candidate=Candidate.objects.get(username=request.session['username'])
    candidate.test_attempted+=1
    candidate.points =(candidate.points*(candidate.test_attempted-1)+points)/candidate.test_attempted
    candidate.save()
    res=HttpResponseRedirect("result")
    return res

def testResultHistory(request):
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")

    candidate=Candidate.objects.filter(username=request.session['username'])
    results= Result.objects.filter(username_id=candidate[0].username)
    context={'candidate':candidate[0],'results':results}
    res=render(request,'candidate_history.html',context)
    return res
def showTestResult(request):
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")
    #fetch result from the Result table
    result=Result.objects.filter(resultid=Result.objects.latest('resultid').resultid,username_id=request.session['username'])
    context={'result':result}
    res=render(request,'show_result.html',context)
    return res
def logoutView(request):
    if 'name'  in request.session.keys():
        del request.session['username']
        del request.session['name']
        return HttpResponseRedirect("login")
# Create your views here.
