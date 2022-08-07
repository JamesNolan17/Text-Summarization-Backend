import re
from time import time
import pandas as pd
import numpy as np
import spacy
from spacy.cli.download import download
from keras.preprocessing.text import Tokenizer 
from keras.preprocessing.sequence import pad_sequences
from keras import backend as K 
import gensim
from numpy import *
from bs4 import BeautifulSoup
from keras.preprocessing.text import Tokenizer 
from keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping
import warnings

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
        
        try:
            url = re.search(r'((https*:\/*)([^\/\s]+))(.[^\s]+)', str(row))
            repl_url = url.group(3)
            row = re.sub(r'((https*:\/*)([^\/\s]+))(.[^\s]+)',repl_url, str(row))
        except:
            pass #there might be emails with no url in them
        row = re.sub("(\s+)",' ',str(row)).lower() #remove multiple spaces
        row=re.sub("(\s+.\s+)", ' ', str(row)).lower() #remove any single charecters hanging between 2 spaces

        yield row

def data_preprocess(raw_text):
    brief_cleaning = text_strip(raw_text)
    print(brief_cleaning)
    download(model="en_core_web_sm")
    nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser']) 
    text = [str(doc) for doc in nlp.pipe(brief_cleaning, batch_size=5000)]
    cleaned_text = np.array(pd.Series(text))
    x_tokenizer = Tokenizer() 
    x_tokenizer.fit_on_texts(list(cleaned_text))
    thresh=4
    cnt=0
    tot_cnt=0
    freq=0
    tot_freq=0

    for key,value in x_tokenizer.word_counts.items():
        tot_cnt=tot_cnt+1
        tot_freq=tot_freq+value
        if(value<thresh):
            cnt=cnt+1
            freq=freq+value
    x_tokenizer = Tokenizer(num_words=tot_cnt-cnt) 
    x_tokenizer.fit_on_texts(list(cleaned_text))
    x_cleaned_text = x_tokenizer.texts_to_sequences(cleaned_text) 
    cleaned_text    =   pad_sequences(x_cleaned_text,  maxlen=1000, padding='post')
    x_voc   =  x_tokenizer.num_words + 1
    return cleaned_text

def decode_sequence(input_seq, encoder_model, decoder_model):
    # Encode the input as state vectors.
    e_out, e_h, e_c = encoder_model.predict(input_seq)
    
    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1,1))
    
    # Populate the first word of target sequence with the start word.
    target_seq[0, 0] = target_word_index['sostok']

    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
      
        output_tokens, h, c = decoder_model.predict([target_seq] + [e_out, e_h, e_c])

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_token = reverse_target_word_index[sampled_token_index]
        
        if(sampled_token!='eostok'):
            decoded_sentence += ' '+sampled_token

        # Exit condition: either hit max length or find stop word.
        if (sampled_token == 'eostok'  or len(decoded_sentence.split()) >= (max_summary_len-1)):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1,1))
        target_seq[0, 0] = sampled_token_index

        # Update internal states
        e_h, e_c = h, c

    return decoded_sentence

def predict(raw_text):
    pd.set_option("display.max_colwidth", 200)
    warnings.filterwarnings("ignore")
    K.clear_session()
    input = data_preprocess(raw_text)
    model = keras.models.load_model('test_main_model.h5')
    encoder_model = keras.models.load_model('test_encoder_model.h5')
    decoder_model = keras.models.load_model('test_decoder_model.h5')
    pre_summary = decode_sequence(input[0], encoder_model, decoder_model)
    return pre_summary
    
print(predict("Lashkar-e-Taiba's Kashmir commander Abu Dujana, who was killed by security forces, said ""Kabhi hum aage, kabhi aap, aaj aapne pakad liya, mubarak ho aapko (Today you caught me. Congratulations)"" after being caught. He added that he won't surrender, and whatever is in his fate will happen to him. ""Hum nikley they shaheed hone (had left home for martyrdom),"" he added.\",\"Lashkar-e-Taiba's Kashmir commander Abu Dujana was killed in an encounter in a village in Pulwama district of Jammu and Kashmir earlier this week. Dujana, who had managed to give the security forces a slip several times in the past, carried a bounty of Rs 15 lakh on his head.Reports say that Dujana had come to meet his wife when he was trapped inside a house in Hakripora village. Security officials involved in the encounter tried their best to convince Dujana to surrender but he refused, reports say.According to reports, Dujana rejected call for surrender from an Army officer. The Army had commissioned a local to start a telephonic conversation with Dujana. After initiating the talk, the local villager handed over the phone to the army officer.""Kya haal hai? Maine kaha, kya haal hai (How are you. I asked, how are you)?"" Dujana is heard asking the officer. The officer replies: ""Humara haal chhor Dujana. Surrender kyun nahi kar deta. Tu galat kar rha hai (Why don't you surrender? You have married this girl. What you are doing isn't right.)""When told that he is being used by Pakistani agencies as a pawn, Dujana, who sounded calm and unperturbed of the situation, said ""Hum nikley they shaheed hone. Main kya karu. Jisko game khelna hai, khelo. Kabhi hum aage, kabhi aap, aaj aapne pakad liya, mubarak ho aapko. Jisko jo karna hai karlo (I had left home for martyrdom. What can I do? Today you caught me. Congratulations. ""Surrender nahi kar sakta. Jo meri kismat may likha hoga, Allah wahi karega, theek hai? (I won't surrender. Allaah would do whatever is there in my fate)"" Dujana went on to say. Dujana, who belonged to Pakistan, was Lashkar-e-Taiba's divisional commander in south Kashmir. He was among the top 10 terrorists identified by the Indian Army in Jammu and Kashmir.With a Rs 15 lakh bounty on his head, Dujana was labelled an 'A++' terrorist - the top grade which was also given to Burhan Wani.Security forces received inputs that during the last few days he was frequenting the houses of his wife Rukaiya and girlfriend Shazia. Police was keeping a watch on both the houses. when it was confirmed he was present in his wife's house, security forces moved in to trap him.ALSO READ:After Abu Dujana, security forces prepare new hitlist of most wanted terroristsAbu Dujana encounter: Jilted lover turned police informer led security forces to LeT commander"))