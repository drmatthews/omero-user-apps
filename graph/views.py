from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from forms import PreviewForm,AnnotationsForm,GraphForm

import os
import re
from math import floor
from collections import defaultdict
import numpy as np
import pandas as pd
import json
import csv
from itertools import islice
import openpyxl
from PIL import Image
import tempfile
import shutil

import omero
from omeroweb.webclient.decorators import login_required

ANNPATH = '/Users/uqdmatt2/Desktop/temp'
#ANNPATH = tempfile.mkdtemp(prefix='downloaded_annotations')

def upload_graph(conn, path):
    """
    This creates a new Image in OMERO using all the images in destination folder as Z-planes
    """
    
    gid = conn.getGroupFromContext().getId()
    conn.SERVICE_OPTS.setOmeroGroup(gid)
    
    # Need to check whether we're dealing with RGB images (3 channels) or greyscale (1 channel)
    img = Image.open(path)
    img.load()
    sizeC = len(img.split())
    sizeZ = 1
    sizeT = 1
    imageName = os.path.basename(path)
    print 'imageName',imageName
    # Create a new Image in OMERO, with the jpeg images as a Z-stack.
    # We need a generator to produce numpy planes in the order Z, C, T.
    def plane_generator():
        img = Image.open(path)
        img.load()      # need to get the data in hand before...
        channels = img.split()
        for channel in channels:
            numpyPlane = np.asarray(channel)
            yield numpyPlane

    # Create the image
    plane_gen = plane_generator()
    newImg = conn.createImageFromNumpySeq(plane_gen, imageName, sizeZ=sizeZ, sizeC=sizeC, sizeT=sizeT)
    print "New Image ID", newImg.getId()
    return newImg
    
def flot_data(xdata,ydata):
    
    # ydata is a list of lists
    fdata = []
    for yd in ydata:
        sdata = []
        for i,y in enumerate(yd):
            sdata.append([xdata[i],y])
        fdata.append(sdata)
    return fdata

def get_data(path,ext,header_row,sheet):
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
    return data
                                   
def get_column(path,ext,col,header_row,sheet):
    try:
        data = get_data(path,ext,header_row,sheet)

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
    
def preview_data(path,ext,sheet):
    max_rows = 10
    max_cols = 10
    try:
        if '.xls' in ext:
            wb = openpyxl.load_workbook(path)
            sh = wb.get_sheet_names()[sheet]
            shdata = wb.get_sheet_by_name(sh)
            num_rows = shdata.get_highest_row() - 1
            num_cols = shdata.get_highest_column()
            data = []
            for r in range(max_rows):
                row_data = []
                for c in range(max_cols):
                    row_data.append(shdata.cell(row=r+1, column=c+1).value)
                data.append(row_data)
        elif '.txt' in ext:
            num_rows = sum(1 for line in open(path))
            with open(path) as file:
                data = [next(file)[:max_cols] for x in xrange(max_rows)]
        elif '.csv' in ext:
            num_rows = sum(1 for line in open(path))
            with open(path) as file:
                csv_file = csv.reader(file)
                data = []
                for i in range(max_rows):
                    data.append(csv_file.next()[:max_cols])
        print num_rows
        if num_rows < 1000:
            return data
        else:
            return None
    except:
        print 'there was a problem parsing the data'
        return None
                
def parse_annotation(path,ext,header_row,sheet):
    try:
        data = get_data(path,ext,header_row,sheet)
    
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
    
    if not os.path.exists(ANNPATH):
        os.makedirs(ANNPATH)
    file_path = os.path.join(ANNPATH, ann.getFile().getName())
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
            
            header_row = 0
            if form.cleaned_data['header'] is not None:
                header_row = form.cleaned_data['header']

            sheet = 0
            if form.cleaned_data['sheet'] is not None:
                sheet = form.cleaned_data['sheet']
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
        preview_form = PreviewForm(options=form_names,\
                                   initial={'preview_sheet':0})
        ann_form = AnnotationsForm(options=form_names,\
                                   initial={'header':0,\
                                            'sheet':0})
        num_xls = len([name for name in names if '.xls' in name])
        num_txt = len([name for name in names if '.txt' in name])
        num_csv = len([name for name in names if '.csv' in name])
        graph_form = GraphForm(options=(('x','x'),('y','y')))
        
        context = {'userFullName': userFullName,
                   'annotations': anns,'num_annotations': len(anns),
                   'annotation_names': names, 'num_xls': num_xls,
                   'num_csv': num_csv, 'num_txt': num_txt,
                   'form': ann_form, 'graph_form': graph_form,\
                   'prev_form':preview_form}
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
            if form.cleaned_data['title']:
                title = form.cleaned_data['title']
            x = form.cleaned_data['x']
            y = form.cleaned_data['y']
            xLabel = x
            if form.cleaned_data['xLabel']:
                xLabel = form.cleaned_data['xLabel']
            yLabel = y
            if form.cleaned_data['yLabel']:
                yLabel = form.cleaned_data['yLabel']
            xdata = [floor(xd) for xd in get_column(fpath,fextension,x,header_row,sheet)]
            xmin = min(xdata)
            xmax = max(xdata)
            ydata = get_column(fpath,fextension,y,header_row,sheet)
            graph = flot_data(xdata,ydata)
            rv = {'message': message,\
                  'title': title, 'x' : x, 'y' : y,\
                  'xLabel': xLabel, 'yLabel': yLabel,\
                  'xdata': xdata, 'ydata': ydata,\
                  'num_series': len(ydata),
                  'xmin': xmin, 'xmax': xmax,'graph_data': graph}
            data = json.dumps(rv)
            return HttpResponse(data, mimetype='application/json')
            
@login_required()
def preview(request, conn=None, **kwargs):
    anns,names = get_user_annotations(conn)
    form_names = [(" "," ")]
    for name in names:
        form_names.append((name,name))
    if request.POST:
        form = PreviewForm(options=form_names,data=request.POST)
        if form.is_valid():
            selected = form.cleaned_data['preview_annotation']

            sheet = 0
            if form.cleaned_data['preview_sheet'] is not None:
                sheet = form.cleaned_data['preview_sheet']
                                
            annId = selected.partition(' ')[0][3:]
            annotation = conn.getObject("Annotation",annId)
            fpath = download_annotation(annotation)
            fname, fextension = os.path.splitext(fpath)
            pdata = preview_data(fpath,fextension,sheet)
            if pdata is not None:
                rv = {'preview_data': pdata}
                data = json.dumps(rv)
                return HttpResponse(data, mimetype='application/json')
            else:
                rv = {'message':"Too many rows"}
                error = json.dumps(rv)
                return HttpResponseBadRequest(error, mimetype='application/json')

@login_required()
def save(request, conn=None, **kwargs):
    if request.POST:
        datauri = request.POST['img']
        imgstr = re.search(r'base64,(.*)', datauri).group(1)
        output_dir = tempfile.mkdtemp(prefix='exported_graphs')
        path = os.path.join(output_dir,"graph.png")
        output = open(path, 'wb')
        output.write(imgstr.decode('base64'))
        output.close()
        # and upload to omero
        img = upload_graph(conn,path)
        if img:
            shutil.rmtree(output_dir)
            rv = {'message':"Sucessfully saved"}
            data = json.dumps(rv)
            return HttpResponse(data, mimetype='application/json')
        else:
            rv = {'message':"Exporting failed"}
            error = json.dumps(rv)
            return HttpResponseBadRequest(error, mimetype='application/json')
        