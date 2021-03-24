from datetime import datetime
import pandas as pd
import logging
import os

from flask import Flask, redirect, render_template, request

from google.cloud import datastore
from google.cloud import language_v1 as language




app = Flask(__name__)


@app.route("/")
def homepage():
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # # Use the Cloud Datastore client to fetch information from Datastore
    # Query looks for all documents of the 'Sentences' kind, which is how we
    # store them in upload_text()
    query = datastore_client.query(kind="Sentences")
    text_entities = list(query.fetch())

    # # Return a Jinja2 HTML template and pass in text_entities as a parameter.
    return render_template("homepage-fei.html", text_entities=text_entities)


@app.route("/upload", methods=["GET", "POST"])
# instead of giving back positive or negative, give back the exact number of sentiment
def upload_text():
    text = request.form["text"]

    # Analyse sentiment using Sentiment API call
    sentiment = analyze_text_sentiment(text)[0].get('sentiment score')
    
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch the current date / time.
    current_datetime = datetime.now()

    # The kind for the new entity. This is so all 'Sentences' can be queried.
    kind = "Sentences"

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key(kind, 'sample_task')

    # Alternative to above, the following would store a history of all previous requests as no key
    # identifier is specified, only a 'kind'. Datastore automatically provisions numeric ids.
    # key = datastore_client.key(kind)

    # Construct the new entity using the key. Set dictionary values for entity
    entity = datastore.Entity(key)
    entity["text"] = text
    entity["timestamp"] = current_datetime
    entity["sentiment"] = sentiment

    # Save the new entity to Datastore.
    datastore_client.put(entity)

    # test save results to a csv
    save_txt_sentiment_to_csv(text, sentiment)
    
    # Redirect to the home page.
    return redirect("/")

def save_txt_sentiment_to_csv(text, sentiment):
    # list of name, degree, score 
    txt = ["i am happy", "a cup of tea", "not nice", "pretty"] 
    senti = [0.5, 0, -0.3, 0.36] 

    # dictionary of lists  
    dict = {'text': txt, 'sentiment': senti}  

    df = pd.DataFrame(dict) 

    # saving the dataframe 
    df.to_csv('text_sentiment_data.csv') 

@app.errorhandler(500)
def server_error(e):
    logging.exception("An error occurred during a request.")
    return (
        """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(
            e
        ),
        500,
    )
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
    for k, v in results.items():
        print(f"{k:10}: {v}")

    # Get sentiment for all sentences in the document
    sentence_sentiment = []
    for sentence in response.sentences:
        item={}
        item["text"]=sentence.text.content
        item["sentiment score"]=sentence.sentiment.score
        item["sentiment magnitude"]=sentence.sentiment.magnitude
        sentence_sentiment.append(item)

    return sentence_sentiment


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

# visualization (code test) 
def text_sentiment_line_chart(df_sentiment_score):
    df_sentiment_score.plot(kind='line', y='sentiment score', x=df_sentiment_score.index+1)

    # Build the chart graphic
    ax = plt.axes()
    ax.grid()
    ax.margins(0) # remove default margins (matplotlib verision 2+)
    ax.axhspan(0, 2.0, facecolor='bisque', alpha=0.5)
    ax.axhspan(-2.0, 0, facecolor='lightcoral', alpha=0.5)

    # Giving y label using xlabel() method 
    plt.ylabel("Sentiment Score", fontweight='bold')  
    # Giving title to the plot
    plt.title("Sentiment Score by Sentence", fontweight='bold')
    plt.show()
    
    

if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
