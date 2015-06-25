from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from forms import AnnotationsForm,GraphForm

import os
from math import floor
from collections import defaultdict
import numpy as np
import pandas as pd
import json

import omero
from omeroweb.webclient.decorators import login_required

PATH = '/Users/uqdmatt2/Desktop/temp'


def flot_data(xdata,ydata):
    
    # ydata is a list of lists
    fdata = []
    for yd in ydata:
        sdata = []
        for i,y in enumerate(yd):
            sdata.append([xdata[i],y])
        fdata.append(sdata)
    return fdata
        
def get_column(path,ext,col,header_row,sheet):

    try:
        if ('xls' in ext):
            with open(path) as t_in:
                data = pd.read_excel(t_in,header=int(header_row),sheetname=sheet,\
                                   engine='xlrd',
                                   index_col=False)
        else:
            with open(path) as t_in:
                data = pd.read_csv(t_in,header=int(header_row),\
                                   sep=r'\t|,',engine='python',\
                                   index_col=False)

        if type(col) != list:
            return list(data[col].values)
        else:
            vals = []    
            for c in col:
                vals.append(list(data[c].values))
            return vals      
    except:
        print 'there was a problem parsing the data'
        return None
        
def parse_annotation(path,ext,header_row,sheet):
    try:
        if ('xls' in ext):
            with open(path) as t_in:
                data = pd.read_excel(t_in,header=int(header_row),sheetname=sheet,\
                                   engine='xlrd',
                                   index_col=False)
        else:
            with open(path) as t_in:
                data = pd.read_csv(t_in,header=int(header_row),\
                                   sep=r'\t|,',engine='python',\
                                   index_col=False)
    
        num_rows = len(data.index)
        if num_rows < 1000:
            columns = [(" ", " ")]
            for col in data.columns.values:
                columns.append((col,col))
            message = "Sucessfully processed %s for plotting" % os.path.basename(path) 
            return columns,message  
        else:
            columns = None
            message = "Unfortunately that dataset has too many columns for plotting" 
            return columns,message
    except:
        print 'there was a problem parsing the data'
        return None
        
def download_annotation(ann):
    """
    Downloads the specified file to and returns the path on the server
    
    @param ann:    the file annotation being downloaded
    """ 
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    file_path = os.path.join(PATH, ann.getFile().getName())
    if os.path.isfile(file_path):
        return file_path
    else:
        f = open(str(file_path), 'w')
        print "\nDownloading file to", file_path, "..."
        try:
            for chunk in ann.getFileInChunks():
                f.write(chunk)
        finally:
            f.close()
            print "File downloaded!"
        return file_path

def find_duplicate_annotations(mylist):
    D = defaultdict(list)
    for i,item in enumerate(mylist):
        D[item].append(i)
    return {k:v for k,v in D.items() if len(v)>1}
    
def get_user_annotations(conn,extensions=('txt','csv','xls','xlsx')):

    params = omero.sys.ParametersI()
    params.exp(conn.getUser().getId())  # only show current user's Datasets
    datasets = conn.getObjects("Dataset", params=params)
    annotations = []
    annotation_names = []
    for dataset in datasets:
        for dsAnn in dataset.listAnnotations():
            if isinstance(dsAnn, omero.gateway.FileAnnotationWrapper):
                annotations.append(dsAnn)
                annotation_names.append(dsAnn.getFile().getName())
        for image in dataset.listChildren():
            for imAnn in image.listAnnotations():
                if isinstance(imAnn, omero.gateway.FileAnnotationWrapper):
                    annotations.append(imAnn)
                    annotation_names.append(imAnn.getFile().getName())
                    
    filtered_anns = []
    filtered_names = []
    for ext in extensions:
        filtered_anns.extend([ann[0] for ann in zip(annotations,annotation_names) if ext in ann[1]])
        filtered_names.extend(["ID:"+str(ann[0].getId())+" "+ann[1] for ann in zip(annotations,annotation_names) if ext in ann[1]])
        
    duplicates = find_duplicate_annotations(filtered_names)
    for k,v in duplicates.iteritems():
        dups = v[1:]
        for d in dups:
            filtered_anns.pop(d)
            filtered_names.pop(d)
        
    return filtered_anns,filtered_names

    
@login_required()
def index(request, conn=None, **kwargs):
    userFullName = conn.getUser().getFullName()
    anns,names = get_user_annotations(conn)
    form_names = [(" "," ")]
    for name in names:
        form_names.append((name,name))
    if request.POST:
        form = AnnotationsForm(options=form_names,data=request.POST)
        if form.is_valid():
            selected = form.cleaned_data['annotation']
            
            header_row = 1
            if form.cleaned_data['header'] is not None:
                header_row = form.cleaned_data['header']

            sheet = 1
            if form.cleaned_data['sheet'] is not None:
                header_row = form.cleaned_data['sheet']
                                
            annId = selected.partition(' ')[0][3:]
            request.session['annotation_id'] = annId
            request.session['header'] = header_row
            request.session['sheet'] = sheet
            annotation = conn.getObject("Annotation",annId)
            fpath = download_annotation(annotation)
            fname, fextension = os.path.splitext(fpath)
            cols,message = parse_annotation(fpath,fextension,header_row,sheet)
            if cols is not None:
                rv = {'success':True,'message':message,'selected': selected,'columns': cols}
                data = json.dumps(rv)
                return HttpResponse(data, mimetype='application/json')
            else:
                rv = {'success':False,'message':message}
                error = json.dumps(rv)
                return HttpResponseBadRequest(error, mimetype='application/json')
    else:
        ann_form = AnnotationsForm(options=form_names)
        num_xls = len([name for name in names if '.xls' in name])
        num_txt = len([name for name in names if '.txt' in name])
        num_csv = len([name for name in names if '.csv' in name])
        graph_form = GraphForm(options=(('x','x'),('y','y')))
        context = {'userFullName': userFullName,
                   'annotations': anns,'num_annotations': len(anns),
                   'annotation_names': names, 'num_xls': num_xls,
                   'num_csv': num_csv, 'num_txt': num_txt,
                   'form': ann_form, 'graph_form': graph_form}
        return render(request, "graph/index.html", context)
            
@login_required()
def plot(request, conn=None, **kwargs):
    annotation_id = request.session['annotation_id']
    annotation = conn.getObject("Annotation",annotation_id)
    fpath = download_annotation(annotation)
    header_row = request.session['header']
    sheet = request.session['sheet']
    fname, fextension = os.path.splitext(fpath)
    cols,message = parse_annotation(fpath,fextension,header_row,sheet)
    if request.POST:
        form = GraphForm(options=cols,data=request.POST.copy())
        if form.is_valid():
            title = annotation.getFile().getName()
            x = form.cleaned_data['x']
            y = form.cleaned_data['y']
            xdata = [floor(xd) for xd in get_column(fpath,fextension,x,header_row,sheet)]
            xmin = min(xdata)
            xmax = max(xdata)
            ydata = get_column(fpath,fextension,y,header_row,sheet)
            flot = flot_data(xdata,ydata)
            rv = {'message': message,\
                  'title': title, 'x' : x, 'y' : y,\
                  'xdata': xdata, 'ydata': ydata,\
                  'num_series': len(ydata),
                  'xmin': xmin, 'xmax': xmax,'flot_data': flot}
            data = json.dumps(rv)
            return HttpResponse(data, mimetype='application/json')
    