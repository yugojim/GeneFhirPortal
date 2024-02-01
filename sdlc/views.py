from django.shortcuts import render#, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden#, HttpResponseRedirect
#from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage \
    #,VideoSendMessage, AudioSendMessage, LocationSendMessage, StickerSendMessage\
        #, ButtonsTemplate, TemplateSendMessage, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
from datetime import datetime
import numpy as np
import pandas as pd
import pathlib
import os
import json 
import PyPDF2
import base64
import requests
import psycopg2
import csv
from . import Function
from . import models

from django.core.servers.basehttp import WSGIServer
WSGIServer.handle_error = lambda *args, **kwargs: None

import warnings
warnings.filterwarnings('ignore')

DocumentPath = str(pathlib.Path().absolute()) + "/static/doc/"
risk = DocumentPath + 'risk.csv'
riskdf = pd.read_csv(risk, encoding='utf8')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fhir = 'http://192.168.211.9:8080/fhir/'#4600VM
postgresip = "192.168.211.19"
genepostgresip = "172.174.201.121"
#genepostgresip = "104.208.68.39"
#genepostgresip = "10.97.242.13"
#genepostgresport="8081"
genepostgresport="5432"
jsonPath=str(pathlib.Path().absolute()) + "/static/template/Observation-Imaging-EKG.json"
ObservationImagingEKGJson = json.load(open(jsonPath,encoding="utf-8"))
 
@csrf_exempt 
def index(request):
    #User = get_user_model()
    #usersdf = User.objects.all().values()
    #print(type([{i.title: i.specs} for i in User.objects.all()]))
    #print([{i.title: i.specs} for i in User.objects.all()])
    user = request.user
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'index.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'index.html', context)
    
def GeneReport(request):
    ReportNo=''
    MPNo=''
    MRN=''
    user = request.user
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml where true '
        #consentsql = 'SELECT * FROM public.reportxml WHERE "ReportNo" = \'M111-10001\''

        if request.POST['ReportNo'] != '':
            ReportNo = request.POST['ReportNo']
            consentsql = consentsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\' '
        if request.POST['MPNo'] != '':
            MPNo = request.POST['MPNo']
            consentsql = consentsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\' '
        if request.POST['MRN'] != '':
            MRN = request.POST['MRN']
            consentsql = consentsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%' "
        #elif request.POST['PatientName'] != '':
        #    consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'FullName' LIKE '%" + request.POST['PatientName'] + "%';"
        #elif request.POST['OrderingMD'] != '':
        #    consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'OrderingMD' LIKE '%" + request.POST['OrderingMD'] + "%';"
        #elif request.POST['Diagnosis'] != '':
        #    consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'SubmittedDiagnosis' LIKE '%" + request.POST['Diagnosis'] + "%';"
        #consentsql = consentsql + ' LIMIT 200'
        search={'ReportNo' : ReportNo,
                'MPNo' : MPNo,
                'MRN' : MRN
                }        
        cur.execute(consentsql)
        rows = cur.fetchall()
        #print(type(rows))
        df = pd.DataFrame(rows)
        #print(consentsql)
        df.to_csv('static/doc/datalist.csv', sep='\t', encoding='utf-8')
        #print(len(rows))
        SELECTint=len(rows)
        conn.close()
        context = {
                'Generight' : Generight,
                'search' : search,
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'GeneReport.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'GeneReport.html', context)

def PMI(request):
    #ReportNo=''
    #MPNo=''
    #MRN=''
    Diagnosis=''
    TestType=''
    OrderingMD=''
    user = request.user
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml where true '
        #if request.POST['ReportNo'] != '':
        #    ReportNo = request.POST['ReportNo']
        #    consentsql = consentsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\' '
        #if request.POST['MPNo'] != '':
        #    MPNo = request.POST['MPNo']
        #    consentsql = consentsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\' '
        #if request.POST['MRN'] != '':
        #    MRN = request.POST['MRN']
        #    consentsql = consentsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%' "
        if request.POST['Diagnosis'] != '':
            Diagnosis = request.POST['Diagnosis']
            consentsql = consentsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'SubmittedDiagnosis' LIKE '%" + request.POST['Diagnosis'] + "%' " 
        if request.POST['TestType'] != '':
            TestType = request.POST['TestType']
            consentsql = consentsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'Sample' ->> 'TestType' LIKE '%" + request.POST['TestType'] + "%' "
        if request.POST['OrderingMD'] != '':
            OrderingMD = request.POST['OrderingMD']
            consentsql = consentsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'OrderingMD' LIKE '%" + request.POST['OrderingMD'] + "%' " 
        
        cur.execute(consentsql)
        rows = cur.fetchall()
        
        datalistsql = "SELECT id, \"ReportNo\",\"MPNo\", \
            resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' as \"MRN\", \
                resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'SubmittedDiagnosis' as \"Diagnosis\", \
                    resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'Sample' ->> 'TestType' as \"NGS Assay\", \
                        resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'OrderingMD' as \"OrderingMD\" \
                            FROM public.reportxml where true "
        #if request.POST['ReportNo'] != '':            
        #    datalistsql = datalistsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\''
        #if request.POST['MPNo'] != '':            
        #    datalistsql = datalistsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\''
        #if request.POST['MRN'] != '':           
        #    datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%'"
        if request.POST['Diagnosis'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'SubmittedDiagnosis' LIKE '%" + request.POST['Diagnosis'] + "%'" 
        if request.POST['TestType'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'Sample' ->> 'TestType' LIKE '%" + request.POST['TestType'] + "%'"
        if request.POST['OrderingMD'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'OrderingMD' LIKE '%" + request.POST['OrderingMD'] + "%'" 
            
        cur.execute(datalistsql)
        datalist = cur.fetchall()
        df = pd.DataFrame(datalist)
        #print(consentsql)
        column_list = ["Id", "報告號碼", "分生號碼", "病歷號", "Diagnosis", "檢測項目", "臨床主治醫師"]  
        df.columns=column_list
        df.to_csv('static/doc/datalist.csv', encoding='utf-8-sig' ,index=False)
        
        SELECTint=len(rows)
        conn.close()
        search={#'ReportNo' : ReportNo,
                #'MPNo' : MPNo,
                #'MRN' : MRN,
                'Diagnosis' : Diagnosis,
                'TestType' : TestType,
                'OrderingMD' : OrderingMD
                } 
        context = {
                'Generight' : Generight,
                'search' : search,
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'PMI.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'PMI.html', context)

def Biomarker(request):
    #ReportNo=''
    #MPNo=''
    #MRN=''
    status=''
    score=''
    user = request.user
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml where true '       
        #if request.POST['ReportNo'] != '':
        #    ReportNo = request.POST['ReportNo']
        #    consentsql = consentsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\' '
        #if request.POST['MPNo'] != '':
        #    MPNo = request.POST['MPNo']
        #    consentsql = consentsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\' '
        #if request.POST['MRN'] != '':
        #    MRN = request.POST['MRN']
        #    consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%' "
        if request.POST['status'] != '':
            status = request.POST['status']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'biomarkers' -> 'microsatellite_instability' ->> 'status' LIKE '%" + request.POST['status'] + "%'"
        if request.POST['score'] != '':
            score = request.POST['score']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'biomarkers' -> 'tumor_mutation_burden' ->> 'score' LIKE '%" + request.POST['score'] + "%'" 
        #print(consentsql)
        cur.execute(consentsql)
        rows = cur.fetchall()
        
        datalistsql = "SELECT id, \"ReportNo\",\"MPNo\", \
            resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' as \"MRN\", \
                resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'biomarkers' -> 'microsatellite_instability' ->> 'status' as \"Microsatellite Status\", \
                    resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'biomarkers' -> 'tumor_mutation_burden' ->> 'score' as \"Tumor Mutational Burden score\" \
                        FROM public.reportxml where true "
        #if request.POST['ReportNo'] != '':
        #    datalistsql = datalistsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\''
        #if request.POST['MPNo'] != '':
        #    datalistsql = datalistsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\''
        #if request.POST['MRN'] != '':
        #    datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%'"
        if request.POST['status'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'biomarkers' -> 'microsatellite_instability' ->> 'status' LIKE '%" + request.POST['status'] + "%'"
        if request.POST['score'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'biomarkers' -> 'tumor_mutation_burden' ->> 'score' LIKE '%" + request.POST['score'] + "%'" 
            
        cur.execute(datalistsql)
        datalist = cur.fetchall()
        df = pd.DataFrame(datalist)
        column_list = ["Id", "報告號碼", "分生號碼", "病歷號", "Microsatellite Status", "Tumor Mutational Burden score"]  
        df.columns=column_list
        df.to_csv('static/doc/datalist.csv', encoding='utf-8-sig' ,index=False)
        
        SELECTint=len(rows)
        conn.close()
        search={#'ReportNo' : ReportNo,
                #'MPNo' : MPNo,
                #'MRN' : MRN,
                'status' : status,
                'score' : score
                } 
        context = {
                'Generight' : Generight,
                'search' : search,
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'Biomarker.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'Biomarker.html', context)
    
def ShortVariants(request):
    #ReportNo=''
    #MPNo=''
    #MRN=''
    gene=''
    protein_effect=''
    cds_effect=''
    allele_fraction=''
    functional_effect=''
    user = request.user
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml where true '       
        #if request.POST['ReportNo'] != '':
        #    ReportNo = request.POST['ReportNo']
        #    consentsql = consentsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\' '
        #if request.POST['MPNo'] != '':
        #    MPNo = request.POST['MPNo']
        #    consentsql = consentsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\' '
        #if request.POST['MRN'] != '':
        #    MRN = request.POST['MRN']
        #    consentsql = consentsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%'"
            
        if request.POST['gene'] != '':
            gene = request.POST['gene']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['gene'] + "%'" 
        if request.POST['protein_effect'] != '':
            protein_effect = request.POST['protein_effect']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['protein_effect'] + "%'"
        if request.POST['cds_effect'] != '':
            cds_effect = request.POST['cds_effect']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['cds_effect'] + "%'"        
        if request.POST['allele_fraction'] != '':
            allele_fraction = request.POST['allele_fraction']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['allele_fraction'] + "%'" 
        if request.POST['functional_effect'] != '':
            functional_effect = request.POST['functional_effect']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['functional_effect'] + "%'" 
        #print(consentsql)
        cur.execute(consentsql)
        rows = cur.fetchall()
        '''
        datalistsql = "SELECT id, \"ReportNo\",\"MPNo\", \
            resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' as \"MRN\", \
                resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' as \"short variants\" \
                    FROM public.reportxml where true "
        #if request.POST['ReportNo'] != '':
        #    datalistsql = datalistsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\''
        #if request.POST['MPNo'] != '':
        #    datalistsql = datalistsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\''
        #if request.POST['MRN'] != '':
        #    datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%'"
        
        if request.POST['gene'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['gene'] + "%'" 
        if request.POST['protein_effect'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['protein_effect'] + "%'"
        if request.POST['cds_effect'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['cds_effect'] + "%'"        
        if request.POST['allele_fraction'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['allele_fraction'] + "%'" 
        if request.POST['functional_effect'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'short_variants' ->> 'short_variant' LIKE '%" + request.POST['functional_effect'] + "%'" 
        #print(datalistsql)   
        cur.execute(datalistsql)
        datalist = cur.fetchall()
        df = pd.DataFrame(datalist)

        column_list = ["Id", "報告號碼", "分生號碼", "病歷號", "short variants"]  
        df.columns=column_list
        df.to_csv('static/doc/datalist.csv', encoding='utf-8-sig' ,index=False)
        '''
        SELECTint=len(rows)
        conn.close()
        search={#'ReportNo' : ReportNo,
                #'MPNo' : MPNo,
                #'MRN' : MRN,
                'gene':gene,
                'protein_effect':protein_effect,
                'cds_effect':cds_effect,
                'allele_fraction':allele_fraction,
                'functional_effect':functional_effect
                } 
        context = {
                'Generight' : Generight,
                'search' : search,
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'ShortVariants.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'ShortVariants.html', context)

def CopyNumberAlterations(request):
    #ReportNo=''
    #MPNo=''
    #MRN=''
    gene=''
    type=''
    copy_number=''
    user = request.user
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml where true '       
        #if request.POST['ReportNo'] != '':
        #    ReportNo = request.POST['ReportNo']
        #    consentsql = consentsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\' '
        #if request.POST['MPNo'] != '':
        #    MPNo = request.POST['MPNo']
        #    consentsql = consentsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\' '
        #if request.POST['MRN'] != '':
        #    MRN = request.POST['MRN']
        #    consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%'"
        
        if request.POST['gene'] != '':
            gene = request.POST['gene']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'copy_number_alterations' ->> 'copy_number_alteration' LIKE '%" + request.POST['gene'] + "%'"
        if request.POST['type'] != '':
            type = request.POST['type']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'copy_number_alterations' ->> 'copy_number_alteration' LIKE '%" + request.POST['type'] + "%'"
        if request.POST['copy_number'] != '':
            copy_number = request.POST['copy_number']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'copy_number_alterations' ->> 'copy_number_alteration' LIKE '%" + request.POST['copy_number'] + "%'"
        #print(consentsql)
        cur.execute(consentsql)
        rows = cur.fetchall()
        '''
        datalistsql = "SELECT id, \"ReportNo\",\"MPNo\", \
            resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' as \"MRN\", \
                resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'copy_number_alterations' ->> 'copy_number_alteration' as \"copy number alterations\" \
                    FROM public.reportxml where true "
        #if request.POST['ReportNo'] != '':
        #    datalistsql = datalistsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\''
        #if request.POST['MPNo'] != '':
        #    datalistsql = datalistsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\''
        #if request.POST['MRN'] != '':
        #    datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%'"
        
        if request.POST['gene'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'copy_number_alterations' ->> 'copy_number_alteration' LIKE '%" + request.POST['gene'] + "%'"
        if request.POST['type'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'copy_number_alterations' ->> 'copy_number_alteration' LIKE '%" + request.POST['type'] + "%'"
        if request.POST['copy_number'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'copy_number_alterations' ->> 'copy_number_alteration' LIKE '%" + request.POST['copy_number'] + "%'"
            
        cur.execute(datalistsql)
        datalist = cur.fetchall()
        df = pd.DataFrame(datalist)
        
        column_list = ["Id", "報告號碼", "分生號碼", "病歷號", "copy number alterations"]  
        df.columns=column_list
        df.to_csv('static/doc/datalist.csv', encoding='utf-8-sig' ,index=False)
        '''
        SELECTint=len(rows)
        conn.close()
        search={#'ReportNo' : ReportNo,
                #'MPNo' : MPNo,
                #'MRN' : MRN,
                'gene':gene,
                'type':type,
                'copy_number':copy_number,
                } 
        context = {
                'Generight' : Generight,
                'search' : search,
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'CopyNumberAlterations.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'CopyNumberAlterations.html', context)

def Rearrangement(request):
    #ReportNo=''
    #MPNo=''
    #MRN=''
    description=''
    targeted_gene=''
    other_gene=''
    user = request.user
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml where true '       
        #if request.POST['ReportNo'] != '':
        #    ReportNo = request.POST['ReportNo']
        #    consentsql = consentsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\' '
        #if request.POST['MPNo'] != '':
        #    MPNo = request.POST['MPNo']
        #    consentsql = consentsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\' '
        #if request.POST['MRN'] != '':
        #    MRN = request.POST['MRN']
        #    consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%'"

        if request.POST['description'] != '':
            description = request.POST['description']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'rearrangements' ->> 'rearrangement' LIKE '%" + request.POST['description'] + "%'"
        if request.POST['targeted_gene'] != '':
            targeted_gene = request.POST['targeted_gene']
            consentsql = consentsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'rearrangements' ->> 'rearrangement' LIKE '%" + request.POST['targeted_gene'] + "%'"
        if request.POST['other_gene'] != '':
            other_gene = request.POST['other_gene']
            consentsql = consentsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'rearrangements' ->> 'rearrangement' LIKE '%" + request.POST['other_gene'] + "%'"
        
        cur.execute(consentsql)
        rows = cur.fetchall()
        '''
        datalistsql = "SELECT id, \"ReportNo\",\"MPNo\", \
            resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' as \"MRN\", \
                resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'rearrangements' ->> 'rearrangement' as \"rearrangements\" \
                    FROM public.reportxml where true "
        #if request.POST['ReportNo'] != '':
        #    datalistsql = datalistsql + ' and "ReportNo" = \'' + request.POST['ReportNo'] + '\''
        #if request.POST['MPNo'] != '':
        #    datalistsql = datalistsql + ' and "MPNo" = \'' + request.POST['MPNo'] + '\''
        #if request.POST['MRN'] != '':
        #    datalistsql = datalistsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%'"
        
        if request.POST['description'] != '':
            datalistsql = datalistsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'rearrangements' ->> 'rearrangement' LIKE '%" + request.POST['description'] + "%'"
        if request.POST['targeted_gene'] != '':
            datalistsql = datalistsql + " and resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'rearrangements' ->> 'rearrangement' LIKE '%" + request.POST['targeted_gene'] + "%'"
        if request.POST['other_gene'] != '':
            datalistsql = datalistsql + " and  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'variant_report' -> 'rearrangements' ->> 'rearrangement' LIKE '%" + request.POST['other_gene'] + "%'"
            
        cur.execute(datalistsql)
        datalist = cur.fetchall()
        df = pd.DataFrame(datalist)
        #print(consentsql)
        column_list = ["Id", "報告號碼", "分生號碼", "病歷號", "rearrangements"]  
        df.columns=column_list
        df.to_csv('static/doc/datalist.csv', encoding='utf-8-sig' ,index=False)        
        '''
        SELECTint=len(rows)
        conn.close()
        search={#'ReportNo' : ReportNo,
                #'MPNo' : MPNo,
                #'MRN' : MRN,
                'description':description,
                'targeted_gene':targeted_gene,
                'other_gene':other_gene,
                } 
        context = {
                'Generight' : Generight,
                'search' : search,
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'Rearrangement.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'Rearrangement.html', context)
    
def GeneFinalReportDetails(request):
    user = request.user
    #print(user.username)
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    #print(Generight) 
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #print(right)  
    try:
        rid=request.GET['id']
        #print(rid)
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml WHERE id = \'' + rid + '\';'
        #print(consentsql)
        cur.execute(consentsql)
        rows = cur.fetchall()
        conn.close()
        #print(rows)
        context = {
                'right' : right,
                'Generight' : Generight,
                'FuncResult' : rid,
                'data' : rows[0]
                }             
        return render(request, 'GeneFinalReportDetails.html', context)
    except:
        context = {
                'right' : right, 
                'Generight' : Generight,
                'FuncResult' : '查無資料'
            } 
        return render(request, 'GeneFinalReportDetails.html', context)

def GeneVariantReportDetails(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #print(right)       
    try:
        rid=request.GET['id']
        #print(rid)
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml WHERE id = \'' + rid + '\';'
        #print(consentsql)
        cur.execute(consentsql)
        rows = cur.fetchall()
        conn.close()
        #print(rows)
        context = {
                'right' : right,
                'FuncResult' : rid,
                'data' : rows[0]
                }             
        return render(request, 'GeneVariantReportDetails.html', context)
    except:
        context = {
                'right' : right,                
                'FuncResult' : '查無資料'
            } 
        return render(request, 'GeneVariantReportDetails.html', context)
    
def ambulance(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:        
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'ambulance.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'ambulance.html', context)

def Phenopacket(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.PhenopacketCURD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data,
                'phenotypic_features_count' : len(data['phenotypic_features']),
                'measurements_count' : len(data['measurements']),
                'biosamples_count' : len(data['biosamples']),
                'genomic_interpretations_count' : len(data['interpretations'][0]['diagnosis']['genomic_interpretations'])
                }             
        return render(request, 'Phenopacket.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Phenopacket.html', context)

def Biosample(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)

    try:
        
        Result,data = Function.BiosampleCURD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Biosample.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Biosample.html', context)
    
def Individual(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)

    try:
        
        Result,data = Function.IndividualCURD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Individual.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Individual.html', context)

def Interpretation(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        
        Result,data = Function.InterpretationCURD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Interpretation.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Interpretation.html', context)

def ClinvarVariant(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        
        Result,data = Function.ClinvarVariantCURD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'ClinvarVariant.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'ClinvarVariant.html', context)

def Patient(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    fhirip=models.fhirip.objects.all()
    #print(fhirip)
    try:
        
        Result,data = Function.PatientCURD(request)
        context = {
                'right' : right,
                'fhirip' : fhirip,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Patient.html', context)
    except:
        context = {
                'right' : right,
                'fhirip' : fhirip,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Patient.html', context)

def Organization(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.OrganizationCURD(request)

        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Organization.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Organization.html', context)

def Practitioner(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.PractitionerCURD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Practitioner.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Practitioner.html', context)
        
def PatientUpload(request):
    user = request.user
    #print(user.username)
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #df = pd.read_excel(uploadedFile)
    #print(method)
    try:
        try:
            inlineRadioOptions = request.POST["inlineRadioOptions"]
        except:
            inlineRadioOptions = ''
        
        if request.POST["fileTitle"] !='':
            fileTitle = request.POST["fileTitle"]
        else:
            fileTitle = '' 
       
        try:
            uploadedFile = request.FILES["uploadedFile"]
        except:
            uploadedFile = ''
        '''    
        if request.POST["ReportNo"] !='':
            ReportNo = request.POST["ReportNo"]
        else:
            ReportNo = ''
            
        if request.POST["MPNo"] !='':
            MPNo = request.POST["MPNo"]
        else:
            MPNo = ''
       
        if request.POST["FullName"] !='':
            FullName = request.POST["FullName"]
        else: 
            FullName = ''
           
        if request.POST["MRN"] !='':
            MRN = request.POST["MRN"]
        else:
            MRN = ''
          
        if request.POST["SpecFormat"] !='':
            SpecFormat = request.POST["SpecFormat"]
        else:
            SpecFormat = ''
       
        if request.POST["BlockId"] !='':
            BlockId = request.POST["BlockId"]
        else:
            BlockId = ''
      
        if request.POST["purity"] !='':
            purity = request.POST["purity"]
        else:
            purity = ''
          
        if request.POST["Tumortype"] !='':
            Tumortype = request.POST["Tumortype"]
        else:
            Tumortype = ''
      
        if request.POST["SubmittedDiagnosis"] !='':
            SubmittedDiagnosis = request.POST["SubmittedDiagnosis"]
        else:
            SubmittedDiagnosis = ''

        if request.POST["TestType"] !='':
            TestType = request.POST["TestType"]
        else:
            TestType = ''        
     
        if request.POST["OrderingMD"] !='':
            OrderingMD = request.POST["OrderingMD"]
        else:
            OrderingMD = ''
      
        if request.POST["Pathologist"] !='':
            Pathologist = request.POST["Pathologist"]
        else:
            Pathologist = ''
      
        if request.POST["ReceivedDate"] !='':
            ReceivedDate = request.POST["ReceivedDate"]
        else:
            ReceivedDate = ''

        print(inlineRadioOptions,
              fileTitle,              
              uploadedFile
              )
        ,
        ReportNo,
        MPNo,
        FullName,
        MRN,
        SpecFormat,
        BlockId,
        purity,
        Tumortype,
        SubmittedDiagnosis,
        TestType,
        OrderingMD,
        Pathologist,
        ReceivedDate
        '''
                
        # Saving the information in the database

        Genedata = models.Genedata(
            inlineRadioOptions=inlineRadioOptions,
            fileTitle = fileTitle,
            uploadedFile = uploadedFile
        )
        '''
        ReportNo = ReportNo,
        MPNo = MPNo,
        FullName = FullName,
        MRN = MRN,
        SpecFormat = SpecFormat,
        BlockId = BlockId,
        purity=purity,
        Tumortype=Tumortype,
        SubmittedDiagnosis=SubmittedDiagnosis,
        TestType=TestType,
        OrderingMD = OrderingMD,
        Pathologist=Pathologist,
        ReceivedDate=ReceivedDate
        '''
        Genedata.save()        
        #documents = models.Document.objects.all()        
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Up finsh'
#                'FuncResult' : Result,
#                'data' : data,
                }
        return render(request, 'PatientUpload.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Up Fail'
                }
        return render(request, 'PatientUpload.html' , context)

def Userright(request):
    user = request.user
    #print(user.username)
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #df = pd.read_excel(uploadedFile)
    #print(method)
    try:
        if request.POST["fileTitle"] !='':
            fileTitle = request.POST["fileTitle"]
        else:
            fileTitle = '' 
        try:
            uploadedFile = request.FILES["uploadedFile"]
        except:
            uploadedFile = ''
        # Saving the information in the database
        Userright = models.Userright(
            fileTitle = fileTitle,
            uploadedFile = uploadedFile,
        )
        
        Userright.save()        
        #documents = models.Document.objects.all()        
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Up finsh'
                }
        return render(request, 'UsrUpload.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'FuncResult' : 'Up Fail'
                }
        return render(request, 'UsrUpload.html' , context)
    
def UpdateMeta(request):
    user = request.user
    #print(user.username)
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    Metaxlsxall=models.Metaxlsx.objects.all().order_by('-id')
    #df = pd.read_excel(uploadedFile)
    #print(method)
    
    try:
        if request.POST["fileTitle"] !='' and request.FILES["uploadedFile"]!='':
            if request.POST["fileTitle"] !='':
                fileTitle = request.POST["fileTitle"]
            else:
                fileTitle = '' 
            try:
                uploadedFile = request.FILES["uploadedFile"]
            except:
                uploadedFile = ''
            # Saving the information in the database
            Metaxlsx = models.Metaxlsx(
                fileTitle = fileTitle,
                uploadedFile = uploadedFile,
            )            
            Metaxlsx.save()        
            #documents = models.Document.objects.all()        
        context = {
                'Generight' : Generight,
                'right' : right,
                'Metaxlsx' : Metaxlsxall,
                'FuncResult' : 'Upload finsh'
                }
        return render(request, 'MetaUpload.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'Metaxlsx' : Metaxlsxall,
                'FuncResult' : 'No file upload'
                }
        return render(request, 'MetaUpload.html' , context)
    
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
    


def Metaxlsx(request):
    user = request.user
    #print(user.username)
    Generight=models.Genepermission.objects.filter(user__username__startswith=user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    
    try:
        rid=request.GET["id"]
        #print(rid)
        Metaxlsx=models.Metaxlsx.objects.filter(id=rid)
        for meta in Metaxlsx:
            #print(meta.uploadedFile)
            #for dirname in os.listdir(os.getcwd()+'/media/'):
                #print(dirname)
            dfpath=os.getcwd().replace('\\','/')+'/media/'+str(meta.uploadedFile)
            #dfpath='/media/'+str(meta.uploadedFile)
            #print(dfpath)

            conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port=genepostgresport)
            #print('Opened database successfully')
            cur = conn.cursor()
            
            df = pd.read_excel(dfpath)
            #print(df)
            df = df.assign(update='')
            #print("Columns")
            #print(df.columns)
            for i in range(len(df)):
                #if i % 10 ==0:11111
                    #print(i)
                    #print(df['分生號碼'][i] + ' ' + df['報告號碼'][i])
                try:
                    ReportNo=df['報告號碼'][i]
                    MPNo=df['分生號碼'][i]
                    query= "SELECT id, resultsreport, \"ReportNo\", \"MPNo\" FROM public.reportxml where \"ReportNo\" = '"+df['報告號碼'][i]+"' and \"MPNo\" = '"+df['分生號碼'][i]+"';"
                    df1 = pd.read_sql(query, conn)
                    for j in range(len(df1)):
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['PMI']['ReportId']=str(df['報告號碼'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['PMI']['MRN']=str(df['病歷號'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['PMI']['FullName']=str(df['病患姓名'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['PMI']['SubmittedDiagnosis']=str(df['Diagnosis'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['PMI']['OrderingMD']=str(df['臨床主治醫師'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['PMI']['Pathologist']=str(df['病理醫師'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['PMI']['ReceivedDate']=str(df['報告日期'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['PMI']['TumorType']=str(df['Tumor type'][i])
                            
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['Sample']['BlockId']=str(df['蠟塊號'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['Sample']['TestType']=str(df['檢測項目'][i])
                            df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['Sample']['SpecFormat']=str(df['檢體別'][i])
                            #if not np.isnan(df['Tumor purity %'][i]):
                            try:
                                df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['Sample']['TumorPurity']=int(df['Tumor purity %'][i].replace('%',''))                                
                            except:
                                print(reportNo=df['報告號碼'][i])
                                print(df['Tumor purity %'][i])
                                df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['Sample']['TumorPurity']='NA'
                            if not np.isnan(df['標本組織部位來源'][i]):
                                df1['resultsreport'][j]['ResultsReport']['ResultsPayload']['FinalReport']['Sample']['SpecimenLocation']=str(df['標本組織部位來源'][i])
                            sql='UPDATE public.reportxml SET resultsreport = \'' + json.dumps(df1['resultsreport'][j], cls=NpEncoder) + '\' WHERE id = ' + str(df1['id'][j]) +';'
                            #if i ==1:
                            datajson=json.dumps(df1['resultsreport'][j], cls=NpEncoder)
                            #print(type(datajson))
                            with open('media/json/'+ReportNo+'_('+MPNo+').json', 'w') as f:
                                f.write(datajson)
                            #print(sql)
                            cur.execute(sql)
                            #print(cur.rowcount)
                            if cur.rowcount > -1:
                                df['update'][i]='OK'
                            conn.commit()
                except:
                    df['update'][i]='NG'
            df.to_excel(dfpath,index=False)
            try:
                import paramiko
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                target_host = '172.174.201.121'
                #target_port = 22
                pwd = 'sdfWER234SDF'
                un = 'sdfWER234'
                ssh.connect( hostname = target_host , username = un, password = pwd )
                stdin, stdout, stderr = ssh.exec_command('bash automate_etl_process.sh')
                with open("stdout.txt", "w") as text_file:
                    text_file.write(stdout.read())
                #print("STDOUT:\n%s\n\nSTDERR:\n%s\n" %( stdout.read(), stderr.read() )) 
                ssh.close()
                #print(os.path.abspath(os.getcwd()))
            except:
                None
        context = {
                'Generight' : Generight,
                'right' : right,
                'Metaxlsx' : Metaxlsx,
                'FuncResult' : 'Updata finsh'
                }
        return render(request, 'Update.html', context)
    except:
        context = {
                'Generight' : Generight,
                'right' : right,
                'Metaxlsx' : '',
                'FuncResult' : 'Updata Fail'
                }
        return render(request, 'Update.html' , context)

def DataUpload(request):
    try:
        if request.method == "POST":
            method=request.POST['method']
            fileTitle = request.POST["fileTitle"]
            uploadedFile = request.FILES["uploadedFile"]
            df = pd.read_excel(uploadedFile)
            document = models.Document(
                title = fileTitle,
                uploadedFile = uploadedFile
            )
            document.save()
        status_codelist=[]
        diagnosticslist=[]
        for i in range(len(df)):
            try:
                Result,data,status_code,diagnostics = Function.PatientUpload(df.iloc[i],method)
                status_codelist.append(status_code)
                diagnosticslist.append(diagnostics)
                context = {
                        'FuncResult' : Result,
                        'data' : data,
                        }
            except:
                context = {
                        'FuncResult' : 'Function'
                        } 
        errordict = {
            "status_code": status_codelist,
            "diagnosticslist": diagnosticslist
            }
        errordf = pd.DataFrame(errordict)
        data=df.merge(errordf, how='outer', left_index=True, right_index=True)
        context = {
                'FuncResult' : Result,
                'data' : data,
                }
        return render(request, 'DataUpload.html', context)
    except:
        context = {
                'FuncResult' : 'FuncResult'
                }
        return render(request, 'DataUpload.html', context )

def AllergyIntolerance(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.AllergyIntoleranceCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'AllergyIntolerance.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'AllergyIntolerance.html', context)

def FamilyMemberHistory(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.FamilyMemberHistoryCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'FamilyMemberHistory.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'FamilyMemberHistory.html', context)

def Encounter(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.EncounterCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Encounter.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Encounter.html', context)
    
def CarePlan(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.CarePlanCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'CarePlan.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'CarePlan.html', context)

def DiagnosticReportNursing(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.DiagnosticReportNursingCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'DiagnosticReportNursing.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'DiagnosticReportNursing.html', context)

def DiagnosticReportRadiationTreatment(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.DiagnosticReportRadiationTreatmentCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'DiagnosticReportRadiationTreatment.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'DiagnosticReportRadiationTreatment.html', context)
    
def DiagnosticReportPathologyReport(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.DiagnosticReportPathologyReportCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'DiagnosticReportPathologyReport.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'DiagnosticReportPathologyReport.html', context)

def Procedure(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.ProcedureCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Procedure.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Procedure.html', context)
    
def ServiceRequest(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.ServiceRequestCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'ServiceRequest.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'ServiceRequest.html', context)
    
def ConditionStage(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.ConditionStageCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'ConditionStage.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'ConditionStage.html', context)

def ImagingStudy(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.ImagingStudyCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'ImagingStudy.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'ImagingStudy.html', context)

def Endpoint(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.EndpointCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Endpoint.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Endpoint.html', context)

def Medication(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.MedicationCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Medication.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Medication.html', context)

def MedicationRequest(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.MedicationRequestCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'MedicationRequest.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'MedicationRequest.html', context)    

def MedicationAdministration(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.MedicationAdministrationCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'MedicationAdministration.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'MedicationAdministration.html', context)

def Immunization(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.ImmunizationCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Immunization.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                } 
        return render(request, 'Immunization.html', context)
    
def dbSNP(request):
    try:
        if 'Alleles' in request.POST:
            Alleles = request.POST['Alleles']
            dbSNP = request.POST['dbSNP']
            #print(Alleles)
            context=Function.post_dbSNP(Alleles,dbSNP)
            #print(context)
        elif 'Alleles' in request.GET:
            Alleles = request.GET['Alleles']
            dbSNP = request.GET['dbSNP']
            #print(Alleles)
            context=Function.post_dbSNP(Alleles,dbSNP)
        else:
            context=None
        return render(request, 'geneticsdbSNP.html', context)
    except:
        return render(request, 'geneticsdbSNP.html', context)

def getRisk(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)    
    try:
        riskrlue = request.GET['risk']
        #riskrlue='Alc_risk'
        #print(riskrlue)

        risksdf=riskdf[riskdf['risk']==riskrlue]
        #print(risksdf)
        #risksdict = risksdf.to_dict()
        risksdict = risksdf.to_dict('records')
        context = {
                'right' : right,
                'riskrlue' : riskrlue,
                'risks' : risksdict
                }
        return render(request,'geneticsRisk.html', context)
    except:
        return render(request,'geneticsRisk.html', context)

def Gene(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.GeneCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'geneticsVghtc.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
            } 
        return render(request, 'geneticsVghtc.html', context)

def MolecularSequence(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.MolecularSequenceCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'MolecularSequence.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
            } 
        return render(request, 'MolecularSequence.html', context)

def ObservationGenetics(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.ObservationGeneticsCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'ObservationGenetics.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
            } 
        return render(request, 'ObservationGenetics.html', context)

def ObservationImaging(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data = Function.ObservationImagingCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'ObservationImaging.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
            } 
        return render(request, 'ObservationImaging.html', context)

def Referral(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        Result,data,prtj,ohrtj,ihrtj,crtj,odrtj,idrtj = Function.ReferralCRUD(request)
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data,
                'prtj' : prtj,
                'ohrtj' : ohrtj,
                'ihrtj' : ihrtj,
                'crtj' : crtj,
                'odrtj' : odrtj,
                'idrtj' : idrtj
                }             
        return render(request, 'Referral.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
            } 
        return render(request, 'Referral.html', context)

def patient_medical_records(request):
    
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #print(right)   
    fhirip=models.fhirip.objects.all()
    try:
        Result,data = Function.patient_medical_recordsCRUD(request)
        context = {
                'fhirip' : fhirip,
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'patient_medical_records.html', context)
    except:
        context = {
                'right' : right,
                'fhirip' : fhirip,
                'FuncResult' : '查無資料'
            } 
        return render(request, 'patient_medical_records.html', context)
@csrf_exempt    
def DischargeSummaryDetails(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #print(right)
    fhirip=models.fhirip.objects.all()
    try:
        fhiripSelect=request.GET['fhir']
    except:
        fhiripSelect=''
    try:
        DischargeSummaryId=request.GET['id']
    except:
        DischargeSummaryId=''
    #print(fhiripSelect)
    #print(DischargeSummaryId)
    #print(fhiripSelect+'Composition/'+DischargeSummaryId)
        
    try:
        url = fhiripSelect+'Composition/'+DischargeSummaryId
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        resultjson=json.loads(response.text)
        #print(resultjson)
        context = {
                'fhiripSelect' : fhiripSelect,
                'fhirip' : fhirip,
                'right' : right,
                'FuncResult' : DischargeSummaryId,
                'data' : resultjson
                }             
        return render(request, 'DischargeSummaryDetails.html', context)
    except:
        context = {
                'fhiripSelect' : fhiripSelect,
                'fhirip' : fhirip,
                'right' : right,                
                'FuncResult' : '查無資料'
            } 
        return render(request, 'DischargeSummaryDetails.html', context)

@csrf_exempt    
def tpoorf(request):
    Verificationurl='https://tproof-dev.twcc.ai/api/v1/tproof/forensics'
    Verification={
      "apikey": "",
      "tokenId": ""
    }    
    headers = {'Content-Type': 'application/json'}
    try:
        tpoorf=request.GET['chain']
        tpoorflist=tpoorf.split(",")
        apikey=tpoorflist[0]
        tokenId=tpoorflist[1]
        Verification['apikey']=apikey
        Verification['tokenId']=tokenId
        payload = json.dumps(Verification)
        #print(payload)
        response = requests.request("POST", Verificationurl, headers=headers, data=payload)
        resultjson=json.loads(response.text)
        #print(response.text)
        context = {
            'data' : resultjson,
            }
        return render(request, 'tpoorf.html', context)
    except:
        context = {} 
        return render(request, 'tpoorf.html', context)

def working(request):
    html = '<h1> working </h1>'
    return HttpResponse(html, status=200)

@csrf_exempt    
def logging(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
  
    try:
        method=request.POST['method']
    except:
        method=''
    try:
        formip=request.POST['formip']
    except:
        formip=''
    try:
        operationdate=request.POST['operationdate']
    except:
        operationdate=''    
    #print(formip,method,operationdate)
    
    conn = psycopg2.connect(database="consent", user="postgres", password="1qaz@WSX3edc", host=postgresip, port="5432")
    cur = conn.cursor()  
    sqlstring =  "SELECT * FROM public.log WHERE method = '" + method + "'"
    if formip != '':
        sqlstring = sqlstring + " AND ip_addr = '" + formip + "'"
    if operationdate != '':
        sqlstring = sqlstring + " AND datetime::date = '" + operationdate + "'"
    sqlstring=sqlstring + " ORDER BY datetime DESC limit 2000;"
    cur.execute(sqlstring)
    rows = cur.fetchall()
    #for row in rows:
        #print(row)
    conn.close()
    context = {
        'right' : right,
        'data' : rows,
        'method' : method,
        'formip' : formip,
        'operationdate' : operationdate
        }                 
    return render(request, 'logging.html', context)

@csrf_exempt    
def DischargeSummary(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #print(right)
    fhirip=models.fhirip.objects.all()
    try:
        fhiripSelect=request.POST['fhirip']
    except:
        fhiripSelect=''
    try:
        Result,data = Function.DischargeSummaryCRUD(request)
        context = {
                'fhiripSelect' : fhiripSelect,
                'fhirip' : fhirip,
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'DischargeSummary.html', context)
    except:
        context = {
                'fhiripSelect' : fhiripSelect,
                'fhirip' : fhirip,
                'right' : right,                
                'FuncResult' : '查無資料'
            } 
        return render(request, 'DischargeSummary.html', context)
    
@csrf_exempt
def VisitNote(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #print(right)
    fhirip=models.fhirip.objects.all()
    try:
        fhiripSelect=request.POST['fhirip']
    except:
        fhiripSelect=''
    try:
        Result,data = Function.VisitNoteCRUD(request)
        context = {
                'fhiripSelect' : fhiripSelect,
                'fhirip' : fhirip,
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'VisitNote.html', context)
    except:
        context = {
                'fhiripSelect' : fhiripSelect,
                'fhirip' : fhirip,
                'right' : right,                
                'FuncResult' : '查無資料'
            } 
        return render(request, 'VisitNote.html', context)

@csrf_exempt
def Consent(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #print(right)
    fhirip=models.fhirip.objects.all()
    try:
        fhiripSelect=request.POST['fhirip']
    except:
        fhiripSelect=''
    try:
        Result,data = Function.ConsentCRUD(request)
        context = {
                'fhiripSelect' : fhiripSelect,
                'fhirip' : fhirip,
                'right' : right,
                'FuncResult' : Result,
                'data' : data
                }             
        return render(request, 'Consent.html', context)
    except:
        context = {
                'fhiripSelect' : fhiripSelect,
                'fhirip' : fhirip,
                'right' : right,                
                'FuncResult' : '查無資料'
            } 
        return render(request, 'Consent.html', context)