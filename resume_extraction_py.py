# -*- coding: utf-8 -*-
"""resume_extraction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1insglA6rBhKWtFZmYz1fL-TyYaXmGrMd
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install datefinder

import json
import random
import pandas as pd
import spacy
import datefinder

from sklearn.model_selection import train_test_split

#import data to a dataframe
data = pd.read_json('/content/drive/My Drive/mindpro/Entity Recognition in Resumes.json', lines = True)

"""The data we used to train the model is from indeed.com.It contains annotated resume details of 220 resumes. where the resume text and index annotations for different entities are given.lets take a look on the data"""

#Visualizing data
data.head()

#Dimension of data
print('Dimension of data:',data.shape)

"""the data provided in a clean format.So not much preproccessing required.lets check the null values"""

#checking any null values in dataframe
data.isna().sum()

"""The extras column contain only null values.but we dont use that column for training or evaluation purpose.so we can ignore that"""

#structure of annotation data
data['annotation'][0]

"""##Using spaCy custom Named Entity Recognition to extract details from the resume Text

But our Trainng data is not in a formt to directly applying to spaCy custom NER training pipeline. The statnderd form of spacy traing format is a list of tuple in the form [
[(text, {'entities : [(start_index, stop_index, Entity_name)],[(start_index, stop_index, Entity_name)]}),
(text, {'entities : [(start_index, stop_index, Entity_name)]})
...
]
So we first convert our dataset into this format. This is done by the function spacyFormatConverter.
"""

#Function to convert our data into spacy format
def spacyFormatConverter(json_filepath):
    try:
        #List to store final training data
        training_data = []
        #open the training json file and store it in variable called lines 
        with open(json_filepath, 'r') as f:
            lines = f.readlines()
        #For every resume in the resume corpus
        for line in lines:
            #load details of the selected resume into variable named data
            data = json.loads(line)
            #clean the text content of resume by replacing \n character with space.
            text = data['content'].replace("\n", " ")
            #create a list to store entity details. thatis star and end indexes and entity name
            entities = []
            #take the annotations of the selected resume which is currently processing
            annotations = data['annotation']
            if annotations is not None:
                #for every annotation labels
                for annotation in annotations:
                    #only a single point in text annotation.
                    point = annotation['points'][0]
                    labels = annotation['label']
                    # handle both list of labels or a single label.
                    if not isinstance(labels, list):
                        labels = [labels]

                    #for every label  in the current resume
                    for label in labels:
                        #storing the start index in variable start
                        start = point['start']
                        #storing ending index in variable end
                        end = point['end']
                        #storing the text value for corresponding entity.this is only stored for whitespace adjustments
                        text_entity = point['text']
                        #This lstrip, rstrip adjustments done for adjusting the index for eliminating  whitespaces in the output
                        lstrip_diff = len(text_entity) - len(text_entity.lstrip())
                        rstrip_diff = len(text_entity) - len(text_entity.rstrip())
                        if lstrip_diff != 0:
                            start = start + lstrip_diff
                        if rstrip_diff != 0:
                            end = end - rstrip_diff
                        #append start, end indexes(end index is excluding thus add 1) and label in a form of tuple to the entity list
                        entities.append((start, end + 1 , label))
            #append resume text and entities to the final traing data list
            training_data.append((text, {"entities" : entities}))
        #retuen the final list
        return training_data
    except Exception as e:
        #if an exception raised then print the details  
        logging.exception("Unable to process " + json_filepath + "\n" + "error = " + str(e))
        return None

#store the formatted clean data into formatted_data variable
formatted_data = spacyFormatConverter('/content/drive/My Drive/mindpro/Entity Recognition in Resumes.json')

#split the data into training and testing set
train_data, test_data = train_test_split(formatted_data, random_state = 77)
print('train data shape :', len(train_data))
print('test data shape :', len(test_data))

train_data[0]

test_data[0]

"""Now the data has been cleaned and formatted

##Training the Model
we use spacy library for training the data and building the model.
"""

#load a blank spacy model for our custom entity recognition
cer = spacy.blank('en')
#function to train the model
def train_model(train_data):
    #if ner(named entity recognition) not in our pipeline names create ner and add to the pipeline
    if 'ner' not in cer.pipe_names:
        ner = cer.create_pipe('ner')
        cer.add_pipe(ner, last = True)
    
    for text, annotation in train_data:
        #for every entity in entities
        for entity in annotation['entities']:
            #add entity name(the format is (start, end, entity_name) so entity[2] used)
            ner.add_label(entity[2])
            
    
    other_pipes = [pipe for pipe in cer.pipe_names if pipe != 'ner']
    #only train NER,   disable all other pipelines
    with cer.disable_pipes(*other_pipes):
        #optimizer  
        optimizer = cer.begin_training()
        #training iterations
        for i in range(15):
            print("Statring iteration " + str(i))
            #shuffle training data for reduce overfitting
            random.shuffle(train_data)
            #dict to store losses
            losses = {}
            #for every items
            for text, annotations in train_data:
                try:
                    #training the model
                    cer.update(
                        [text], #batch of texts
                        [annotations],  #batch of annotations
                        drop=0.2,  # dropout - prevent overfitting
                        sgd=optimizer,  #  update weights
                        losses=losses)
                except Exception as e:
                    pass   
            print(losses)

#train the model using training_data
train_model(train_data)

#save the model for further use
cer.to_disk('resume_extractor')

#load the pretrained model
resume_parser = spacy.load('resume_extractor')

"""##Demostrating Performance"""

#demonstrating  : sample 1
print('Sample 1')
#any randominput  text  from  test data
rand = random.randint(0, len(test_data)-1)
print('Resume data to be extracted : \n', test_data[rand][0])
print('\n Resume details'.upper())
doc = resume_parser(test_data[rand][0])
#data parsed out from the resume
for ent in doc.ents:
    print(f'{ent.label_.upper():{20}}- {ent.text}')

#demonstrating performance : sample 2
print('sample 2')
#any randominput  text  from  test data
rand = random.randint(0, len(test_data)-1)
print('Resume data to be extracted : \n', test_data[rand][0])
print('\n Resume details'.upper())
doc = resume_parser(test_data[rand][0])
#data parsed out from the resume
for ent in doc.ents:
    print(f'{ent.label_.upper():{20}}- {ent.text}')

