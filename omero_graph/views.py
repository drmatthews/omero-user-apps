from django.http import Http404, HttpResponse
from django.shortcuts import render

from collections import defaultdict
import numpy as np
import pandas as pd

import omero
from omeroweb.webclient.decorators import login_required

def store_data(ann):
    """
    Downloads the specified file to and returns the path on the server
    
    @param ann:    the file annotation being downloaded
    """ 
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    file_path = os.path.join(PATH, ann.getFile().getName())
    store = pd.HDFStore(file_path,mode='w')
    try:
        for chunk in ann.getFileInChunks():
            store.append('df',chunk)
    finally:
        store.close()
    return file_path

def find_duplicate_annotations(mylist):
    D = defaultdict(list)
    for i,item in enumerate(mylist):
        D[item].append(i)
    return {k:v for k,v in D.items() if len(v)>1}
    
def get_user_annotations(conn,extensions=('txt','csv','xls')):

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
    context = {'userFullName': userFullName,
               'annotations': anns
               'annotation_names': names }
    return render(request, "omero_graph/index.html", context)