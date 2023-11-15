from django.conf import settings
from pangea.config import PangeaConfig
from pangea.services import Embargo, IpIntel, UserIntel, DomainIntel, Redact, UrlIntel
from pangea.tools import logger_set_pangea_config
import json
from asgiref.sync import sync_to_async
import pangea.exceptions as pe
import os,re


config = PangeaConfig(domain=settings.PANGEA_DOMAIN)
embargo = Embargo(settings.PANGEA_TOKEN, config=config)
redact = Redact(settings.PANGEA_TOKEN, config=config)
ip_intel = IpIntel(settings.PANGEA_TOKEN, config=config)
user_intel = UserIntel(settings.PANGEA_TOKEN, config=config)
domain_intel = DomainIntel(settings.PANGEA_TOKEN, config=config)
url_intel = UrlIntel(settings.PANGEA_TOKEN, config=config)



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def process_comment_url(text):
    url_dict = {}
    flag = False
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    for url in urls:
        response = url_intel.reputation(url=url, provider="crowdstrike")
        url_dict[url] = response.result.data.verdict
        if response.result.data.verdict.lower() == "malicious": flage = True
    return url_dict, flag

def process_comment_domain(text):
    domain_dict = {}
    flag = False
    domains = re.findall(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:/|\s|$)', text)
    for domain in domains:
        response = domain_intel.reputation(domain=domain, provider="crowdstrike")
        domain_dict[domain] = response.result.data.verdict
        if response.result.data.verdict.lower() == "malicious": flage = True
    return domain_dict, flag

def pnagea_services(comment):
    try:
        if comment.ip:
            embargo_response = embargo.ip_check(ip=comment.ip)
            if embargo_response.result:
                if embargo_response.result.count:
                    comment.embargo = embargo_response._json
        
        redact_response = redact.redact(text=comment.body)
        # print(redact_response)
        if redact_response.result.count:
            comment.redact = True
            comment.body = redact_response.result.redacted_text
        
        ip_intel_response = response = ip_intel.reputation(ip=comment.ip, provider="crowdstrike")
        if ip_intel_response.result:
            comment.ip_intel = ip_intel_response.result.data.verdict
            if ip_intel_response.result.data.verdict.lower() == "malicious": comment.malicious = True

        user_intel_response = user_intel.user_breached(email=comment.email, provider="spycloud")
        if user_intel_response.result.data.found_in_breach:
            comment.malicious = True
            comment.user_intel_breach = user_intel_response.result.data.breach_count

        comment.url_intel,url_flag = process_comment_url(comment.body)
        if url_flag: comment.malicious = True
        comment.domain_intel,domain_flag = process_comment_domain(comment.body)
        if domain_flag: comment.malicious = True
        
        comment.save()

    except pe.PangeaAPIException as e:
        print(f"Embargo Request Error: {e.response.summary}")
        for err in e.errors:
            print(f"\t{err.detail} \n")


