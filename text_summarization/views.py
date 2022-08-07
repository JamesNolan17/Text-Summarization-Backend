from django.shortcuts import render
from matplotlib.pyplot import text
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers import TextSerializer, InputSerializer
from . import models
from rest_framework import status
import os
import re 
from time import time
import spacy
from spacy.cli.download import download
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


def text_strip(row):
    
        
        #ORDER OF REGEX IS VERY VERY IMPORTANT!!!!!!
        
        row=re.sub("(\\t)", ' ', str(row)).lower() #remove escape charecters
        row=re.sub("(\\r)", ' ', str(row)).lower() 
        row=re.sub("(\\n)", ' ', str(row)).lower()
        
        row=re.sub("(__+)", ' ', str(row)).lower()   #remove _ if it occors more than one time consecutively
        row=re.sub("(--+)", ' ', str(row)).lower()   #remove - if it occors more than one time consecutively
        row=re.sub("(~~+)", ' ', str(row)).lower()   #remove ~ if it occors more than one time consecutively
        row=re.sub("(\+\++)", ' ', str(row)).lower()   #remove + if it occors more than one time consecutively
        row=re.sub("(\.\.+)", ' ', str(row)).lower()   #remove . if it occors more than one time consecutively
        
        row=re.sub(r"[<>()|&©ø\[\]\'\",;?~*!]", ' ', str(row)).lower() #remove <>()|&©ø"',;?~*!
        
        row=re.sub("(mailto:)", ' ', str(row)).lower() #remove mailto:
        row=re.sub(r"(\\x9\d)", ' ', str(row)).lower() #remove \x9* in text
        row=re.sub("([iI][nN][cC]\d+)", 'INC_NUM', str(row)).lower() #replace INC nums to INC_NUM
        row=re.sub("([cC][mM]\d+)|([cC][hH][gG]\d+)", 'CM_NUM', str(row)).lower() #replace CM# and CHG# to CM_NUM
        
        
        row=re.sub("(\.\s+)", ' ', str(row)).lower() #remove full stop at end of words(not between)
        row=re.sub("(\-\s+)", ' ', str(row)).lower() #remove - at end of words(not between)
        row=re.sub("(\:\s+)", ' ', str(row)).lower() #remove : at end of words(not between)
        
        row=re.sub("(\s+.\s+)", ' ', str(row)).lower() #remove any single charecters hanging between 2 spaces
        
        #Replace any url as such https://abc.xyz.net/browse/sdf-5327 ====> abc.xyz.net
        try:
            url = re.search(r'((https*:\/*)([^\/\s]+))(.[^\s]+)', str(row))
            repl_url = url.group(3)
            row = re.sub(r'((https*:\/*)([^\/\s]+))(.[^\s]+)',repl_url, str(row))
        except:
            pass #there might be emails with no url in them
        

        
        row = re.sub("(\s+)",' ',str(row)).lower() #remove multiple spaces
        
        #Should always be last
        row=re.sub("(\s+.\s+)", ' ', str(row)).lower() #remove any single charecters hanging between 2 spaces

        
        
        return row

def data_preprocess(raw_text):
    brief_cleaning = text_strip(raw_text)
    print(brief_cleaning)
    download(model="en_core_web_sm")
    nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser']) 
    text = [str(doc) for doc in nlp.pipe(brief_cleaning, batch_size=5000)]
    return text

class TextInstanceGetView(GenericAPIView):
   # permission_classes = (IsAuthenticated,)
    serializer_class = TextSerializer
    
    def get(self, request):
        text = models.text.objects.all().order_by('created_at')
        if len(text)== 0:
            return Response(list(), status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.serializer_class(text, many=True)
            self.queryset = serializer
        return Response(serializer.data, status = status.HTTP_200_OK)
        

class TextDeleteOneView(GenericAPIView):
    #permission_classes = (IsAuthenticated,)

    def delete(self, request, text_id):
        text = models.text.objects.get(id = text_id)
        if text:
            text.delete()
        else:
            return Response("No video found! " + str(text),status=status.HTTP_400_BAD_REQUEST)
        return Response("Deleted!",status=status.HTTP_201_CREATED)

       
class TextGetOneView(GenericAPIView):
    #permission_classes = (IsAuthenticated,)
    serializer_class = TextSerializer
    def get(self, request, text_id):
        text = models.text.objects.get(id = text_id)
        serializer = self.serializer_class(text, many=False)
        return Response(serializer.data)

class TextUploadView(GenericAPIView):
    #permission_classes = (IsAuthenticated,)
    serializer_class = TextSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TextUpdateView(GenericAPIView):
    #permission_classes = (IsAuthenticated,)
    serializer_class = TextSerializer
    def post(self,request, text_id):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            text = models.text.objects.get(id = text_id)
            text.raw_text = serializer.data['raw_text']
            text.summary = serializer.data['summary']
            text.labels = serializer.data['labels']
            text.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@method_decorator(csrf_exempt, name='dispatch')
class InputView(GenericAPIView):
    serializer_class = InputSerializer

    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            raw_text = serializer.data['raw_text']
            # perform AI 
            print(raw_text)
            preprecessed_data = data_preprocess(raw_text)
            print(preprecessed_data)
            summary = 'haha'
            lable_list = ['happy']
            lable = ' '.join(str(e) for e in lable_list)
            data = {
                "raw_text": raw_text,
                "summary": summary,
                "labels": lable,
                "preprocessed_data":' '
            }
            text_serializer = TextSerializer(data = data)
            if text_serializer.is_valid():
                text_serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response("Created Successfully", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


