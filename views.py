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

def get_words(request):
    # select 10 random entries from the database and put them
    # into a list 
    r_set = Words.objects.order_by('?')[:10]
    # As we build up quiz data we will maintain
    # a list of words to exclude so that words aren't
    # repeated during the quiz.
    exclude_list = []
    data = list()
    for entry in r_set:
        # the word for the quiz is added
        # to the exclude list so it won't be used
        # for any of the answers or any of the
        # subsequent words
        exclude_list.append(entry.word)

        # for every question this keeps track
        # of what words are used as answers so
        # they are not repeated
        entry_exclude = []

        # answer_list is a list of defintions
        # that will contain the choices for
        # the word.
        answer_list = []

        # 3 answers are picked randomly from the
        # full word set in the database. with the
        # following constraints:
        #   a) the defintion cannot correspond to 
        #      a word that was already used as
        #      an answer (entry_exclude)
        #   b) the definition cannot correspond to 
        #      one of the words that was used for
        #      the quiz (exclude_list)
        #   c) the definition must correspond to 
        #      the same part-of-speech of the word
        #      being quizzed.

        for x in range(0,3): 
            answer = Words.objects.exclude(word__in=exclude_list+entry_exclude).filter(speech=entry.speech).order_by('?')[0]
            entry_exclude.append(answer.word)
            answer_list.append(answer.definition)

        # now that we have three wrong defitions to be used
        # as answers for the word being quizzed the real
        # answer needs to be inserted randomly into the list
        answer_list.insert(random.randrange(len(answer_list)+1),entry.definition)
        # this dictionary represents the JSON data that will
        # be returned to the browser
        #  q - the word being quizzed
        #  a - the list of 4 defintions to pick from
        #  s - the index into 'a' that corresponds to the
        #      correct definition
        d = {
                'q': entry.word,
                'a': answer_list,
                's': answer_list.index(entry.definition)
            }
        data.append(d)

    # record the start time in a session variable, this will
    # be used later in the gameover view to calculate how much
    # time it took to complete the game
    request.session['start_game'] = float("%0.2f" % time())

    # return the words, answers, and solutions in a JSON response
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

