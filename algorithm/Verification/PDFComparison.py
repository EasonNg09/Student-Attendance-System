import subprocess
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

output1 = subprocess.check_output(['python', 'C:\FYPCode/algorithm\Verification\PDFExtract.py'], text=True)
output2 = subprocess.check_output(['python', 'C:\FYPCode/algorithm\Verification\PDFReader.py'], text=True)

# Tokenize the outputs into words using NLTK word_tokenize
words1 = word_tokenize(output1)
words2 = word_tokenize(output2)

# Calculate word similarity using TF-IDF and Cosine Similarity
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform([output1, output2])
cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
similarity_percentage = cosine_sim * 100

if similarity_percentage > 81:
    message = "Congratulations! You have completed the verification process."
else:
    message = "Sorry. Please try again."

print(f"Cosine Similarity Percentage: {similarity_percentage:.2f}%")
print(message)