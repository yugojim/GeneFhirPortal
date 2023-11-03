from django.shortcuts import render#, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden#, HttpResponseRedirect
#from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage \
    #,VideoSendMessage, AudioSendMessage, LocationSendMessage, StickerSendMessage\
        #, ButtonsTemplate, TemplateSendMessage, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
from datetime import datetime

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

DocumentPath = str(pathlib.Path().absolute()) + "/static/doc/"
risk = DocumentPath + 'risk.csv'
riskdf = pd.read_csv(risk, encoding='utf8')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fhir = 'http://192.168.211.9:8080/fhir/'#4600VM
postgresip = "192.168.211.19"
genepostgresip = "104.208.68.39"

jsonPath=str(pathlib.Path().absolute()) + "/static/template/Observation-Imaging-EKG.json"
ObservationImagingEKGJson = json.load(open(jsonPath,encoding="utf-8"))
 
@csrf_exempt 
def index(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'index.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'index.html', context)
    
def GeneReport(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port="8081")
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml '
        #consentsql = 'SELECT * FROM public.reportxml WHERE "ReportNo" = \'M111-10001\''

        if request.POST['ReportNo'] != '':
            consentsql = consentsql + 'WHERE "ReportNo" = \'' + request.POST['ReportNo'] + '\''
        elif request.POST['MPNo'] != '':
            consentsql = consentsql + 'WHERE "MPNo" = \'' + request.POST['MPNo'] + '\''
        elif request.POST['MRN'] != '':
            consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['MRN'] + "%';"
        #elif request.POST['PatientName'] != '':
        #    consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'FullName' LIKE '%" + request.POST['PatientName'] + "%';"
        #elif request.POST['OrderingMD'] != '':
        #    consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'OrderingMD' LIKE '%" + request.POST['OrderingMD'] + "%';"
        #elif request.POST['Diagnosis'] != '':
        #    consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'SubmittedDiagnosis' LIKE '%" + request.POST['Diagnosis'] + "%';"
        else:
            consentsql = consentsql + ' LIMIT 200;'
        
        cur.execute(consentsql)
        rows = cur.fetchall()
        #print(type(rows))
        #datadict=dict(zip(rows))
        #with open('datalist.csv', 'w', newline='') as f:
        df = pd.DataFrame(rows)
        #print(consentsql)
        df.to_csv('static/doc/datalist.csv', sep='\t', encoding='utf-8')
        #with open("studentgrades.csv", "w", newline="") as file:
        #    writer = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=";")
        #    writer.writerows(rows)     
        #print(len(rows))
        SELECTint=len(rows)
        conn.close()
        context = {
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'GeneReport.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'GeneReport.html', context)

def PMI(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port="8081")
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml '        

        if request.POST['Diagnosis'] != '':
            consentsql = consentsql + 'WHERE "ReportNo" = \'' + request.POST['Diagnosis'] + '\''
        elif request.POST['TestType'] != '':
            consentsql = consentsql + 'WHERE "MPNo" = \'' + request.POST['TestType'] + '\''
        elif request.POST['OrderingMD'] != '':
            consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['OrderingMD'] + "%';"
        else:
            consentsql = consentsql + ' LIMIT 200;'
        
        cur.execute(consentsql)
        rows = cur.fetchall()
        df = pd.DataFrame(rows)
        #print(consentsql)
        df.to_csv('static/doc/datalist.csv', sep='\t', encoding='utf-8')
        SELECTint=len(rows)
        conn.close()
        context = {
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'PMI.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'PMI.html', context)

def Biomarker(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port="8081")
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml '       

        if request.POST['status'] != '':
            consentsql = consentsql + 'WHERE "ReportNo" = \'' + request.POST['status'] + '\''
        elif request.POST['score'] != '':
            consentsql = consentsql + 'WHERE "MPNo" = \'' + request.POST['score'] + '\''
        else:
            consentsql = consentsql + ' LIMIT 200;'
        
        cur.execute(consentsql)
        rows = cur.fetchall()
        df = pd.DataFrame(rows)
        #print(consentsql)
        df.to_csv('static/doc/datalist.csv', sep='\t', encoding='utf-8')
        SELECTint=len(rows)
        conn.close()
        context = {
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'Biomarker.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'Biomarker.html', context)
    
def ShortVariants(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port="8081")
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml '        

        if request.POST['gene'] != '':
            consentsql = consentsql + 'WHERE "ReportNo" = \'' + request.POST['gene'] + '\''
        elif request.POST['Protein_change'] != '':
            consentsql = consentsql + 'WHERE "MPNo" = \'' + request.POST['Protein_change'] + '\''
        elif request.POST['cds_effect'] != '':
            consentsql = consentsql + 'WHERE "MPNo" = \'' + request.POST['cds_effect'] + '\''
        elif request.POST['functional_effect'] != '':
            consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['functional_effect'] + "%';"
        else:
            consentsql = consentsql + ' LIMIT 200;'
        
        cur.execute(consentsql)
        rows = cur.fetchall()
        df = pd.DataFrame(rows)
        #print(consentsql)
        df.to_csv('static/doc/datalist.csv', sep='\t', encoding='utf-8')
        SELECTint=len(rows)
        conn.close()
        context = {
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'ShortVariants.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'ShortVariants.html', context)

def CopyNumberAlterations(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port="8081")
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml '        

        if request.POST['gene'] != '':
            consentsql = consentsql + 'WHERE "ReportNo" = \'' + request.POST['gene'] + '\''
        elif request.POST['type'] != '':
            consentsql = consentsql + 'WHERE "MPNo" = \'' + request.POST['type'] + '\''
        else:
            consentsql = consentsql + ' LIMIT 200;'
        
        cur.execute(consentsql)
        rows = cur.fetchall()
        df = pd.DataFrame(rows)
        #print(consentsql)
        df.to_csv('static/doc/datalist.csv', sep='\t', encoding='utf-8')
        SELECTint=len(rows)
        conn.close()
        context = {
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'CopyNumberAlterations.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'CopyNumberAlterations.html', context)

def Rearrangement(request):
    user = request.user
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    try:
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port="8081")
        cur = conn.cursor()
        consentsql = 'SELECT * FROM public.reportxml '        

        if request.POST['description'] != '':
            consentsql = consentsql + 'WHERE "ReportNo" = \'' + request.POST['description'] + '\''
        elif request.POST['targeted_gene'] != '':
            consentsql = consentsql + 'WHERE "MPNo" = \'' + request.POST['targeted_gene'] + '\''
        elif request.POST['other_gene'] != '':
            consentsql = consentsql + "WHERE  resultsreport -> 'ResultsReport' -> 'ResultsPayload' -> 'FinalReport' -> 'PMI' ->> 'MRN' LIKE '%" + request.POST['other_gene'] + "%';"
        else:
            consentsql = consentsql + ' LIMIT 200;'
        
        cur.execute(consentsql)
        rows = cur.fetchall()
        df = pd.DataFrame(rows)
        #print(consentsql)
        df.to_csv('static/doc/datalist.csv', sep='\t', encoding='utf-8')
        SELECTint=len(rows)
        conn.close()
        context = {
                'right' : right,
                'FuncResult' : SELECTint,
                'rows' : rows
                }
        return render(request, 'Rearrangement.html', context)
    except:
        context = {
                'right' : right,
                'FuncResult' : 'Function'
                }
        return render(request, 'Rearrangement.html', context)
    
def GeneFinalReportDetails(request):
    user = request.user
    #print(user.username)
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    #print(right)  
    try:
        rid=request.GET['id']
        #print(rid)
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port="8081")
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
        return render(request, 'GeneFinalReportDetails.html', context)
    except:
        context = {
                'right' : right,                
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
        conn = psycopg2.connect(database="vghtpegene", user="postgres", password="1qaz@WSX3edc", host=genepostgresip, port="8081")
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
    right=models.Permission.objects.filter(user__username__startswith=user.username)
    if request.method == "POST":
        # Fetching the form data
        method=request.POST['method']
        fileTitle = request.POST["fileTitle"]
        uploadedFile = request.FILES["uploadedFile"]
        #print(fileTitle,uploadedFile)
        df = pd.read_excel(uploadedFile)
        # Saving the information in the database
        document = models.Document(
            title = fileTitle,
            uploadedFile = uploadedFile
        )
        document.save()
    #documents = models.Document.objects.all()
    #print(method)
    status_codelist=[]
    diagnosticslist=[]
    try:
        for i in range(len(df)):
            #print(i)
            #print(df.iloc[i])              
            try:
                Result,data,status_code,diagnostics = Function.PatientUpload(df.iloc[i],method)
                status_codelist.append(status_code)
                diagnosticslist.append(diagnostics)
                context = {
                        'right' : right,
                        'FuncResult' : Result,
                        'data' : data,
                        }
                #print(statuscode)             
                #return render(request, 'PatientUpload.html', context)
            except:
                context = {
                        'right' : right,
                        'FuncResult' : 'Function'
                        } 
                #return render(request, 'PatientUpload.html', context)
        errordict = {
            'right' : right,
            "status_code": status_codelist,
            "diagnosticslist": diagnosticslist
            }
        errordf = pd.DataFrame(errordict)
        #print(type(errordf))
        #print(errordf)
        #print(df)
        data=df.merge(errordf, how='outer', left_index=True, right_index=True)
        #print(df.merge(errordf, how='outer', left_index=True, right_index=True))
        #print(pd.merge(df, errordf))
        context = {
                'right' : right,
                'FuncResult' : Result,
                'data' : data,
                }
        return render(request, 'PatientUpload.html', context)
    except:
        context = {
                'right' : right,
                'Projects' : 'Projects'
                }
        return render(request, 'PatientUpload.html' , context)

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