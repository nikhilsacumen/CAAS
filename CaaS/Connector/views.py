from django.shortcuts import render, redirect, HttpResponse
import json
from django.shortcuts import render
from .config import payload
from .models import SSCConnector
from django.contrib import messages
from ssc.main import collect_events
from Jira import views, models
from Slack.utils import send_message_to_slack
from django.contrib.auth.decorators import login_required
from Slack.models import Slack
import datetime


@login_required(login_url='/login/')
def home(request):
    if request.POST:
        current_user = request.user
        ssc_data = request.POST.dict()
        interval = ssc_data.get('interval')
        api_url = ssc_data.get('api_url')
        api_token = ssc_data.get('api_token')
        overall_score = ssc_data.get('overall_score')
        factor_score = ssc_data.get('factor_score')
        issue_level_event = ssc_data.get('issue_level')
        domain = ssc_data.get('domain')
        try:
            ssc_obj = SSCConnector.objects.filter(user_id = request.user).first()
        except Exception as err:
            print("Getting exception as {}".format(err))
        else:
            if not ssc_obj:
                new_ssc = SSCConnector(user_id=current_user, interval=interval, api_url=api_url, api_token=api_token,
                                       overall_score=overall_score,
                                       factor_score=factor_score, issue_level_event=issue_level_event, domain=domain)
                new_ssc.save()
                messages.success(request, f'Your SecurityScoreCard is Registered')
            else:
                ssc_obj.interval = interval
                ssc_obj.api_url = api_url
                ssc_obj.api_token = api_token
                ssc_obj.overall_score = overall_score
                ssc_obj.factor_score = factor_score
                ssc_obj.issue_level_event =issue_level_event
                ssc_obj.domain = domain
                ssc_obj.save()
                messages.success(request, f'Your SecurityScoreCard is Saved Successfully')

        return redirect('/ssc_connector/ssc/')
    else:
        current_user = request.user
        ssc_data =  SSCConnector.objects.filter(user_id = current_user).first()
        slack_data  =  Slack.objects.filter(source_id =  ssc_data).first()
        jira_data = models.Jira.objects.filter(user_id = current_user).first()
    return render(request, 'dashboard/home.html',context={'ssc_data':ssc_data, 'jira_data':jira_data, 'slack_data':slack_data})

@login_required(login_url='/login/')
def process_ssc(request):
    try:
        ssc_user = SSCConnector.objects.filter(user_id=request.user).first()
        slack_user = Slack.objects.filter(source_id__user_id=request.user).first()
        jira_user = models.Jira.objects.filter(user_id=request.user).first()

        slack_flag = slack_user and slack_user.flag
        jira_flag = jira_user and jira_user.flag
        ssc_flag = ssc_user and ssc_user.flag
    except Exception as err:
        print("Getting exception as {}".format(err))
    else:
        if not ssc_flag:
            # To do: disable jira and slack
            pass
        else:
            if not jira_user and not slack_user:
                return messages.warning(request, f'No app is configured.. Please configure at least one..!!')
            if jira_flag:
                url, username, api_token, options_str = jira_user.app_url, jira_user.email_id, jira_user.api_key, jira_user.jira_config
                options_formatted = options_str.replace("'", '"')
                options = json.loads(options_formatted)
                jira_obj = views.Connector(url, username, api_token)
                access_key, base_url, domain = ssc_user.api_token, ssc_user.api_url, ssc_user.domain
                sc_jira_response = collect_events(access_key, domain, **options)
                data = process_ssc_response(sc_jira_response)
                for each_record in data:
                    current_time = str(datetime.datetime.now())
                    msg = "New SecurityScorecard Issue is reported on {}.".format(current_time)
                    payload["fields"]["summary"] = msg
                    payload["fields"]['description']['content'][0]['content'][0]['text'] = json.dumps(each_record[0])
                    jira_resp = jira_obj.create_issue(**payload)
                else:
                    messages.success(request, f"New issue is reported in Jira.")
            if slack_flag:
                access_key, base_url, domain = ssc_user.api_token, ssc_user.api_url, ssc_user.domain
                options_str = slack_user.config
                options_formatted = options_str.replace("'", '"')
                options = json.loads(options_formatted)
                sc_slack_response = collect_events(access_key, domain, **options)
                data = process_ssc_response(sc_slack_response)
                for each_record in data:
                    send_message_to_slack(token=slack_user.auth_token, channel=slack_user.default_channel, message=each_record[0])


def process_ssc_response(sc_response):
    for key, each_factor in sc_response.items():
        if isinstance(each_factor, list):
            for each in each_factor:
                tmp = list()
                tmp.append(each)
                yield tmp
        else:
            tmp = list()
            tmp.append(each_factor)
            yield tmp


def ssc_test(request):
   
    token = request.POST.get('api_token',None)
    domain = request.POST.get('domain',None)
    options = {"fetch_company_overall":True}
    sc_response = collect_events(token, domain, **options)
    if sc_response['overall_resp'] is  not None:
        return HttpResponse("Success")


def set_jira_flag(request):
    set_flag(request, models.Jira, 'Jira')
    return redirect("/ssc_connector/ssc/")


def set_slack_flag(request):
    set_flag(request, Slack, 'Slack')
    return redirect("/ssc_connector/ssc/")


def set_ssc_flag(request):
    set_flag(request, SSCConnector, 'SecurityScoreCard')
    return redirect("/ssc_connector/ssc/")


def set_flag(request, flag_obj, flag_name):
    # ssc = flag_obj.objects.filter(user_id=request.user).first()
    if flag_name == "Slack":
        ssc = flag_obj.objects.filter(source_id__user_id=request.user).first()
    else:
        ssc = flag_obj.objects.filter(user_id=request.user).first()
    if ssc:
        if ssc.flag:
            msg = "{} is Deactivated".format(flag_name)
            ssc.flag = False
            ssc.save()
            messages.warning(request, msg)
        else:
            msg = "{} is Activated".format(flag_name)
            ssc.flag = True
            ssc.save()
            process_ssc(request)
            messages.success(request, msg)