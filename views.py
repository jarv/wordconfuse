# Create your views here.
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import simplejson
from defs import WORDS
from time import time
from wordconfuse.models import GameScores,Words
from wordconfuse.forms import NewHS,GameOver
import random

def index(request):
    return render_to_response('index.html')

def get_words(request):
    # select 10 entries from the word data
    r_set = Words.objects.order_by('?')[:10]
    # list of words that we will be testing
    w_list = r_set.values_list('word', flat=True)
    exclude_list = []
    data = list()
    for entry in r_set:
        # to pick the answers we will select
        # 3 random entries from the remaining
        # words in the set that use the same
        # part of speech as the answer.  
        exclude_list.append(entry.word)

        entry_exclude = []
        answer_list = []

        for x in range(0,3): 
            answer = Words.objects.exclude(word__in=exclude_list+entry_exclude).filter(speech=entry.speech).order_by('?')[0]
            entry_exclude.append(answer.word)
            answer_list.append(answer.definition)

        answer_list.insert(random.randrange(len(answer_list)+1),entry.definition)
        d = {
                'q': entry.word,
                'a': answer_list,
                's': answer_list.index(entry.definition)
            }
        data.append(d)
        
    request.session['start_game'] = float("%0.2f" % time())
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

@csrf_exempt
def gameover(request):
    if request.method == 'POST':
        form = GameOver(request.POST)
        if not form.is_valid():
            return HttpResponse('Validation Error')

        count = int(form.cleaned_data['count'])
        now = float("%0.2f" % time())

        if not request.session['start_game']:
            return HttpResponse('Error')

        game_time = float("%0.2f" % (now - request.session['start_game']) )
        g = GameScores(
                ip=request.META['REMOTE_ADDR'],
                time_start=request.session['start_game'],
                time_end=now,
                time_delta=game_time,
                count=count)
        g.save();
        request.session['last_id'] = g.id
        form = NewHS()
        hs = GameScores.objects.filter(username__isnull=False).order_by('-count', 'time_delta')[0:6]
        new_hs = False
        
        if len(hs) < 6 or count > hs[5].count:
            new_hs = True
        elif count == hs[5].count and game_time < hs[5].time_delta:
            new_hs = True

        go = {
            'new_hs': new_hs,
            'delta': game_time,
            'count': count,
        }
        return render_to_response('gameover.html',
                {
                    'form':form,
                    'hs':hs,
                    'go':go,
                })
    return HttpResponse('Derp, you need to post something')

@csrf_exempt
def new_hs(request):
    if request.method == 'POST':
        form = NewHS(request.POST)
        if not form.is_valid():
            HttpResponse('Invalid Username')
        g = GameScores.objects.get(id=request.session['last_id'])
        g.username = form.cleaned_data['username']
        g.save()
        hs = GameScores.objects.filter(username__isnull=False).order_by('-count', 'time_delta')[0:6]
        return render_to_response('hs.html', { 'hs':hs, })
    return HttpResponse('Derp, you need to post the username')

def hs(request):
    hs = GameScores.objects.filter(username__isnull=False).order_by('-count', 'time_delta')[0:6]
    return render_to_response('hs.html', { 'hs': hs, })

