import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import itertools
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.metrics import classification_report
from jinja2 import Environment, FileSystemLoader

news = pd.read_csv('fake_or_real_news.csv', index_col=0)
# here we print isna function to check for NaN values and duplicated.sum to make sure there are no cloned rows
news.isna().sum()
news.duplicated().sum()

# we sort_index to sort in ascending parameter the dataframe by Index
news = news.sort_index(axis=0, ascending=True, inplace=False)

# we erase metadata and source for a less-biased response


def clean_source(texto):
    texto = str(texto)

    # Remove agency patterns like NEW YORK (Reuters) -
    texto = re.sub(r'^[A-Z\s]+?\s*\((REUTERS|AP|AFP)\)\s*-\s*',
                   '', texto, flags=re.IGNORECASE)

    # Erase "(Bloomberg) -" or alike
    texto = re.sub(r'^\s*.*?\((Bloomberg|Reuters|AP|AFP)\)\s*-\s*',
                   '', texto, flags=re.IGNORECASE)

    # Erase prefixes "Leave a reply"
    texto = re.sub(r'^Leave a reply\s+', '', texto, flags=re.IGNORECASE)

    # Erase prefixes "Next Prev Swipe left/right"
    texto = re.sub(r'^Next\s+Prev\s+Swipe\s+left/right\s*',
                   '', texto, flags=re.IGNORECASE)

    # Erase prefixes "Next Swipe left/right"
    texto = re.sub(r'^Next\s+Swipe\s+left/right\s*',
                   '', texto, flags=re.IGNORECASE)

    # Erase authors by name and surname
    texto = re.sub(r'\bby\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4}', '', texto)

    # to clean multiple blank spaces
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto


news['text'] = news['text'].apply(clean_source)

labels = news.label
# we use value_counts to get the total number of FAKE/REAL news
news_type = labels.value_counts()

# we sum all the news to create a column graph adding differentiated colors for the bars
total = news_type.sum()
colors = ["steelblue", "salmon"]

# we use matplotlib.pylot to create a visual graph that shows fake vs real news
plt.figure(figsize=(8, 5))
plt.title("Real vs. Fake news Distribution")
plt.xlabel("Type of new")
plt.ylabel("Amount of news")

bars = plt.bar(news_type.index, news_type.values, color=colors)

# we use the function for to give bar shape by height, % and width
for bar in bars:
    height = bar.get_height()
    percentage = (height / total) * 100
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{percentage:.1f}%",
        ha="center",
        va="bottom"
    )
plt.savefig('News_graph.png')

# we separate the data into two groups: one to train the model and another to test if it really learns to identify
x_train, x_test, y_train, y_test = train_test_split(
    news['text'], labels, test_size=0.2, random_state=7)


news_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
# fit and transform train set and then transform test set
news_vectorizer_train = news_vectorizer.fit_transform(x_train)
news_vectorizer_test = news_vectorizer.transform(x_test)


# initialize a SGDC classifier to train the model
Classifier = SGDClassifier(loss='hinge', penalty=None,
                           learning_rate='pa1', eta0=1.0, max_iter=50)
Classifier.fit(news_vectorizer_train, y_train)

# predict on the test set and calculate accuracy
y_pred = Classifier.predict(news_vectorizer_test)
y_score = Classifier.decision_function(news_vectorizer_test)
score = accuracy_score(y_test, y_pred)
print(f'Accuracy: {round(score*100, 2)}%')

# Generate the confusion matrix using the true labels and the model predictions
confusion = confusion_matrix(y_test, y_pred, labels=['FAKE', 'REAL'])
# Convert the confusion matrix into a DataFrame for easier reading and display
confusion_df = pd.DataFrame(confusion,
                            index=['FAKE', 'REAL'],
                            columns=['Prediction FAKE', 'Prediction REAL'])
print(confusion_df)

# Create a DataFrame that stores the test text, the real label, the predicted label, and the model score
results = pd.DataFrame({'text': x_test,
                        'Actual Label': y_test,
                        'Predicted Label': y_pred,
                        'Score': y_score})
# Keep only the rows where the prediction is different from the actual label
misclassified = results[results['Actual Label'] != results['Predicted Label']]
misclassified['Preview'] = misclassified['text'].str[:150] + '...'
# Create a confidence value based on the absolute value of the score
misclassified['Confidence'] = misclassified['Score'].abs().round(3)
misclassified = misclassified[['Preview', 'Actual Label',
                               'Predicted Label', 'Score', 'Confidence']]

# Keep only the rows where the prediction matches the actual label
correct_classified = results[results['Actual Label']
                             == results['Predicted Label']].copy()
correct_classified['Preview'] = correct_classified['text'].str[:150] + '...'
correct_classified = correct_classified[[
    'Preview', 'Actual Label', 'Predicted Label']]


# Filter the correctly classified examples where the news was actually FAKE and predicted as FAKE
correct_fake = correct_classified[
    (correct_classified['Actual Label'] == 'FAKE') &
    (correct_classified['Predicted Label'] == 'FAKE')
]

# Filter the correctly classified examples where the news was actually REAL and predicted as REAL
correct_real = correct_classified[
    (correct_classified['Actual Label'] == 'REAL') &
    (correct_classified['Predicted Label'] == 'REAL')
]


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)
pd.set_option('display.max_colwidth', 60)

print(misclassified.head(
    10).to_string(index=False))

# Count how many errors belong to each combination of actual label and predicted label
error_summary = misclassified.groupby(
    ['Actual Label', 'Predicted Label']
).size().reset_index(name='Count')

print(error_summary)

# Generate a classification report with precision, recall, f1-score, and support
report = classification_report(y_test, y_pred, output_dict=True)
report_df = pd.DataFrame(report).transpose()
print(report_df)


confusion_html = confusion_df.to_html(classes='table', border=0)
report_html = report_df.to_html(classes='table', border=0)
errors_html = misclassified.head(10).to_html(
    index=False, classes='table', border=0)
error_summary_html = error_summary.to_html(
    index=False, classes='table', border=0)
correct_fake_html = correct_fake.head(10).to_html(
    index=False, classes='table', border=0)
correct_real_html = correct_real.head(10).to_html(
    index=False, classes='table', border=0)

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('news_report.j2')

html_out = template.render(
    accuracy=round(score * 100, 2),
    confusion_table=confusion_html,
    report_table=report_html,
    error_summary_table=error_summary_html,
    misclassified_table=errors_html,
    correct_fake_table=correct_fake_html,
    correct_real_table=correct_real_html,
    chart_path='News_graph.png'
)

with open('news_report.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

# Save the trained TF-IDF vectorizer so it can be reused later without having to fit it again on the training data
joblib.dump(news_vectorizer, 'vectorizer.pkl')
# Save the trained classifier to disk so it can be loaded later and used to predict new news articles without retraining the model
joblib.dump(Classifier, 'classifier.pkl')

print("HTML report generated: news_report.html")
print("Model saved: vectorizer.pkl and classifier.pkl")
