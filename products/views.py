"""Import models"""
from django.core.files.base import ContentFile
from django.shortcuts import render
from products.forms import URLForm
from .models import *
from Main_extract.feature_extractor import *
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from django.core.cache import cache
import pandas as pd
import time
from pathlib import Path
from ml_model_src.prediction import *
import folium
import geocoder
from urllib.parse import urlparse
import csv




RESULT_FILE = ""
PROCESS_FALG = None
FEATURES = []
RESULTS_PREDICT = {}
FOLDER_RESULT_NAME = ""
ALL_URLS_DB = None
RELATED_PULSES = []


drop_list = [ 
                # Investigation findings
                'host', # ip address
                "get_asn",  # asn                           | source Shodan, ipinfo
                "longitude", # lon                          | shource Shodan
                "latitude" , # lat                          | shource Shodan
                'num_open_ports' , # number of open ports   | source shodan
                "hostnames", # host names | source shodan, ipinfo
                'open_ports', # open ports | source shodan
                "subdomains", # subdomain | source shodan, whois
                'isp', # isp source shodan
                'connection_speed',  
                'is_live', 
                # Lifecycle Information
                'registration_date', # source whois
                'expiration_date', # source whois
                'last_updates_dates', # source whois 
                'intended_life_span', # (self.url_expiration_date() - self.url_creation_date()).days
                'life_remaining', # (self.url_expiration_date() - self.now).days
                'ttl', # ttl_from_registration
                # HTTP Response
                "url",  
                'tld',   
                'suspecious_tld', 
                'status_code', 
                'header',
                
                 
                'has_port_in_string',  
                'ip', # is have ip in url


                'domain_in_brand','port_in_url','shortening_service',
                'statistical_report', 'external_favicon', 'links_in_tags', 'sfh',  
                'popup_window', 'whois_registered_domain',
                'nameServerwhois', 'HTMLinfo']

def run_tasks_in_parallel(tasks, request,submitedUrl ):
    global RESULTS_PREDICT
    start = time.time()
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task, request,submitedUrl ) for task in tasks]
        for running_task in as_completed(running_tasks):
            # running_task.result()
            taskres = running_task.result()
            RESULTS_PREDICT.update(taskres)
    end = time.time()

    print(f"\n------------------------------------TIME-----------------------------\n: {end-start}s")

def get_related_urls(URLsubmitByUser):
    global ALL_URLS_DB
    global RELATED_PULSES
    RELATED_PULSES = []


    parsed_url = urlparse(URLsubmitByUser)
    base_url = parsed_url.netloc
    for i in ALL_URLS_DB:
        if base_url in i.url:
            RELATED_PULSES.append(i)

def location_view(data):
    global FOLDER_RESULT_NAME
    print("============MAP VIEW============\n")
    start = time.time()
    ip = str(data["host"].values[0])
    IPLocache = geocoder.ip(ip)
    mapPlot = folium.Map(location=IPLocache.latlng, titles = "Open test", zoom_start=12)
    folium.Circle(location=IPLocache.latlng, radius=50).add_to(mapPlot)
    folium.Marker(location=IPLocache.latlng, popup="My location").add_to(mapPlot)
    path = 'media/loc/' + 'loc_{}.html'.format(Path(FOLDER_RESULT_NAME).name)
  
    mapPlot.save(path)
    end = time.time()
    print(f"\n------------TIME MAP VIEW----------\n: {end-start}s")
    return path

def save_staticResults(request, submitedUrl):
    print("============STATIC============\n")
    global FEATURES
    url_submit_by_user = submitedUrl.url
    res = static_prediction(FEATURES)

    static_result.objects.get_or_create(user = request.user, url = submitedUrl)
    staticResult = static_result.objects.get(url = submitedUrl)

    staticResult.prediction = res["prediction"]
    staticResult.conf_score = res["conf_score"]
    staticResult.url = url_submit_by_user

    if res["prediction"] == 1:
        staticResult.status = 'Phishing'
    else:
        staticResult.status = 'Normal'
    staticResult.save()
    return {'static':res["prediction"]}

def save_dynamicResult(request,submitedUrl):
    print("============DYNAMIC============\n")
    # dynamic prediction PROCESS_FALG
    global FOLDER_RESULT_NAME
    print("------------Screenshot folder------------\n", FOLDER_RESULT_NAME)
    url_submit_by_user = submitedUrl.url
    res = dynamic_predictions(FOLDER_RESULT_NAME)

    dynamic_result.objects.get_or_create(user = request.user, url = submitedUrl)
    dynamicResult = dynamic_result.objects.get(url = submitedUrl)
    b_name = res['brand_name'] if res['brand_name']!= None else "No brand name"
    dynamicResult.brand_name = b_name
    dynamicResult.conf_score = res['conf_score'] if res['conf_score'] != None else "0"
    dynamicResult.prediction = res["prediction"]

    dynamicResult.url= url_submit_by_user
    if res["prediction"] == 1:
        dynamicResult.status = 'Phishing'
    else:
        dynamicResult.status = 'Normal'
    dynamicResult.save()
    
    return { "vt_score" : res["virustotal"], "img_path" : res['image_result'], 'brand_name': b_name, 'dynamic':res["prediction"] }

# def MyUrl(request):
#     all_url = final_result.objects.filter(user=request.user).order_by('-time')
#     return render(request, 'MyUrl.html', { 'count': all_url.count(), 'url': all_url})

# Trang thông báo lỗi
def error404(request, *args, **kwargs):
    return render(
        request, '404.html'
    )


def url_details(request, pid):
    global RELATED_PULSES
    global ALL_URLS_DB
    ALL_URLS_DB = []
    ALL_URLS_DB = final_result.objects.all().order_by('-time')
    re = final_result.objects.get(url_id = pid)
    get_related_urls(re.url)
    return render(request, 'url_detail.html', {'Result': re, 'related_pulses': RELATED_PULSES})
    
def img_details(request, pid):
    obj = final_result.objects.get(url_id = pid) 
    return render(request, 'img_details.html', {'obj': obj})


def home(request):
    global RESULT_FILE
    global PROCESS_FALG 
    global FEATURES
    global RESULTS_PREDICT
    global FOLDER_RESULT_NAME
    global ALL_URLS_DB
    global RELATED_PULSES

    ALL_URLS_DB = final_result.objects.all().order_by('-time')
    top_URLs = ALL_URLS_DB[:15]

    form = URLForm()
    if request.method == 'POST':
        form = URLForm(request.POST, user=request.user)
        if form.is_valid():
            #save url to final_result form
            # form.save()
            URLsubmitByUser = form.showURL()
            get_related_urls(URLsubmitByUser)
            

            if cache.get(URLsubmitByUser):
                submitedUrl = cache.get(URLsubmitByUser)
                print("HIT THE CACHE")
                # return render(request, 'url_detail.html', {'Result': submitedUrl , 'get_all_urls_from_wayback':None, 'find_login_page_from_wayback':None, 'find_admin_page_from_wayback':None})
                return render(request, 'url_detail.html', {'Result': submitedUrl , 'related_pulses': RELATED_PULSES})
            else:
                try:
                    start_time = time.time()
                    #caculate conf_score & prediction
                    print("============START PREPROCESS: EXTRACTION & SCREENSHOT TAKING============\n")
                    FOLDER_RESULT_NAME, RESULT_FILE = Extracter(URLsubmitByUser)
                    print("============END PREPROCESS============\n")

                    if FOLDER_RESULT_NAME == False:
                        PROCESS_FALG = False
                        return render(request, 'detect.html', { 'count': top_URLs.count(), 'url': top_URLs, 'form':form, 'process': PROCESS_FALG})

                    form.save()
                    submitedUrl = final_result.objects.filter(user=request.user).latest('time')
                    print("============WORKING ON OBJECT WITH URL {0}============\n".format(submitedUrl.url))
                    # read result
                    results = pd.read_csv(RESULT_FILE, on_bad_lines='skip')
                    submitedUrl.loc_path = location_view(results)
                    submitedUrl.host = results["host"].values[0]
                    submitedUrl.is_live = results["is_live"].values[0]
                    submitedUrl.host_country = results["host_country"].values[0]
                    submitedUrl.get_asn = results["get_asn"].values[0]
                    submitedUrl.num_open_ports = results["num_open_ports"].values[0]
                    submitedUrl.subdomains = results["subdomains"].values[0]
                    submitedUrl.hostnames = results['hostnames'].values[0]
                    submitedUrl.open_ports= results["open_ports"].values[0]
                    submitedUrl.connection_speed = results["connection_speed"].values[0]
                    submitedUrl.isp= results["isp"].values[0]
                    submitedUrl.nameServerwhois = results["nameServerwhois"].values[0]
                    submitedUrl.HTMLinfo = results["HTMLinfo"].values[0]
                    submitedUrl.registration_date = results["registration_date"].values[0]
                    submitedUrl.expiration_date= results["expiration_date"].values[0]
                    submitedUrl.last_updates_dates = results['last_updates_dates'].values[0]
                    submitedUrl.intended_life_span = results['intended_life_span'].values[0]
                    submitedUrl.life_remaining = results['life_remaining'].values[0]
                    submitedUrl.ttl = results['ttl'].values[0]
                    submitedUrl.finalurl = results['url'].values[0]
                    submitedUrl.scheme = results["scheme"].values[0]
                    submitedUrl.status_code = results['status_code'].values[0]
                    submitedUrl.headers = results['header'].values[0]
                    submitedUrl.tld = results['tld'].values[0]
                    submitedUrl.suspecious_tld = results['suspecious_tld'].values[0]
                    
                
                    submitedUrl.has_port_in_string = results['has_port_in_string'].values[0]
                    submitedUrl.ip = results['ip'].values[0]

                    print("============DATA ANALYSIS============\n")
                    data = results.drop(columns=drop_list)
                    
                    data = convertData(data)
                    data = data.fillna(0)
                    fields = data.columns

                    
                    FEATURES = []
                    for f in fields:
                        FEATURES.append(float(data[str(f)].values[0]))
                    
                    with open("data.csv", "w", encoding='utf-8', newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(fields)
                        writer.writerow(FEATURES)
                        
                    print("============X FEATURES============\n", len(FEATURES))
                    print("============FOLDER_RESULT_NAME============\n", FOLDER_RESULT_NAME)
                    run_tasks_in_parallel([
                        save_staticResults,
                        save_dynamicResult
                    ], request,submitedUrl )
                    print("============ RESULTS_PREDICT ============ \n",RESULTS_PREDICT)
                    
                    # start = time.time()
                    # s = save_staticResults(request,  submitedUrl)
                    # end = time.time()
                    # print(f"\n------------TIME STATIC----------\n: {end-start}s")

                    
                    # start = time.time()
                    # d = save_dynamicResult(request, submitedUrl)
                    # end = time.time()
                    # print(f"\n------------TIME DYNAMIC----------\n: {end-start}s")

                   

                    print("Random Forest Result = ", RESULTS_PREDICT['static'])
                    print("Object Detection Model Result ", RESULTS_PREDICT['dynamic'])
                    score = float(RESULTS_PREDICT['static'])*0.3 + float(RESULTS_PREDICT['dynamic'])* 0.7
                    ## final results evaluation 7:3 
                    final_score = 0

                    if score >=0.5:
                        final_score = 1
                    elif score == 0.3:
                        final_score = 0
                    else:
                        final_score = 0
                    
                    submitedUrl.prediction_final = final_score
                    if final_score == 1:
                        submitedUrl.status = "phishing"
                    elif final_score == 0.5:
                        submitedUrl.status = "warning"
                    else: 
                        submitedUrl.status = "normal"
                    print("============ FINAL RESULT ============ \n",RESULTS_PREDICT)
                    print("Score: ", score)
                    print("Final score: ", final_score)
                    submitedUrl.vt_score = RESULTS_PREDICT['vt_score']

                    with open(RESULTS_PREDICT['img_path'], 'rb') as f:
                        data = f.read()
                    submitedUrl.img_path.save("predict.png", ContentFile(data) )
                    submitedUrl.brand_name = RESULTS_PREDICT['brand_name'] 

                    submitedUrl.save()
                    PROCESS_FALG = True

                    print("TIME ----->: ", round(time.time() - start_time, 4))

                    cache.set(URLsubmitByUser, submitedUrl) # cache for 7 days
                    print("HIT THE DB")
                    return render(request, 'url_detail.html', {'Result': submitedUrl , 'related_pulses': RELATED_PULSES})
                except final_result.DoesNotExist:
                    print("Does not exist")
                    return render(request, 'detect.html', { 'count': top_URLs.count(), 'url': top_URLs, 'form':form, 'process': PROCESS_FALG})
    return render(request, 'detect.html', { 'count': top_URLs.count(), 'url': top_URLs, 'form':form, 'process': PROCESS_FALG})

