import os

import pandas as pd
import numpy as np
# import plotly as py

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import (
    Flask, 
    jsonify, 
    render_template, 
    request, 
    redirect)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///db/lyricsupdated.sqlite"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
Samples_Metadata = Base.classes.sample_metadata
Samples = Base.classes.samples


@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")


@app.route("/names")
def names():
    """Return a list of sample names."""

    # Use Pandas to perform the sql query
    stmt = db.session.query(Samples_Metadata).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Return a list of the column names (sample names)
    return jsonify(list(df.Era.unique()))

@app.route("/artists/<sample>")
def artists(sample):
    """Return a list of artists names."""
    sel = [
        Samples_Metadata.sample,
        Samples_Metadata.Genre,
        Samples_Metadata.Artist,
        Samples_Metadata.Song,
        Samples_Metadata.Year,
        Samples_Metadata.Decade,
        Samples_Metadata.Era,
        Samples_Metadata.Lyrics,
    ]

    results = db.session.query(*sel).filter(Samples_Metadata.Era == sample).all()

    # print(results)
    # print(results[5])

    # Create a dictionary entry for each row of metadata information
    sample_metadata_list = []
    
    for result in results:
        sample_metadata = {}
        # sample_metadata["sample"] = result[0]
        # sample_metadata["Genre"] = result[1]
        sample_metadata["Artist"] = result[2]
        # sample_metadata["Song"] = result[3]
        # sample_metadata["Year"] = result[4]
        # sample_metadata["Decade"] = result[5]
        # sample_metadata["Era"] = result[6]
        # sample_metadata["Lyrics"] = result[7]

        sample_metadata_list.append(sample_metadata)
        
    print(sample_metadata_list)
    return jsonify(sample_metadata_list)

@app.route("/metadata/<sample>")
def sample_metadata(sample):
    """Return the MetaData for a given sample."""
    sel = [
        Samples_Metadata.sample,
        Samples_Metadata.Genre,
        Samples_Metadata.Artist,
        Samples_Metadata.Song,
        Samples_Metadata.Year,
        Samples_Metadata.Decade,
        Samples_Metadata.Era,
        Samples_Metadata.Lyrics,
    ]

    results = db.session.query(*sel).filter(Samples_Metadata.Era == sample).all()

    # print(results)
    # print(results[5])

    # Create a dictionary entry for each row of metadata information
    sample_metadata_list = []
    
    for result in results:
        sample_metadata = {}
        # sample_metadata["sample"] = result[0]
        sample_metadata["Genre"] = result[1]
        sample_metadata["Artist"] = result[2]
        sample_metadata["Song"] = result[3]
        sample_metadata["Year"] = result[4]
        # sample_metadata["Decade"] = result[5]
        # sample_metadata["Era"] = result[6]
        # sample_metadata["Lyrics"] = result[7]

        sample_metadata_list.append(sample_metadata)
        
    print(sample_metadata_list)
    return jsonify(sample_metadata_list)


@app.route("/samples/<sample>")
def samples(sample):
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    stmt = db.session.query(Samples).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Filter the data based on the sample number and
    # only keep rows with values above 1
    sample_data = df.loc[df[sample] > 1, ["otu_id", "otu_label", sample]]
    # Format the data to send as json
    data = {
        "otu_ids": sample_data.otu_id.values.tolist(),
        "sample_values": sample_data[sample].values.tolist(),
        "otu_labels": sample_data.otu_label.tolist(),
    }
    return jsonify(data)

@app.route("/charts/<sample>")
def chart_data(sample):
    """Return the data for the song chosen by the user"""
    sel = [
        Samples_Metadata.sample,
        Samples_Metadata.Genre,
        Samples_Metadata.Artist,
        Samples_Metadata.Song,
        Samples_Metadata.Year,
        Samples_Metadata.Decade,
        Samples_Metadata.Era,
        Samples_Metadata.Lyrics
    ]

    results = db.session.query(*sel).filter(Samples_Metadata.Era == sample).all()

    song_metadata_list = []
    
    # song_genre = [result[1] for result in results]


    # song_era = [result[6] for result in results]
    # trace = {
    #         "labels": song_genre,
    #         "values": song_genre,
    #         "type": "pie"      
    # }
    song_metadata = {}
    for result in results:
    #     # song_metadata["sample"] = result[0]
        if result[1] in song_metadata:
            song_metadata[result[1]]+=1
        else:
            song_metadata[result[1]]=1

        # song_metadata["Genre"] = result[1]
    #     # song_metadata["Artist"] = result[2]
    #     #song_metadata["Song"] = result[3]
    #     # song_metadata["Year"] = result[4]
    #     song_metadata["Era"]= result[6]
    #     # song_metadata["Lyrics"] = result[7]
        # song_metadata_list.append(song_metadata)
    
    # print(song_metadata_list)
    return jsonify(song_metadata)

@app.route("/linecharts")
def line_data():
    df= pd.read_csv('C:/Users/trevo/Desktop/UNCCDataAn/Projects/Project2/Resources/compression_score.csv')
    compress_list=df.groupby("Year").mean()["compress_score"].values.tolist()
    years=df["Year"].unique()
    years_list=years.tolist()

    compression_data= {
        "compression": compress_list,
        "Year" : years_list
    }

    return jsonify(compression_data)

if __name__ == "__main__":
    app.run(port=5001)

