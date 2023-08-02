# -*- coding: utf-8 -*-
"""AnalisisSentimenMAXIM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r2lztIyFA2nHaLRNHqiu0Y6B4hwb9WAN

# INSTALL LIBRARY
"""

!pip install googletrans==3.1.0a0
!pip install swifter
!pip install vaderSentiment

"""# IMPORT LIBRARY"""

# IMPORT LIBRARY

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#library untuk support library pandas (mempercepat waktu proses)
import swifter

#library untuk translete dataset
from googletrans import Translator

# library untuk pemrosesan dan analisis teks
import string
import re #Regex library = untuk melakukan search data
import nltk #nltk library = untuk memproses teks
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

# library vadersentiment untuk pelabelan data otomatis
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#library untuk melakukan tf-idf
from sklearn.feature_extraction.text import TfidfVectorizer

#library untuk melakukan pembagian data training dan test
from sklearn.model_selection import train_test_split

#library Naive Bayes multinomial
from sklearn.naive_bayes import MultinomialNB

#library random forest
from sklearn.ensemble import RandomForestClassifier

# Library Akurasi
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

#library untuk visualisasi dengan wordcloud
from wordcloud import WordCloud

#mengunduh kata tidak memiliki makna penting dan punkt
nltk.download('punkt')
nltk.download('stopwords')
print(stopwords.words('english'))

df = pd.read_csv('dataset_gplayID.csv') # Membaca atau import dataset dengan ekstensi .csv
df.head(5)

#Cek Tahun Hasil Penarikan Dataset

#mengubah kolom / atribut tanggal menjadi tipedata datetime
df['Tanggal'] = pd.to_datetime(df['at'])

# Tanggal pertama
tanggal_mulai = df['Tanggal'].min().date()

# Tanggal terakhir
tanggal_selesai = df['Tanggal'].max().date()

print("Data dimulai pada:", tanggal_mulai)
print("Data berakhir pada:", tanggal_selesai)

df.info() #cek berapa jumlah data pada dataset

"""# **PREPROCESSING**

## TRANSLETE DATASET
"""

translator = Translator()
df.loc[:,'content'] = df['content'].apply(lambda x: translator.translate(x, src='id', dest='en').text)
df.to_csv('dataset_gplayTRNSLTE.csv', index=False)

df.head(3)

"""## CLEANING DATA"""

df = pd.read_csv('dataset_gplayTRNSLTE.csv')
df.head(3)

#menghapus kolom yang tidak diperlukan
df = df.drop(['userImage', 'score', 'thumbsUpCount', 'reviewCreatedVersion', 'replyContent', 'repliedAt','appVersion'], axis=1)
df.head(5)

# Untuk Mengecek apakah ada data yang kosong / NaN pada dataset
df.isnull().any()
# jika hasil TRUE = ada data NaN / NULL. jika FALSE maka sebaliknya

# untuk membuat duplikasi kolom dan cek kolom sudah terbuat atau belum
df['cleaningdata'] = df['content']
df.info()

df.drop_duplicates(subset=['reviewId'], inplace=True)
df.info()

def remove_content_special(text):
  #Menghapus Tab, new line, dan back slice
  text = text = text.replace('\\t'," ").replace('\\n'," ").replace('\\u'," ").replace('\\',"")
  # Menghapus karakter non-ASCII (emoticon, chinese word, .etc)
  text = text.encode('ascii', 'replace').decode('ascii')
  #Menghapus mention, link, dan hashtag
  text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)"," ", text).split())
  #Menghapus URL yang tidak lengkap
  text = text.replace("http://", " ").replace("https://", " ")
  #Menghapus Angka
  text = re.sub(r"\d+", "", text)
  #Remove Punctuation untuk menghilangkan tanda baca seperti koma dan titik
  text = text.translate(str.maketrans("","",string.punctuation))
  #Remove whitespace pada awalan dan akhiran
  text = text.strip()
  #Mengganti multiple whitespace menjadi satu spasi
  text = re.sub('\s+',' ',text)

  return text

df['cleaningdata'] = df['cleaningdata'].apply(remove_content_special)

df[['content','cleaningdata']].head()

"""## CASEFOLDING"""

# str.lower untuk merubah setiap kalimat menjadi huruf kecil
df['casefolding'] = df['cleaningdata'].str.lower()
df[['content','casefolding']].head()

"""## TOKENIZING"""

# NLTK word rokenize
def word_tokenize_wrapper(text):
    return word_tokenize(text)

df['tokenizing'] = df['casefolding'].apply(word_tokenize_wrapper)

print('Tokenizing Result : \n')
print(df['tokenizing'].head())
print('\n\n\n')

df[['content','tokenizing']].head()

"""## FILTERING (Stopword removal)"""

stop_words = set(stopwords.words('english'))

df['filtering'] = df['tokenizing'].apply(lambda x: [word for word in x if word not in stop_words])
df[['content','filtering']].head()

"""## STEMMING"""

# create stemmer
stemmer = SnowballStemmer("english")

term_dict = {}

for document in df['filtering']:
    for term in document:
        if term not in term_dict:
            term_dict[term] = ' '

print(len(term_dict))
print("------------------------")

for term in term_dict:
    term_dict[term] = stemmer.stem(term)
    print(term,":" ,term_dict[term])

print(len(term_dict))
print("------------------------")
print(term_dict)
print("------------------------")


# apply stemmed term to dataframe
def get_stemmed_term(document):
    return [term_dict[term] for term in document]

df['stemming'] = df['filtering'].apply(get_stemmed_term)

df[['content','stemming']].head()

df.head()

df.info()

df.to_csv("dataset_gplayHASIL.csv")

"""# **pelabelan data**"""

df = pd.read_csv("dataset_gplayHASIL.csv")
analyser = SentimentIntensityAnalyzer()

# function to calculate vader sentiment
scores = [analyser.polarity_scores(x) for x in df['stemming']]
print(scores)
df['compound_scores'] = [x['compound'] for x in scores]

df[['stemming','compound_scores']].head()

# Membuat fungsi untuk mengubah nilai menjadi 3 label
def label_sentiment(score):
    if score <= -0.05:
        return 'negatif'
    elif score >= 0.05:
        return 'positif'
    else:
        return 'netral'

# Menerapkan fungsi pada kolom "compound_scores" untuk membuat kolom baru "sentiment"
df['sentiment'] = df['compound_scores'].apply(label_sentiment)

df[['stemming','compound_scores','sentiment']].head()

#menghitung jumlah sentimen
pos_label = df.loc[df['sentiment'] == 'positif'].shape[0]
neg_label  = df.loc[df['sentiment'] == 'negatif'].shape[0]
net_label = df.loc[df['sentiment'] == 'netral'].shape[0]

# Menghitung persentase
total_data = len(df)
pos_percentase = (pos_label / total_data) * 100
neg_percentase = (neg_label / total_data) * 100
neu_percentase = (net_label / total_data) * 100

# Menampilkan hasil
print("Persentase Label Sentiment:")
print(f"Positif: {pos_label} data {pos_percentase:.2f}%")
print(f"Negatif: {neg_label} data {neg_percentase:.2f}%")
print(f"Netral: {net_label} data {neu_percentase:.2f}%")

# Visualisasi Count Plot ( untuk menampilkan frekuensi masing-masing kategori dalam
# variabel kategorikal dalam bentuk bar chart) dengan Seaborn
count_data = sns.countplot(x='sentiment', data=df, palette = "Set2")

#memasukkan teks / angka pada tiap diagram
for p in count_data.patches:
    count_data.annotate(f'\n{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=12, color='white', xytext=(0,-10), textcoords='offset points')


# Menambahkan judul dan label sumbu
plt.title('Hasil Pelabelan Sentiment')
plt.xlabel('Sentimen')
plt.ylabel('Counts')

# Menampilkan grafik
plt.show()

df.to_csv("dataset_gplayLABEL_VADER.csv")

"""# PEMBAGIAN DATA TRAINING DAN DATA TEST"""

df = pd.read_csv("dataset_gplayLABEL_VADER.csv")

# Bagi data menjadi data training 80% dan data test 20%
x_train, x_test, y_train, y_test = train_test_split(df["stemming"], df["sentiment"], test_size=0.2, random_state=42)

# Menampilkan jumlah data train dan test pada kelas x dan y
print("Size of x_train: ", (x_train.shape))
print("Size of y_train: ", (y_train.shape))
print("Size of x_test: ", (x_test.shape))
print("Size of y_test: ", (y_test.shape))

"""# **TF-IDF**"""

#menggunakan TF-IDF
vector = TfidfVectorizer()
X_train_tfidf = vector.fit_transform(x_train)
X_test_tfidf = vector.transform(x_test)

"""# **NAIVE BAYES MULTINOMIAL**"""

# Proses Pelatihan untuk Model Naive Bayes
# Untuk Model Naive Bayes menggunakan rumus Multinomial

naivebayes = MultinomialNB()
naivebayes.fit(X_train_tfidf,y_train)

#note : menggunakan tf-idf -> pembagian data training & test -> model : 75.66% akurasi

# Proses Pengujian Model Naive Bayes
nb_pred = naivebayes.predict(X_test_tfidf)
nb_acc = accuracy_score(nb_pred, y_test)*100
print(f"Test Accuracy: {nb_acc}%")

#menampilkan hasil akurasi recall presisi dan f1-score
print("HASIL classification report")
print(classification_report(y_test, nb_pred))

#menampilkan hasil akurasi dengan confusion matriX
print("HASIL CONFUSION MATRIX")
confusionNB = confusion_matrix(y_test, nb_pred)
print(confusionNB,"\n")

"""## Visualisasi Naive Bayes"""

#menampilkan Hasil Klasifikasi sentimen dengan NAIVE BAYES
prednb = pd.DataFrame() #pembentukan dataframe sementara
prednb['content'] = x_test #untuk digunakan pada visualisasi wordcloud
prednb['sentiment'] = nb_pred #untuk digunakan menghitung label dan PIE CHART


#menghitung jumlah sentimen
pos_labelpie = prednb.loc[prednb['sentiment'] == 'positif'].shape[0]
neg_labelpie  = prednb.loc[prednb['sentiment'] == 'negatif'].shape[0]
net_labelpie = prednb.loc[prednb['sentiment'] == 'netral'].shape[0]

# Menghitung persentase
total_datapie = len(nb_pred)
pos_percentasepie = (pos_labelpie / total_datapie) * 100
neg_percentasepie = (neg_labelpie / total_datapie) * 100
neu_percentasepie = (net_labelpie / total_datapie) * 100

# Menampilkan hasil
print("Persentase Label Sentiment:")
print(f"Positif: {pos_labelpie} data {pos_percentasepie:.2f}%")
print(f"Negatif: {neg_labelpie} data {neg_percentasepie:.2f}%")
print(f"Netral: {net_labelpie} data {neu_percentasepie:.2f}%")

#PIE CHART
#deklarasi variabel untuk menentukan label dan presentase
labelNB = ['Positif','Negatif','Netral']
presentaseNB = [pos_labelpie, neg_labelpie, net_labelpie]
warnaNB=['#78B16B', '#EDEBE0','#828153']

# Membuat pie chart
plt.figure(figsize=(6, 6))
plt.title('Hasil Klasifikasi Dengan Naive Bayes (Pie Chart)')
plt.pie(presentaseNB, labels=labelNB,colors=warnaNB, autopct='%.2f%%', startangle=180)
plt.legend()

# Menampilkan pie chart
plt.show()

#HEATMAP
sns.heatmap(confusionNB, annot=True, cmap='Greens', fmt='d', xticklabels=['Negatif', 'Netral', 'Positif'],
            yticklabels=['Negatif', 'Netral', 'Positif'])
plt.title('Hasil Confusion Matrix Dari Klasifikasi Dengan Naive Bayes (Heatmap)\n')

#WORD CLOUD
# Membuat fungsi untuk menampilkan kata pada wordcloud
def wordcloud_nb(words):
    wordcloudNB = WordCloud(width=800, height=500, colormap='YlGn', background_color='black', random_state=42, max_font_size=100).generate(words)

    plt.figure(figsize=(9, 6))
    plt.imshow(wordcloudNB, interpolation='bilinear')
    plt.axis('off')


# Menampilkan wordcloud
all_wordsNB = ' '.join([text for text in prednb['content']])
wordcloud_nb(all_wordsNB)

#Wordcloud Sentiment positif
positif_wordsNB = ' '.join(text for text in prednb['content'][prednb['sentiment'] == 'positif'])
wordcloud_nb(positif_wordsNB)

#Wordcloud Sentiment negatif
negatif_wordsNB = ' '.join(text for text in prednb['content'][prednb['sentiment'] == 'negatif'])
wordcloud_nb(negatif_wordsNB)

#Wordcloud Sentiment netral
netral_wordsNB = ' '.join(text for text in prednb['content'][prednb['sentiment'] == 'netral'])
wordcloud_nb(netral_wordsNB)

"""# **RANDOM FOREST**"""

#membuat model untuk random forest dan melatihnya dengan data training
randomforest = RandomForestClassifier()
randomforest.fit(X_train_tfidf,y_train)

# Proses Pengujian Model Random Forest
rf_pred = randomforest.predict(X_test_tfidf)
rf_acc = accuracy_score(rf_pred, y_test)*100
print(f"Test Accuracy: {rf_acc}%")

#menampilkan hasil akurasi recall presisi dan f1-score
print("HASIL classification report")
print(classification_report(y_test, rf_pred))

#menampilkan hasil akurasi  dengan confusion matriX
print("HASIL CONFUSION MATRIX")
confusionRF = confusion_matrix(y_test, rf_pred)
print(confusionRF,"\n")

"""## Visualisasi Random Forest"""

#menampilkan Hasil Klasifikasi sentimen dengan NAIVE BAYES
predrf = pd.DataFrame() #pembentukan dataframe sementara
predrf['content'] = x_test #untuk digunakan pada visualisasi wordcloud
predrf['sentiment'] = rf_pred #untuk digunakan menghitung label dan PIE CHART

#menghitung jumlah sentimen
pos_labelpierf = predrf.loc[predrf['sentiment'] == 'positif'].shape[0]
neg_labelpierf = predrf.loc[predrf['sentiment'] == 'negatif'].shape[0]
net_labelpierf = predrf.loc[predrf['sentiment'] == 'netral'].shape[0]

# Menghitung persentase
total_datapierf = len(rf_pred)
pos_percentasepierf = (pos_labelpierf / total_datapierf) * 100
neg_percentasepierf = (neg_labelpierf / total_datapierf) * 100
neu_percentasepierf = (net_labelpierf / total_datapierf) * 100

# Menampilkan hasil
print("Persentase Label Sentiment:")
print(f"Positif: {pos_labelpierf} data {pos_percentasepierf:.2f}%")
print(f"Negatif: {neg_labelpierf} data {neg_percentasepierf:.2f}%")
print(f"Netral: {net_labelpierf} data {neu_percentasepierf:.2f}%")

#PIE CHART
#deklarasi variabel untuk menentukan label dan presentase
labelRF = ['Positif','Negatif','Netral']
presentaseRF = [pos_labelpierf, neg_labelpierf, net_labelpierf]
warnaRF=['#F4D96E', '#CAA38E','#9E6B4E']

# Membuat pie chart
plt.figure(figsize=(6, 6))
plt.title('Hasil Klasifikasi Dengan Random Forest (Pie Chart)')
plt.pie(presentaseRF, labels=labelRF,colors=warnaRF, autopct='%.2f%%', startangle=180)
plt.legend()

# Menampilkan pie chart
plt.show()

#HEATMAP
sns.heatmap(confusionRF, annot=True, cmap='YlOrBr', fmt='d', xticklabels=['Negatif', 'Netral', 'Positif'],
            yticklabels=['Negatif', 'Netral', 'Positif'])
plt.title('Hasil Confusion Matrix Dari Klasifikasi Dengan Random Forest (Heatmap)\n')

#WORD CLOUD
# Membuat fungsi untuk menampilkan kata pada wordcloud
def wordcloud_rf(words):
    wordcloudRF = WordCloud(width=800, height=500, colormap="YlOrBr" ,background_color='black', random_state=42, max_font_size=100).generate(words)

    plt.figure(figsize=(9, 6))
    plt.imshow(wordcloudRF, interpolation='bilinear')
    plt.axis('off')


# Menampilkan wordcloud
all_wordsRF = ' '.join([text for text in predrf['content']])
wordcloud_rf(all_wordsRF)

#Wordcloud Sentiment positif
positif_wordsRF = ' '.join(text for text in predrf['content'][predrf['sentiment'] == 'positif'])
wordcloud_rf(positif_wordsRF)

#Wordcloud Sentiment negatif
negatif_wordsRF = ' '.join(text for text in predrf['content'][predrf['sentiment'] == 'negatif'])
wordcloud_rf(negatif_wordsRF)

#Wordcloud Sentiment netral
netral_wordsRF = ' '.join(text for text in predrf['content'][predrf['sentiment'] == 'netral'])
wordcloud_rf(netral_wordsRF)