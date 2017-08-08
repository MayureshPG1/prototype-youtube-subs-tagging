About
-----
This is a prototype for automatically tagging youtube videos to 2-3 primaray topics of importance. The targetted videos for prototype shoube be of two to three people having a conversation. 

> The tags are generated for conversation content only. No other data
> from videos will be used for tagging.

It is expected that user will train the model with manually inputed tags and this model will be used for testing.
The prototype is build in python using scikit-learn machine learning library.

Usage
-----
**For training:**

 - Create Train folder at root directory
 - Run VBB_Train.py file

Usage: *VBB_Train.py [options]*
Options:
  **-h, --help**   show this help message and exit
  **-g, --generate**  Generate Training data by reading TrainData.txt from root  folder. 
TrainData.txt is csv file with each row in format: youtube_url, tag1, tag2, tag3 etc.
  **-t, --train**     Execute training with generated trained data. The training data must be generated before calling this option
 

> It is expected that user will manually create TrainData.txt file. And
> tags in TrainData.txt belong to dbpedia ontology.

**For Testing:**

 - Create a Test folder at root directory
 - Run VBB_Test.py file
 
Usage:  *VBB_Test.py <youtube_url>*

The console window will show matched output tags.

Dependencies
------------
 - **python 2.7.13**
 - **youtube-dl** utility. It's executable is included in the root folder. [https://github.com/rg3/youtube-dl]
 - **numpy** python module [http://www.numpy.org/]
 - **scikit-learn** python machine learning module [http://scikit-learn.org/stable/]
  
 

Design Notes
------------
The problem to be solved can be catagories as multi-label text classification. Where in each conversation can have one-more tags associated with it.

LinearSVM classifier is used for as it performed the best results.
To have multi-label output One vs Rest approach is applied.

Youtube subtitles are download and saved. To cleanup the subtitles text preprocessing pipeline is applied. Cleaned up subtitles are saved as temparory files in /Train folder.

For creating features from input text common english stop words are removed and TF-IDF is applied.

After performing training, the trained model is saved in /Train folder. This model is loaded back while performing test.


Notes
-----

 - Partial/batch training is not supported. For large datasets this could save a lot of memory but is deemed to be out of scope right now.
 - It is expected that the tags in TrainData.txt are of dbpedia ontology. Ideally user should describe the content in natural language and a routine will figure out the dbpedia tags. I've written a function `mapUserTagToDBPediaOntology(tag)` but could not figure out exact algorithm for mapping. In current form this function uses SPARQL to query dbpedia. And fetches uri's matching with natural text. From those uri's it figures out subjects of each topic and out of these subjects we should get our ontology tags.
 - I've not extensively trained the model. But, for 30-40 videos the results are ok. No quantification of precision, recall, f1-scoere etc. is done.