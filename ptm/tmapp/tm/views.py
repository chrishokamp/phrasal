import logging
from datetime import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from tm.models import SourceTxt,TargetTxt,LanguageSpec,TranslationStats,UISpec

logger = logging.getLogger(__name__)

# Generates a work queue for the user
from tm_workqueue import get_work_list, select_ui_for_user, select_tgt_lang

@login_required
def index(request):
    """ Shows the work queue for each user.
    Args:
    Returns:
    Raises:
    """
    # TODO(spenceg): Load up the work queue for this user
    src_list = get_work_list(request.user)
    
    return render_to_response('tm/index.html',
                              {'src_list' : src_list, 'first_name' : request.user.first_name, 'last_name' : request.user.last_name},
                              context_instance=RequestContext(request))

@login_required
def tr(request, src_id):
    """ Selects a translation interface for this user.
    Args:
    Returns:
    Raises:
    """
    try:
        src = SourceTxt.objects.select_related().get(pk=src_id)
        (ui_name,ui_id) = select_ui_for_user(request.user)
        tgt_lang = select_tgt_lang(src.lang, request.user)

    except SourceTxt.DoesNotExist, RuntimeError:
        raise Http404

    src_toks = src.txt.split()
    ui_template = ''
    if ui_name == 'tr':
        ui_template = 'tm/tr.html'
    elif ui_name == 'meedan':
        ui_template = 'tm/tr_meedan.html'
    elif ui_name == 'trados':
        ui_template = 'tm/tr_trados.html'
    elif ui_name == 'sjc':
        ui_template = 'tm/tr_sjc.html'
    else:
        raise Http404
    
    return render_to_response(ui_template, {'src':src, 'src_toks':src_toks, 'tgt_lang':tgt_lang, 'ui_id':ui_id}, context_instance=RequestContext(request))
    

@login_required
def trdone(request, src_id):
    """
    Args:
    Returns:
    Raises:
    """

    # Get everything out of the POST / request
    tgt_lang_pk = request.POST['form-tgt-lang']
    tgt_txt = request.POST['form-tgt-txt'].strip()
    action_log = request.POST['form-action-log'].strip()
    ui_id = request.POST['form-ui-id'].strip()
    tgt_user = request.user
    tgt_date = datetime.now()

    # Save the actual target translation
    src = get_object_or_404(SourceTxt, pk=src_id)
    tgt_lang = get_object_or_404(LanguageSpec, pk=tgt_lang_pk)

    tgt = TargetTxt.objects.create(src=src,user=tgt_user,date=tgt_date,txt=tgt_txt,lang=tgt_lang)
    tgt.save()

    # Save translation session stats    
    ui = get_object_or_404(UISpec, pk=ui_id)
    
    tgt_stats = TranslationStats.objects.create(tgt=tgt,ui=ui,user=tgt_user,action_log=action_log)
    tgt_stats.save()
    
    return HttpResponseRedirect(reverse('tm.views.history',args=(src_id,)))
    
@login_required
def history(request, src_id):
    """
    Args:
    Returns:
    Raises:
    """
    try:
        src = SourceTxt.objects.select_related().get(pk=src_id)
    except SourceTxt.DoesNotExist:
        raise Http404
    # Now get the translations
    tgt_list = TargetTxt.objects.select_related().filter(src=src_id).order_by('-date')
    return render_to_response('tm/history.html',
                              {'src':src, 'tgt_list':tgt_list},
                              context_instance=RequestContext(request))
