import nltk
nltk.download('punkt')#Sentence tokenizer
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import json
import pickle
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
import random
import tkinter as tk
import matplotlib.pyplot as plt
words=[]
classes = []
documents = []
ignore_words = ['?', '!']
data_file = open('English.json').read() # read json file
intents = json.loads(data_file) # load json file

for intent in intents['intents']:
    for pattern in intent['patterns']:
        #tokenize each word
        w = nltk.word_tokenize(pattern)
        words.extend(w)# add each elements into list
        #combination between patterns and intents
        documents.append((w, intent['tag']))#add single element into end of list
        # add to tag in our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])
nltk.download('wordnet') #lexical database for the English language
nltk.download('omw-1.4')
# lemmatize, lower each word and remove duplicates
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
# sort classes
classes = sorted(list(set(classes)))
# documents = combination between patterns and intents
print (len(documents), "documents\n", documents, "\n")
# classes = intents[tag]
print (len(classes), "classes\n", classes, "\n")
# words = all words, vocabulary
print (len(words), "unique lemmatized words\n", words, "\n")
pickle.dump(words,open('words.pkl','wb'))
pickle.dump(classes,open('classes.pkl','wb'))
# Convert labels to unique values using LabelEncoder
# create our training data
training = []
# create an empty array for our output
output_empty = [0] * len(classes)
# training set, bag of words for each sentence
for doc in documents:
    # initialize our bag of words
    bag = []
    # list of tokenized words
    pattern_words = doc[0]
    # convert pattern_words in lower case
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # create bag of words array,if word match found in current pattern then put 1 otherwise 0.[row * colm(263)]
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    
    # in output array 0 value for each tag ang 1 value for matched tag.[row * colm(8)]
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    
    training.append([bag, output_row])
# shuffle training and turn into np.array
random.shuffle(training)
training = np.array(training)
# create train and test. X - patterns(words), Y - intents(tags)
train_x = list(training[:,0])
train_y = list(training[:,1])
print("Training data created")
from tensorflow.python.framework import ops
ops.reset_default_graph()
# Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
# equal to number of intents to predict output intent with softmax
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))
print("First layer:",model.layers[0].get_weights()[0])
# Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
# sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
#fitting and saving the model 
hist = model.fit(np.array(train_x), np.array(train_y), epochs=150, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)

print("model created")

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot Model Training Report")
        self.root.geometry("800x400")

        self.accuracy_label = tk.Label(root, text="Accuracy:")
        self.accuracy_label.pack()

        self.accuracy_value = tk.Label(root, text="0.00")
        self.accuracy_value.pack()

        self.loss_label = tk.Label(root, text="Loss:")
        self.loss_label.pack()

        self.loss_value = tk.Label(root, text="0.00")
        self.loss_value.pack()

        self.plot_button = tk.Button(root, text="Plot Accuracy and Loss", command=self.plot_graphs)
        self.plot_button.pack()

    def update_values(self, accuracy, loss):
        self.accuracy_value.config(text=f"{accuracy:.2f}")
        self.loss_value.config(text=f"{loss:.2f}")

    def plot_graphs(self):
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.plot(hist.history['accuracy'])  # Change 'history' to 'hist'
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')

        plt.subplot(1, 2, 2)
        plt.plot(hist.history['loss'])  # Change 'history' to 'hist'
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')

        plt.tight_layout()

        plt.show()

    
        
    # Create a plot of accuracy and loss
    

if __name__ == "__main__":
    root = tk.Tk()
    chatbot_gui = ChatbotGUI(root)

    final_accuracy = hist.history['accuracy'][-1]  # Change 'history' to 'hist'
    final_loss = hist.history['loss'][-1]  # Change 'history' to 'hist'
    chatbot_gui.update_values(final_accuracy, final_loss)

    root.mainloop()
