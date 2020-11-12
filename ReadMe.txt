Dataset: The  model can be used to extract keyfeatures from a resume text.It used SpaCy library and its NER methods 
for extracting the details from the resume. The Main Challenge was the absence of annotated data for training the model.
This model uses resume dataset from indeed.com which is a popular jobsearching portel.This JSON  dataset contains
a set of 220 resume bodies with annotations of different entities.

Approach : The next step is to convert the dataset into a format supported by spaCy.For this, a seperate function was written.
then the data is splitted into train and test dataset using sklearns train_test_split function.Then the train data is used to
train the model.After training the model was saved to disk

Output : The model performance is demonstrated by feeding random text input from the test data and print the extracted details using
the trained model. 

Notes : The model performes well with the data from test set which is in the same format of train data. but some times the model
fails to perform well with custom inputs.This is not because the model overfitted but this is because we cannot provide diverse
dataset to the model.since all the data came from indeed.com it allways follows somewhat similar pattern, not the exact pattern
but something similar. if we get more diverse annotated data surely the model performs well. 

Whats next : Get  more quality data and improve the model. Either we can manually annotate data but it takes more time and the will not completed
within  short time.Also we can check another approches in nlp too like transformers etc.

The orginal coding performed on google colab and saved in colab ipynb format.Also a .py version is attached
.please use colab for better performance.

 
