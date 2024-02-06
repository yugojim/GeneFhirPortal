import PyPDF2
import os
import glob
import xmltodict
import xml.etree.ElementTree as ET
import json
import psycopg2
import os
import shutil
import path
import re
import pandas as pd
import csv
import numpy as np
import warnings
warnings.filterwarnings('ignore')

### 新增XML 至SQL ###
def xmlisql(PdfPath,conn,cur):
    os.chdir(PdfPath)
    dirlist=glob.glob('*_*')
    for dirpath in dirlist:
        try:    
            ReportNo, MPNo = dirpath.replace('(', '').replace(')', '').split('_')
            filepathlist =glob.glob(os.path.join(dirpath, "*.xml"))
            #print(filepathlist)        
            for filename in filepathlist:
                #print(filename)
                #print(filename.split('\\')[1])
                #os.remove(filename)
                #try:
                with open(filename, encoding="utf-8") as fd:
                    exDict = xmltodict.parse(fd.read())            
                    sql='INSERT INTO public.reportxml(resultsreport,"ReportNo", "MPNo") VALUES (\'' + json.dumps(exDict).replace("'", " ").replace("rr:", "").replace(":rr", "").replace("@", "").replace(":xsi", "xsi").replace("xsi:", "xsi").replace(":xsd", "xsd").replace("xsd:", "xsd").replace("-", "_") + '\'' + ',\'' + ReportNo + '\'' + ',\'' + MPNo + '\'' + ');'
                    #print(sql)
                    cur.execute(sql)            
                    conn.commit()
                    #print(dirpath + ' INSERT')
                #except:
                    #print('no xml')
            #print(dirpath + ' OK')
        except:
            None
            #print(dirpath + ' NG')
    os.chdir('..')
    return 'xml2sql done'

### 更新XML 至SQL ###
def xml2sql(PdfPath,conn,cur):
    os.chdir(PdfPath)
    dirlist=glob.glob('*_*')
    for dirpath in dirlist:
        try:    
            ReportNo, MPNo = dirpath.replace('(', '').replace(')', '').split('_')
            filepathlist =glob.glob(os.path.join(dirpath, "*.xml"))
            #print(filepathlist)        
            for filename in filepathlist:
                #print(filename)
                #print(filename.split('\\')[1])
                #os.remove(filename)

                with open(filename, encoding="utf-8") as fd:
                    exDict = xmltodict.parse(fd.read()) 
                sql='UPDATE public.reportxml SET resultsreport = \'' + json.dumps(exDict).replace("'", " ").replace("rr:", "").replace(":rr", "").replace("@", "").replace(":xsi", "xsi").replace("xsi:", "xsi").replace(":xsd", "xsd").replace("xsd:", "xsd").replace("-", "_") + '\' \
                    where "ReportNo"= \'' + ReportNo + '\' and ' + '"MPNo"=\'' + MPNo + '\'' + ';'
                #print(sql)
                cur.execute(sql)  
                conn.commit()
                #print(cur.rowcount)
                print(dirpath + ' UPDATE')

            #print(dirpath + ' OK')
        except:
            print(dirpath + ' NG')
    os.chdir('..')
    return 'xml2sql done'

### Archer ###
def Archer2xml(PdfPath):
    os.chdir(PdfPath)
    dirlist=glob.glob('*_*')
    #print(len(dirlist))
    for dirpath in dirlist:
        try: 
            basedict={
                "rr:ResultsReport": {
                    "rr:ResultsPayload": {
                        "FinalReport":{
                            "Sample": {
                                "FM_Id": "",
                                "SampleId": "",
                                "BlockId": "",
                                "TRFNumber": "",
                                "TestType": "",
                                "SpecFormat": "",
                                "ReceivedDate": "",
                                },
                            "PMI" : {
                                "ReportId": "",
                                "MRN": "",
                                "FullName": "",
                                "FirstName": "",
                                "LastName": "",
                                "SubmittedDiagnosis": "",
                                "Gender": "",
                                "DOB": "",
                                "OrderingMD": "",
                                "OrderingMDId": "",
                                "Pathologist": "",
                                "CopiedPhysician1": "",
                                "MedFacilName": "",
                                "MedFacilID": "",
                                "SpecSite": "",
                                "CollDate": "",
                                "ReceivedDate": "",
                                "CountryOfOrigin": ""
                               }
                            },
                        "variant-report": {
                            "short_variants": {
                                "short_variant":[]
                                },
                            "copy_number_alterations": {
                                "copy_number_alteration": []
                                },
                            "rearrangements": {
                            	"rearrangement": []
                            },
                            "biomarkers": {
                                "microsatellite_instability": {
                                    "status": ""
                                },
                                "tumor_mutation_burden": {
                                    "score": ""
                                }
                            }                
                        }
                        }
                    }
            }
            ReportNo, MPNo  = dirpath.replace('(', '').replace(')', '').split('_')
            filepathlist =glob.glob(os.path.join(dirpath, "*).pdf"))
            #print(filepathlist)        
            for filename in filepathlist:
                #print(filename)
                reader = PyPDF2.PdfReader(filename)
                #text_file = open("Output.txt", "w", encoding="utf-8")
                text=[]
                for i in range(len(reader.pages)):
                    text.append(reader.pages[i].extract_text())
                    #text_file.write(reader.pages[i].extract_text())
                #text_file.close()
                short_variants = []            
                rearrangement = []
                biomarkers = []
                copy_number_alterations = []
                pmi = []           
                rearrangementlist=[]
                for i in range(len(text)):
                       
                    try:    
                        #rearrangement
                        if text[i].find('Reportable Isoforms') > -1: 
                            #print(text[i])
                            #print('rearrangement ' + str(i))
                            import re
                            test_string = text[i]
                            ans=re.findall('Fusion:.+\n',test_string)
                            for a in ans:                            
                                rearrangementlist.append({
                                    "description": a[8:],
                                    "other_gene": a[8:].replace(' ','').replace('\n','').split('®')[0],
                                    "targeted_gene": a[8:].replace(' ','').replace('\n','').split('®')[1]
                                    })
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['rearrangements']['rearrangement'] = rearrangementlist
                            #print(rearrangementlist)
                    except:
                        None
                with open(dirpath+'\\'+ReportNo+'_('+MPNo+'.xml', 'w', encoding="utf-8") as output:
                    output.write(xmltodict.unparse(basedict, pretty=True))            
                #print(dirpath + ' OK')
        except:
            None#print(dirpath + ' NG')
   
    os.chdir('..')
    return 'Archer2xml done'

### BRCA Assay meta###
def BRCAAssay2xml(PdfPath):
    os.chdir(PdfPath)
    dirlist=glob.glob('*_*')
    #print(len(dirlist))
    for dirpath in dirlist:
        basedict={
            "rr:ResultsReport": {
                "rr:ResultsPayload": {
                    "FinalReport":{
                        "Sample": {
                            "FM_Id": "",
                            "SampleId": "",
                            "BlockId": "",
                            "TRFNumber": "",
                            "TestType": "",
                            "SpecFormat": "",
                            "ReceivedDate": "",
                            },
                        "PMI" : {
                            "ReportId": "",
                            "MRN": "",
                            "FullName": "",
                            "FirstName": "",
                            "LastName": "",
                            "SubmittedDiagnosis": "",
                            "Gender": "",
                            "DOB": "",
                            "OrderingMD": "",
                            "OrderingMDId": "",
                            "Pathologist": "",
                            "CopiedPhysician1": "",
                            "MedFacilName": "",
                            "MedFacilID": "",
                            "SpecSite": "",
                            "CollDate": "",
                            "ReceivedDate": "",
                            "CountryOfOrigin": ""
                           }
                        },
                    "variant-report": {
                        "short_variants": {
                            "short_variant":[]
                            },
                        "copy_number_alterations": {
                            "copy_number_alteration": []
                            },
                        "rearrangements": {
                        	"rearrangement": []
                        },
                        "biomarkers": {
                            "microsatellite_instability": {
                                "status": ""
                            },
                            "tumor_mutation_burden": {
                                "score": ""
                            }
                        }                
                    }
                    }
                }
            }
        ReportNo, MPNo= dirpath.replace('(', '').replace(')', '').split('_')
        filepathlist =glob.glob(os.path.join(dirpath, "*).pdf"))
        #print(filepathlist)
        try:        
            for filename in filepathlist:
                    #print(filename)            
                    reader = PyPDF2.PdfReader(filename)
                    #text_file = open("Output.txt", "w", encoding="utf-8")
                    text=[]
                    for i in range(len(reader.pages)):
                        text.append(reader.pages[i].extract_text())
                        #text_file.write(reader.pages[i].extract_text())
                    #text_file.close()            
                    short_variants = []            
                    rearrangement = []
                    biomarkers = []
                    copy_number_alterations = []
                    pmi = [] 
                    
                    for i in range(len(text)):
                        try:
                            #copy_number_alterations
                            
                            if text[i].find('Copy Number') > -1: 
                                start = text[i].find('Locus Copy Number')
                                end = text[i].find('Copy Number Variation')
                                #print(text[i][start+17:end].strip())
                                copy_number_alterations.extend(text[i][start+28:end].strip().split('\n'))
                                copy_number_alterationlist=[]
                                
                                    
                                for copy_number_alteration in copy_number_alterations:
                                    alterationlist = copy_number_alteration.split(' ')
                                    copy_number_alterationlist.append({"copy_number": alterationlist[2],
                                                              "gene": alterationlist[0],
                                                              "position": alterationlist[1]})
                                basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['copy_number_alterations']['copy_number_alteration'] = copy_number_alterationlist
                                #print(len(text[i][start+43:end-4].split(' \n')))
                            #print(copy_number_alterations)
                        except:
                            None
            
                        if text[i].find('Sample Information') > -1: 
                            #print('\nPMI')
                            #print(text[0])
                            start = text[i].find('Sample Information')
                            end = text[i].find('Note:')
                            #print(text[i][start:end])
                            PATIENT=text[i][start+18:end].strip() 
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['FullName'] = PATIENT.split('\n')[0].split(':')[1].strip()
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['Gender'] = PATIENT.split('\n')[1].split(':')[1].strip()
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['MRN'] = PATIENT.split('\n')[3].split(':')[1].strip()
                            try:
                                basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMD'] = PATIENT.split('\n')[6].split(':')[1].strip().split(' ')[1]
                                basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMDId'] = PATIENT.split('\n')[6].split(':')[1].strip().split(' ')[0]
                            except:
                                basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMDId'] = PATIENT.split('\n')[6].split(':')[1].strip()
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['ReportId'] = PATIENT.split('\n')[7].split(':')[1].strip()
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['TestType'] = PATIENT.split('\n')[12].split(':')[1].strip()
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['SpecFormat'] = PATIENT.split('\n')[13].split(':')[1].strip()
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['BlockId'] = PATIENT.split('\n')[14].split(':')[1].strip()
                            try:
                                basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['TumorPurity'] = PATIENT.split('\n')[15].split(':')[1].strip()
                            except:
                                basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['BlockId'] = ''
                                basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['ReceivedDate'] = PATIENT.split('\n')[14].split(':')[1].strip()
                            
                            start = text[i].find('Cancer Type:')
                            end = text[i].find('Table of Contents')
                            (text[i][start:end])
                            CancerType = text[i][start+12:end].strip() 
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['SubmittedDiagnosis'] = CancerType
                           
                        if text[i].find('DNA Sequence') > -1:
                            #print('\nDETECTED VARIANTS')                        
                            #print(text[i])
                            start = text[i].find('ClinVar 1 Coverage')
                            end = text[i].find('DNA Sequence')
                            short_variants.extend(text[i][start+18:end].strip().split('\n'))
                            #print(len(text[i][start+22:end-5].split(' \n')))
                            #print(text[i][start+22:end-5].split(' \n'))
                            
                        if len(short_variants) > 0:
                            short_variantllist=[]
                            for i in range(len(short_variants)):
                                if len(short_variants[i].split(' ')) > 6 : 
                                    try:
                                        functional_effect = short_variants[i].split(' ')[7]
                                        depth = short_variants[i].split(' ')[8]
                                    except:
                                        depth = ''
                                        functional_effect = ''
                                        
                                    if  short_variants[i].split(' ')[6] == 'frameshift':
                                        transcript = 'frameshift Deletion'
                                    else:
                                        transcript = short_variants[i].split(' ')[6]
                                    if  functional_effect=='Taipei': #functional_effect =='' or
                                        None                                
                                    else:
                                        short_variantllist.append({
                                            "cds_effect": short_variants[i].split(' ')[2],
                                            "depth":depth,
                                            "functional_effect": functional_effect,
                                            "gene": short_variants[i].split(' ')[0],
                                            "percent_reads": short_variants[i].split(' ')[5],
                                            "position": short_variants[i].split(' ')[4],
                                            "protein_effect": short_variants[i].split(' ')[1],
                                            "transcript": transcript,
                                            })
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['short_variants']['short_variant'] = short_variantllist
                            #print(short_variantllist)
                    with open(dirpath+'\\'+ReportNo+'_('+MPNo+').xml', 'w', encoding="utf-8") as output:
                        output.write(xmltodict.unparse(basedict, pretty=True))            
                    #print(dirpath + ' OK')
        except:
            print(dirpath + ' NG')
    os.chdir('..')
    return 'BRCAAssay2xml done'

### Myeloid Assay meta###
def MyeloidAssay2xml(PdfPath):
    os.chdir(PdfPath)
    dirlist=glob.glob('*_*')
    #print(len(dirlist))
    for dirpath in dirlist:
        basedict={
            "rr:ResultsReport": {
                "rr:ResultsPayload": {
                    "FinalReport":{
                        "Sample": {
                            "FM_Id": "",
                            "SampleId": "",
                            "BlockId": "",
                            "TRFNumber": "",
                            "TestType": "",
                            "SpecFormat": "",
                            "ReceivedDate": "",
                            },
                        "PMI" : {
                            "ReportId": "",
                            "MRN": "",
                            "FullName": "",
                            "FirstName": "",
                            "LastName": "",
                            "SubmittedDiagnosis": "",
                            "Gender": "",
                            "DOB": "",
                            "OrderingMD": "",
                            "OrderingMDId": "",
                            "Pathologist": "",
                            "CopiedPhysician1": "",
                            "MedFacilName": "",
                            "MedFacilID": "",
                            "SpecSite": "",
                            "CollDate": "",
                            "ReceivedDate": "",
                            "CountryOfOrigin": ""
                           }
                        },
                    "variant-report": {
                        "short_variants": {
                            "short_variant":[]
                            },
                        "copy_number_alterations": {
                            "copy_number_alteration": []
                            },
                        "rearrangements": {
                        	"rearrangement": []
                        },
                        "biomarkers": {
                            "microsatellite_instability": {
                                "status": ""
                            },
                            "tumor_mutation_burden": {
                                "score": ""
                            }
                        }                
                    }
                    }
                }
            }
        ReportNo, MPNo= dirpath.replace('(', '').replace(')', '').split('_')
        filepathlist =glob.glob(os.path.join(dirpath, "*).pdf"))
        #print(filepathlist)
        #try:        
        for filename in filepathlist:
                #print(filename)            
                reader = PyPDF2.PdfReader(filename)
                #text_file = open("Output.txt", "w", encoding="utf-8")
                text=[]
                for i in range(len(reader.pages)):
                    text.append(reader.pages[i].extract_text())
                    #text_file.write(reader.pages[i].extract_text())
                #text_file.close()            
                short_variants = []            
                rearrangement = []
                biomarkers = []
                copy_number_alterations = []
                pmi = [] 
                
                for i in range(len(text)):
                        
                    try:    
                        #rearrangement
                        if text[i].find('Fusions (RNA)') > -1: 
                            rearrangementlist=[]
                            #print(text[i])
                            start = text[i].find('Read Count')
                            end = text[i].find('Gene Fusions')
                            rearrangement.extend(text[i][start+11:end].split('  '))
                            rearrangement=rearrangement[0].split('\n')
                            for i in range(len(rearrangement)):
                                rearrangementlist.append({
                                    "description": "",
                                    "equivocal": "",
                                    "in_frame": "",
                                    "other_gene": rearrangement[0].replace(' - ', '-').split(' ')[1],
                                    "pos1": rearrangement[0].replace(' - ', '-').split(' ')[2],
                                    "pos2": "",
                                    "status": "",
                                    "supporting_read_pairs": rearrangement[0].replace(' - ', '-').split(' ')[3],
                                    "targeted_gene": rearrangement[0].replace(' - ', '-').split(' ')[0],
                                    "type": "",
                                    "dna_evidence": {
                                    "sample": ""
                                    }})
                            
                            print('\nFusions')
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['rearrangements']['rearrangement']=rearrangementlist
                            #print(rearrangement)    
                    except:
                        None
        
                    if text[i].find('Sample Information') > -1: 
                        #print('\nPMI')
                        #print(text[0])
                        start = text[i].find('Sample Information')
                        end = text[i].find('Note:')
                        #print(text[i][start:end])
                        PATIENT=text[i][start+18:end].strip() 
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['FullName'] = PATIENT.split('\n')[0].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['Gender'] = PATIENT.split('\n')[1].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['MRN'] = PATIENT.split('\n')[3].split(':')[1].strip()
                        try:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMD'] = PATIENT.split('\n')[6].split(':')[1].strip().split(' ')[1]
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMDId'] = PATIENT.split('\n')[6].split(':')[1].strip().split(' ')[0]
                        except:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMDId'] = PATIENT.split('\n')[6].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['ReportId'] = MPNo
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['TestType'] = PATIENT.split('\n')[12].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['SpecFormat'] = PATIENT.split('\n')[13].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['BlockId'] = PATIENT.split('\n')[14].split(':')[1].strip()
                        try:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['TumorPurity'] = PATIENT.split('\n')[15].split(':')[1].strip()
                        except:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['BlockId'] = ''
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['ReceivedDate'] = PATIENT.split('\n')[14].split(':')[1].strip()
                        
                        start = text[i].find('Cancer Type:')
                        end = text[i].find('Table of Contents')
                        (text[i][start:end])
                        CancerType = text[i][start+12:end].strip() 
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['SubmittedDiagnosis'] = CancerType
                       
                    if text[i].find('DNA Sequence') > -1:
                        #print('\nDETECTED VARIANTS')                        
                        #print(text[i])
                        start = text[i].find('Effect Coverage')
                        end = text[i].find('DNA Sequence')
                        short_variants.extend(text[i][start+16:end].strip().split('\n'))
                        #print(len(text[i][start+22:end-5].split(' \n')))
                        #print(text[i][start+22:end-5].split(' \n'))
                        
                    if len(short_variants) > 0:
                        short_variantllist=[]
                        short_variantllist_temp=''
                        for i in range(len(short_variants)):
                            if len(short_variants[i].split(' ')) > 8 : 
                                try:
                                    functional_effect = short_variants[i].split(' ')[7]
                                    depth = short_variants[i].split(' ')[8]
                                except:
                                    depth = ''
                                    functional_effect = ''
                                if  short_variants[i].split(' ')[6] == 'frameshift':
                                    transcript = 'frameshift Deletion'
                                else:
                                    transcript = short_variants[i].split(' ')[6]
                                short_variantllist.append({
                                    "cds_effect": short_variants[i].split(' ')[2],
                                    "depth":depth,
                                    "functional_effect": functional_effect,
                                    "gene": short_variants[i].split(' ')[0],
                                    "percent_reads": short_variants[i].split(' ')[5],
                                    "position": short_variants[i].split(' ')[4],
                                    "protein_effect": short_variants[i].split(' ')[1],
                                    "transcript": transcript,
                                    })
                            else:
                               short_variantllist_temp=short_variantllist_temp+short_variants[i]
                               if len(short_variantllist_temp.split(' ')) > 6:
                                   short_variantllist.append({
                                       "cds_effect": short_variantllist_temp.split(' ')[2],
                                       "depth":short_variantllist_temp.split(' ')[6][len(short_variantllist_temp.split(' ')[6])-4:],
                                       "functional_effect": short_variantllist_temp.split(' ')[6][:len(short_variantllist_temp.split(' ')[6])-4],
                                       "gene": short_variantllist_temp.split(' ')[0],
                                       "percent_reads": short_variantllist_temp.split(' ')[4],
                                       "position": short_variantllist_temp.split(' ')[3],
                                       "protein_effect": short_variantllist_temp.split(' ')[1],
                                       "transcript": short_variantllist_temp.split(' ')[5],
                                       })
                                   
        
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['short_variants']['short_variant'] = short_variantllist
                        #print('short_variantllist')
                        
                with open(dirpath+'\\'+ReportNo+'_('+MPNo+').xml', 'w', encoding="utf-8") as output:
                    output.write(xmltodict.unparse(basedict, pretty=True))            
                #print(dirpath + ' OK')
        #except:
            #print(dirpath + ' NG')
    os.chdir('..')
    return 'MyeloidAssay2xml done'

### Tumor Mutation Load Assay###
def MutationLoadAssay2xml(PdfPath):
    os.chdir(PdfPath)
    dirlist=glob.glob('*_*')
    #print(len(dirlist))
    for dirpath in dirlist:
        basedict={
            "rr:ResultsReport": {
                "rr:ResultsPayload": {
                    "FinalReport":{
                        "Sample": {
                            "FM_Id": "",
                            "SampleId": "",
                            "BlockId": "",
                            "TRFNumber": "",
                            "TestType": "",
                            "SpecFormat": "",
                            "ReceivedDate": "",
                            },
                        "PMI" : {
                            "ReportId": "",
                            "MRN": "",
                            "FullName": "",
                            "FirstName": "",
                            "LastName": "",
                            "SubmittedDiagnosis": "",
                            "Gender": "",
                            "DOB": "",
                            "OrderingMD": "",
                            "OrderingMDId": "",
                            "Pathologist": "",
                            "CopiedPhysician1": "",
                            "MedFacilName": "",
                            "MedFacilID": "",
                            "SpecSite": "",
                            "CollDate": "",
                            "ReceivedDate": "",
                            "CountryOfOrigin": ""
                           }
                        },
                    "variant-report": {
                        "short_variants": {
                            "short_variant":[]
                            },
                        "copy_number_alterations": {
                            "copy_number_alteration": []
                            },
                        "rearrangements": {
                        	"rearrangement": []
                        },
                        "biomarkers": {
                            "microsatellite_instability": {
                                "status": ""
                            },
                            "tumor_mutation_burden": {
                                "score": ""
                            }
                        }                
                    }
                    }
                }
            }
        ReportNo, MPNo = dirpath.replace('(', '').replace(')', '').split('_')
        filepathlist =glob.glob(os.path.join(dirpath, "*).pdf"))
        #print(filepathlist)
        #try:        
        for filename in filepathlist:
                #print(filename)            
                reader = PyPDF2.PdfReader(filename)
                #text_file = open("Output.txt", "w", encoding="utf-8")
                text=[]
                for i in range(len(reader.pages)):
                    text.append(reader.pages[i].extract_text())
                    #text_file.write(reader.pages[i].extract_text())
                #text_file.close()            
                short_variants = []            
                rearrangement = []
                biomarkers = []
                copy_number_alterations = []
                pmi = [] 
                
                for i in range(len(text)):
                        
                    try:    
                        #rearrangement
                        if text[i].find('Fusions (RNA)') > -1: 
                            rearrangementlist=[]
                            #print(text[i])
                            start = text[i].find('Read Count')
                            end = text[i].find('Gene Fusions')
                            rearrangement.extend(text[i][start+11:end].split('  '))
                            rearrangement=rearrangement[0].split('\n')
                            for i in range(len(rearrangement)):
                                rearrangementlist.append({
                                    "description": "",
                                    "equivocal": "",
                                    "in_frame": "",
                                    "other_gene": rearrangement[0].replace(' - ', '-').split(' ')[1],
                                    "pos1": rearrangement[0].replace(' - ', '-').split(' ')[2],
                                    "pos2": "",
                                    "status": "",
                                    "supporting_read_pairs": rearrangement[0].replace(' - ', '-').split(' ')[3],
                                    "targeted_gene": rearrangement[0].replace(' - ', '-').split(' ')[0],
                                    "type": "",
                                    "dna_evidence": {
                                    "sample": ""
                                    }})
                            
                            print('\nFusions')
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['rearrangements']['rearrangement']=rearrangementlist
                            #print(rearrangement)    
                    except:
                        None
        
                    if text[i].find('Sample Information') > -1: 
                        #print('\nPMI')
                        #print(text[0])
                        start = text[i].find('Sample Information')
                        end = text[i].find('Note:')
                        #print(text[i][start:end])
                        PATIENT=text[i][start+18:end].strip() 
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['FullName'] = PATIENT.split('\n')[0].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['Gender'] = PATIENT.split('\n')[1].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['MRN'] = PATIENT.split('\n')[3].split(':')[1].strip()
                        try:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMD'] = PATIENT.split('\n')[6].split(':')[1].strip().split(' ')[1]
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMDId'] = PATIENT.split('\n')[6].split(':')[1].strip().split(' ')[0]
                        except:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMDId'] = PATIENT.split('\n')[6].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['ReportId'] = MPNo
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['TestType'] = PATIENT.split('\n')[12].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['SpecFormat'] = PATIENT.split('\n')[13].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['BlockId'] = PATIENT.split('\n')[14].split(':')[1].strip()
                        try:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['TumorPurity'] = PATIENT.split('\n')[15].split(':')[1].strip()
                        except:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['BlockId'] = ''
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['ReceivedDate'] = PATIENT.split('\n')[14].split(':')[1].strip()
                        
                        start = text[i].find('Cancer Type:')
                        end = text[i].find('Table of Contents')
                        (text[i][start:end])
                        CancerType = text[i][start+12:end].strip() 
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['SubmittedDiagnosis'] = CancerType
                       
                    if text[i].find('DNA Sequence') > -1:
                        #print('\nDETECTED VARIANTS')                        
                        #print(text[i])
                        start = text[i].find('Effect Coverage')
                        end = text[i].find('DNA Sequence')
                        short_variants.extend(text[i][start+16:end].strip().split('\n'))
                        #print(len(text[i][start+22:end-5].split(' \n')))
                        #print(text[i][start+22:end-5].split(' \n'))
                        
                    if len(short_variants) > 0:
                        short_variantllist=[]
                        short_variantllist_temp=''
                        for i in range(len(short_variants)):
                            if len(short_variants[i].split(' ')) > 8 : 
                                try:
                                    functional_effect = short_variants[i].split(' ')[7]
                                    depth = short_variants[i].split(' ')[8]
                                except:
                                    depth = ''
                                    functional_effect = ''
                                if  short_variants[i].split(' ')[6] == 'frameshift':
                                    transcript = 'frameshift Deletion'
                                else:
                                    transcript = short_variants[i].split(' ')[6]
                                short_variantllist.append({
                                    "cds_effect": short_variants[i].split(' ')[2],
                                    "depth":depth,
                                    "functional_effect": functional_effect,
                                    "gene": short_variants[i].split(' ')[0],
                                    "percent_reads": short_variants[i].split(' ')[5],
                                    "position": short_variants[i].split(' ')[4],
                                    "protein_effect": short_variants[i].split(' ')[1],
                                    "transcript": transcript,
                                    })
                            else:
                               short_variantllist_temp=short_variantllist_temp+short_variants[i]
                               if len(short_variantllist_temp.split(' ')) > 6:
                                   short_variantllist.append({
                                       "cds_effect": short_variantllist_temp.split(' ')[2],
                                       "depth":short_variantllist_temp.split(' ')[6][len(short_variantllist_temp.split(' ')[6])-4:],
                                       "functional_effect": short_variantllist_temp.split(' ')[6][:len(short_variantllist_temp.split(' ')[6])-4],
                                       "gene": short_variantllist_temp.split(' ')[0],
                                       "percent_reads": short_variantllist_temp.split(' ')[4],
                                       "position": short_variantllist_temp.split(' ')[3],
                                       "protein_effect": short_variantllist_temp.split(' ')[1],
                                       "transcript": short_variantllist_temp.split(' ')[5],
                                       })
                                   
        
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['short_variants']['short_variant'] = short_variantllist
                        #print('short_variantllist')
                        
                with open(dirpath+'\\'+ReportNo+'_('+MPNo+').xml', 'w', encoding="utf-8") as output:
                    output.write(xmltodict.unparse(basedict, pretty=True))            
                #print(dirpath + ' OK')
        #except:
            #print(dirpath + ' NG')
    os.chdir('..')
    return 'MutationLoadAssay2xml done'

### creating a pdf reader object Focus Assay ###
def FocusAssay2xml(PdfPath):
    #print('FocusAssay2xml')
    #print(os.getcwd())
    os.chdir(os.getcwd()+'/'+PdfPath)
    #dirlist=glob.glob('M112-10065_(PT23030)*')#Fusions
    dirlist=glob.glob('*_*')
    #print(len(dirlist))
    for dirpath in dirlist:
        basedict={
            "rr:ResultsReport": {
                "rr:ResultsPayload": {
                    "FinalReport":{
                        "Sample": {
                            "FM_Id": "",
                            "SampleId": "",
                            "BlockId": "",
                            "TRFNumber": "",
                            "TestType": "",
                            "SpecFormat": "",
                            "ReceivedDate": "",
                            },
                        "PMI" : {
                            "ReportId": "",
                            "MRN": "",
                            "FullName": "",
                            "FirstName": "",
                            "LastName": "",
                            "SubmittedDiagnosis": "",
                            "Gender": "",
                            "DOB": "",
                            "OrderingMD": "",
                            "OrderingMDId": "",
                            "Pathologist": "",
                            "CopiedPhysician1": "",
                            "MedFacilName": "",
                            "MedFacilID": "",
                            "SpecSite": "",
                            "CollDate": "",
                            "ReceivedDate": "",
                            "CountryOfOrigin": ""
                           }
                        },
                    "variant-report": {
                        "short_variants": {
                            "short_variant":[]
                            },
                        "copy_number_alterations": {
                            "copy_number_alteration": []
                            },
                        "rearrangements": {
                        	"rearrangement": []
                        },
                        "biomarkers": {
                            "microsatellite_instability": {
                                "status": ""
                            },
                            "tumor_mutation_burden": {
                                "score": ""
                            }
                        }                
                    }
                    }
                }
            }
      
        try:    
            ReportNo, MPNo  = dirpath.replace('(', '').replace(')', '').split('_')
            filepathlist =glob.glob(os.path.join(dirpath, "*).pdf"))
            #print(filepathlist)
            
            for filename in filepathlist:
                #print(filename)            
                reader = PyPDF2.PdfReader(filename)
                #text_file = open("Output.txt", "w", encoding="utf-8")
                text=[]
                for i in range(len(reader.pages)):
                    text.append(reader.pages[i].extract_text())
                    #text_file.write(reader.pages[i].extract_text())
                #text_file.close()            
                short_variants = []            
                rearrangement = []
                biomarkers = []
                copy_number_alterations = []
                pmi = []           
                
                for i in range(len(text)):
                    #print(i)
                    #print(text[i])
                    #print(text[i].find('Gene Fusions') > -1)
                    try:
                        #rearrangement
                        
                        if text[i].find('Gene Fusions (RNA)') > -1: 
                            #print(text[i])                    
                            start = text[i].find('ID Locus Read Count')
                            end = text[i].find('Gene Fusions')
                            #print(text[i][start+19:end-5].strip().split('\n'))
                            
                            rearrangement.extend(text[i][start+19:end].strip().split('\n'))
                            rearrangementlist=[]
                            for i in range(len(rearrangement)):
                                rearrangementlist.append({
                            		"description": rearrangement[i].replace(' - ', '-').split(' ')[1].split('.')[0]+'.'+rearrangement[i].replace(' - ', '-').split(' ')[1].split('.')[1],
                            		"other_gene": rearrangement[i].replace(' - ', '-').split(' ')[0].split('-')[0],
                                    "pos1": rearrangement[i].replace(' - ', '-').split(' ')[2].split('-')[0],
                                    "pos2": rearrangement[i].replace(' - ', '-').split(' ')[2].split('-')[1],
                                    "supporting_read_pairs": rearrangement[i].replace(' - ', '-').split(' ')[3],
                            		"targeted_gene": rearrangement[i].replace(' - ', '-').split(' ')[0].split('-')[1]
                                    })                                                       
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['rearrangements']['rearrangement']=rearrangementlist
                            #print(len(text[i][start+16:end-5].split(' \n')))    
                            #print('rearrangementlist')
                    except:
                        None
                            
                    #print(text[i].find('Copy Number Variations') > -1)
                    try:
                        #copy_number_alterations
                        
                        if text[i].find('Copy Number') > -1: 
                            #print('\ncopy_number_alterations')
                            #print(text[i])
                            start = text[i].find('Locus Copy Number')
                            end = text[i].find('Copy Number Variation')
                            #print(text[i][start+17:end].strip())
                            copy_number_alterations.extend(text[i][start+17:end].strip().split('\n'))
                            copy_number_alterationlist=[]
                            
                                
                            for copy_number_alteration in copy_number_alterations:
                                alterationlist = copy_number_alteration.split(' ')
                                copy_number_alterationlist.append({"copy_number": alterationlist[2],
                                                          "gene": alterationlist[0],
                                                          "position": alterationlist[1]})
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['copy_number_alterations']['copy_number_alteration'] = copy_number_alterationlist
                            #print(len(text[i][start+43:end-4].split(' \n')))
                        #print(copy_number_alterations)
                    except:
                        None

                    #pmi
                    #print(text[i].find('Sample Information') > -1)
                    #:
                    if text[i].find('Sample Information') > -1: 
                        #print('\nPMI')
                        #print(text[0])
                        start = text[i].find('Sample Information')
                        end = text[i].find('Note:')
                        #print(text[i][start:end])
                        PATIENT=text[i][start+18:end].strip() 
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['FullName'] = PATIENT.split('\n')[0].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['Gender'] = PATIENT.split('\n')[1].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['MRN'] = PATIENT.split('\n')[3].split(':')[1].strip()
                        try:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMD'] = PATIENT.split('\n')[6].split(':')[1].strip().split(' ')[1]
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMDId'] = PATIENT.split('\n')[6].split(':')[1].strip().split(' ')[0]
                        except:
                            basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['OrderingMDId'] = PATIENT.split('\n')[6].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['ReportId'] = PATIENT.split('\n')[7].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['ReportId'] = PATIENT.split('\n')[8].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['BlockId'] = dirpath
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['TestType'] = PATIENT.split('\n')[12].split(':')[1].strip()
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['Sample']['SpecFormat'] = PATIENT.split('\n')[13].split(':')[1].strip()
                        
                        start = text[i].find('Cancer Type:')
                        end = text[i].find('Table of Contents')
                        (text[i][start:end])
                        CancerType = text[i][start+12:end].strip() 
                        basedict['rr:ResultsReport']['rr:ResultsPayload']['FinalReport']['PMI']['SubmittedDiagnosis'] = CancerType
                    #except:
                        #None
                        
                    #short variants
                    #print(text[i].find('DNA Sequence') > -1)                   
                    if text[i].find('DNA Sequence') > -1:
                        #print('\nDETECTED VARIANTS')                        
                        #print(text[i])
                        start = text[i].find('Effect Coverage')
                        end = text[i].find('DNA Sequence')
                        short_variants.extend(text[i][start+15:end].strip().split('\n'))
                        #print(len(text[i][start+22:end-5].split(' \n')))
                        #print(text[i][start+22:end-5].split(' \n'))
                        
                    if len(short_variants) > 0:
                        short_variantllist=[]
                        for i in range(len(short_variants)):
                            if len(short_variants[i].split(' '))==9:                                
                                short_variantllist.append({
                                    "cds_effect": short_variants[i].split(' ')[2],
                                    "depth": short_variants[i].split(' ')[8],
                                    "functional_effect": short_variants[i].split(' ')[7],
                                    "gene": short_variants[i].split(' ')[0],
                                    "percent_reads": short_variants[i].split(' ')[5],
                                    "position": short_variants[i].split(' ')[4],
                                    "protein_effect": short_variants[i].split(' ')[1],
                                    "transcript": short_variants[i].split(' ')[6],
                                    }) 

                        basedict['rr:ResultsReport']['rr:ResultsPayload']['variant-report']['short_variants']['short_variant'] = short_variantllist
                        #print('short_variantllist')
                        
                with open(dirpath+'\\'+ReportNo+'_('+MPNo+').xml', 'w', encoding="utf-8") as output:
                    output.write(xmltodict.unparse(basedict, pretty=True))            
                #print(dirpath + ' OK')           
        except:
            None
            #print(dirpath + ' NG')
            
    os.chdir('..')
    return 'FocusAssay2xml done'

### 轉出PDF 至 目錄 ###
def pdf2dir(PdfPath,root):
    os.chdir(PdfPath)
    try:
        dirlist=glob.glob('*_*')
        #print(len(dirlist))
        for dirpath in dirlist:
            try:    
                ReportNo, MPNo = dirpath.replace('(', '').replace(')', '').split('_')
                #filepathlist =glob.glob(os.path.join(dirpath, "*.xml"))
                filepathlist =glob.glob(os.path.join(dirpath, "*).pdf"))
                #print(filepathlist)        
                for filename in filepathlist:
                    #print(filename.split('\\')[1])
                    # Source file
                    source = filename              
                    # Destination file 
                    destination = '../../gene/'+filename.split('\\')[1]             
                    # Copy source to destination 
                    #dest = shutil.move(source, destination) 
                    dest = shutil.copyfile(source, destination) 
                    #print(dirpath + ' OK')
            except:
                None
                #print(dirpath + ' NG')
    except:
        None
    os.chdir('..')
    return 'pdf2dir done'
