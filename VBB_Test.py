import subprocess
import os
import sys
import pickle
import numpy as np
import VBB_CleanupSubs as cleanup
from optparse import OptionParser

def testUrl(youtube_url):
    """Downloads youtube url and performs match on trained data."""
    print 'Downloading subtitles/cc data...'
    cur_working_dir = os.getcwd()
    test_data_folder = cur_working_dir + '/Test'
    training_data_folder = cur_working_dir + '/Train'
    script_name = cur_working_dir + '/youtube-dl '
    flags = '--write-auto-sub --skip-download --sub-lang en '

    try:
        cmd_name = script_name + flags + ' -o ' + '"' + test_data_folder + '/' + 'Test' + '" ' + youtube_url
        output = subprocess.check_output(cmd_name, stderr=subprocess.STDOUT, shell=True)
        print output
    except Exception as e:
        print 'Could not download youtube subtitles'
        raise

    print 'Cleaning up subtitles/cc data...'
    cleanup.cleanupFile(test_data_folder + '/' + 'Test.en.vtt')

    print 'Loading trained model...'
    #load the trained moded and vectoriser
    try:
        fin = open(training_data_folder + '/TrainedModel.pkl', 'rb')
        try:
            count_vec, classifier, mlb = pickle.load(fin)
        except Exception as e:
            print 'failed to load trained model'
            raise
        finally:
            fin.close()
    except IOError:
        print 'trained model does not exist'
        return

    # load current url's data
    try:
        f = open(test_data_folder + '/' + 'Test.en.tmp.txt','rt')
        try:
            test_data = f.read()
        except Exception as e:
            print 'could not load test tmp file'
            raise
        finally:
            f.close()
    except IOError:
        print 'test tmp file does not exist'
        return

    print 'Performing match...'
    tmp_data_list = []
    tmp_data_list.append(test_data)
    test_data_np = np.array(tmp_data_list)
    test_data_transformed = count_vec.transform(test_data_np)
    predicted = classifier.predict(test_data_transformed)
    
    all_labels = mlb.inverse_transform(predicted)
    print 'Matched Tags are: '
    for label in all_labels:
        print label

def main():
    if len(sys.argv[1:]) == 0:
        print 'Usage is: VBB_Test.py <youtube_url>'
        return

    youtube_url = sys.argv[1] 
    testUrl(youtube_url)

if __name__ == '__main__':
    main()