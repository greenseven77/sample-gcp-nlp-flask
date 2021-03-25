# Import google-cloud-language
# Make sure that you have installed or upgraded to the latest google-cloud-language using pip
from google.cloud import language_v1 as language
import pandas as pd
import numpy as np

#Print all columns and all rows in a panda dataframe
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


# Module to give 'sentiment' results:
# take a sentence, run the module, result back:
# 1. original text; 
# 2. sentiment score -- between -1 to 1
# 3. sentiment magnitude -- absolute value of the score, but will agrregate
def analyze_text_sentiment(text):
    client = language.LanguageServiceClient()
    document = language.Document(content=text, type_=language.Document.Type.PLAIN_TEXT)

    response = client.analyze_sentiment(document=document)

    sentiment = response.document_sentiment
    results = dict(
        text=text,
        score=f"{sentiment.score:.1%}",
        magnitude=f"{sentiment.magnitude:.1%}",
    )
    
    # Get sentiment for all sentences in the document
    sentence_sentiment = []
    for sentence in response.sentences:
        item={}
        item["text"]=sentence.text.content
        item["sentiment score"]=sentence.sentiment.score
        item["sentiment magnitude"]=sentence.sentiment.magnitude
        sentence_sentiment.append(item)
    
    return sentence_sentiment

# return results by sentence
def save_sentiment_to_df (text):
    df_sentiment=pd.DataFrame(analyze_text_sentiment(text))
    return df_sentiment

# get text from a file
def get_text_from_file (file_name):
    #open text file in read mode
    text_file = open(file_name, "r")
    
    #read whole file to a string
    data = text_file.read()

    #close file
    text_file.close()

    return data

#Get basic information
def get_basic_info(file_name):
    text = get_text_from_file (file_name)
    # create the result into dataframe for further info
    df_text_sentiment_stats = save_sentiment_to_df(text)
    df_text_sentiment_stats.reset_index(inplace=True)
    # 1. how many sentense?
    cnt_sentences = df_text_sentiment_stats.shape[0]
    print("There are total of ", cnt_sentences, " sentences in the artical.")
    # 2. The sentiment score of each sentence:
    #print(df_text_sentiment_stats['sentiment score'])
    
    return df_text_sentiment_stats['sentiment score']