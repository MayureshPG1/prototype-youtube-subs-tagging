import subprocess
import csv
import os
import sys
from optparse import OptionParser

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
import pickle

import VBB_CleanupSubs as cleanup
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3

def generateTrainingData():
    """Script to read Traindata.txt file and get each youtube video link and save it's subtitles to Train folder"""
    
    # delete all files from last training session
    print 'Removing old training data...'
    foldername = training_data_folder + '/'
    files = os.listdir(foldername)
    for file in files:
        os.remove(foldername + file) 

    print 'Downloading subtitles/cc data...'
    lines = []
    try:
        f = open(training_data_file, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    lines.append(row)
        except Exception as e:
            print 'failed to read training data file'
            raise
        finally:
            f.close()
    except IOError:
        print 'could not load training data file'
        return

    script_name = cur_working_dir + '/youtube-dl '
    flags = '--write-auto-sub --skip-download --sub-lang en '

    index = 0
    for line in lines:
        cmd_name = script_name + flags + ' -o ' + '"' + training_data_folder + '/' + str(index) + '" ' + line[0]
        output = subprocess.check_output(cmd_name, stderr=subprocess.STDOUT, shell=True)
        print output
        index = index + 1

    print 'Cleaning up subtitles/cc data...'
    # remove extra metadata from subs
    cleanup.cleanupSubsFromFolder(training_data_folder)

def performTraining():
    """Read *.tmp.txt files and perform training """

    try:
        print 'Extracting training data...'
        training_data = populateTrainingData()
        print 'Extracting training targets data...'
        training_targets = populateTrainingTargets()
    except Exception as e:
        print 'failure in loading training data'
        return

    print 'Performing training routine...'

    try:
        mlb = MultiLabelBinarizer()
        target_matrix = mlb.fit_transform(training_targets)

        count_vec = CountVectorizer(stop_words='english',lowercase=True)
        training_data_vec = count_vec.fit_transform(training_data)

        tfidf_trans = TfidfTransformer()
        training_data_vec_tfidf = tfidf_trans.fit_transform(training_data_vec)

        classifier = OneVsRestClassifier(LinearSVC())
        classifier.fit(training_data_vec_tfidf,target_matrix)
    except Exception as e:
        print 'Failed to train model'
        raise
    
    print 'Dumping trained model...'
    # dump the trained data for future use
    try:
        fout = open(training_data_folder + '/TrainedModel.pkl', 'wb')
        try:
            pickle.dump((count_vec, classifier, mlb), fout)
        except Exception as e:
            print 'failed to dump trained model'
            raise
        finally:
            fout.close()
    except IOError:
        print 'could not save trained model'
        return

def populateTrainingTargets():
    """Reads TrainingData.txt file and gets tags for each video """
    try:
        f = open(training_data_file, 'rt')
        lines = []
        try:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    lines.append(row)
        except Exception as e:
            print 'failed to load training targets'
            raise
        finally:
            f.close()
    except IOError:
        print 'could not load training data file'
        raise

    targets = []
    for line in lines:
        tags = []
        count = 0
        for t in line:
            if count == 0:
                count = count + 1
                continue
            else:
                tags.append(t)
        targets.append(tags)

    return targets

def populateTrainingData():
    """Reads all *.tmp.txt files from /Train folder and loads training data from each file"""
    foldername = training_data_folder + '/'
    files = os.listdir(foldername)
    files_tmp = [f for f in files if f.endswith('.tmp.txt')]

    old_data = np.empty((0))
    for file in files_tmp:
        try:
            f = open(foldername + file,"rt")
            try:
                new_data = f.read()
                new_data = np.append(old_data,new_data)
                old_data = new_data
            except Exception as e:
                print 'failed to load training data'
                raise
            finally:
                f.close()
        except IOError:
            print 'could not load tmp.txt file'
            raise

    return new_data



def main():
    global cur_working_dir
    cur_working_dir = os.getcwd()

    global training_data_folder
    training_data_folder = cur_working_dir + '/Train'
    
    global training_data_file
    training_data_file = cur_working_dir + '/Traindata.txt'

    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--generate",
                      dest="generateTrainingData",
                      action="store_true",
                      help="Generate Training data by reading TrainData.txt from root folder."
                      "TrainData.txt is csv file with each row in format: youtube_url,tag1,tag2,tag3")
    parser.add_option("-t", "--train",
                      dest="train",
                      action="store_true",
                      help="Execute training with generated trained data. The training data must be generated before calling this option")

    options,arguments = parser.parse_args()

    if len(sys.argv[1:]) == 0:
        parser.print_help()

    if options.generateTrainingData:
        generateTrainingData()
        print 'Training data generation completed!'

    if options.train:
        performTraining()
        print 'Training completed!'

if __name__ == '__main__':
    main()

def mapUserTagToDBPediaOntology(tag):
    """"To be completed. Do not use."""
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    
    # query dbpedia for all the uri entries which contain user given tag
    uri_query = """SELECT ?uri ?txt WHERE {
                  ?uri rdfs:label ?txt .
                  ?txt bif:contains "'REPLACE_TAG'" .}"""
    
    new_uri_query = uri_query.replace('REPLACE_TAG',tag)
    sparql.setQuery(new_uri_query)
    sparql.setReturnFormat(XML)
    results = sparql.query().convert().toxml()

    # for each returned uri query to get subjects associated with it
    sparql.setQuery("""
        PREFIX  dbo:  <http://dbpedia.org/ontology/>
        PREFIX  dcterms: <http://purl.org/dc/terms/>

        SELECT * WHERE
          { <http://dbpedia.org/resource/REPLACE_URI> (dbo:wikiPageRedirects)*/(dbo:wikiPageDisambiguates)* ?page
            OPTIONAL
              { ?page dcterms:subject ?categoryUri}
          }
    """)
    sparql.setReturnFormat(XML)
    results = sparql.query().convert().toxml()
    
    # ideally make a histogram of all the subjects across uri. 
    # The first 3 of subjects by number should be dbpedia context aware ontology for a given conversation 
