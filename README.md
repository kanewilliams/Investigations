# Kindle Review Investigation

(Note: Please see [the .ipynb](kindle_review_investigation.ipynb) for more information)

## Executive Summary (Spoilers!)

In this analysis I attempt to predict a book's "`helpfulness`" rating (created from the `helpful` stat) by using various features of the text, and the following fairly-interpretable models:
  - Decision Trees (standard)
  - Random Forests
  - Naive Bayes bag-of-words models + Wordclouds

**If you want a high "helpful" score on a kindle review:**

- Use **longer reviews**.
- Give a **high score.** *
- **Use the following words** (presumably if applicable): "serial killer", "murder", "easy", "fun", "recommended", "love scene", "demon"
- Provide more emotionally charged answers (**higher sentiment**)

For more information, scroll down and see:
1) Word Cloud
2) Interpretation of Decision Tree

These were the most informative models. Limitations apply.

(*) Presumably only for those books that deserve one.

## Distribution of "Helpfulness" of a review (Target Variable)

![image](https://github.com/user-attachments/assets/83d52a44-4d10-4c89-89ac-bafb0a496400)

## Review Score against Helpfulness

![image](https://github.com/user-attachments/assets/4aa39695-5968-475f-8787-bf7225a07f6e)

## Decision Tree with Helpfulness as target

![image](https://github.com/user-attachments/assets/de827071-b214-4138-b3b8-7578d486c79d)

### Interpretation

As we would expect (and it's quite nice that it is what we expected), the decision tree picks out the fact that score is bi-modal, and splits based on positive and negative scores.

- If the score < 2.5 (low score), then:
  - Having a small review_length (< 120) is predictive of not being not very helpful (helpfulness: 40-60).
  - Having a higher review_length predicts higher helpfulness (70-80).

- If the score > 2.5 (high score), then:
  - The next important thing is whether the score is a high (4, 5) or middling (3) score.
    - Scores of 4 or 5 benefit **greatly** from having a higher review_length. (helpfulness of 20 vs 85)  
    - Scores of 3 generally get the **best** helpfulness overall, particular if they are longer than 50 words (**92**!). 
    - (NOTE: scores of 3 may be more nuanced and trustworthy since they don't just blindly click a score of "1" or "5")

## Feature Importances (using Random Forest)

![image](https://github.com/user-attachments/assets/0fb1dc53-5af2-450b-8e46-508bc070ca10)

As with a standard decision tree, we see that:
- (1) score and 
- (2) review_length are the most important when it comes to helpfulness.

Using long words followed by the sentiment of the review are important.

## Words used in Helpful Reviews

### 1-grams
![image](https://github.com/user-attachments/assets/62a5af5a-9c22-4ad7-a851-810a288b4ba8)

Top 15 most helpful words/phrases:
highly recommend: 1.5374
collection: 1.4394
mystery: 1.3142
screen: 1.1944
laugh: 1.1899
twists: 1.1814
recommended: 1.1395
fun: 1.1011
highly: 1.0971
excellent: 1.0056
quick: 0.9938
easy: 0.9754
suspense: 0.9705
war: 0.9366
amazing: 0.9298

### 2-grams

![image](https://github.com/user-attachments/assets/3796c1f1-e52f-4703-9bb6-0906320bdd91)

Top 15 most helpful words/phrases:
serial killer: 2.0355
highly recommended: 1.7354
highly recommend: 1.4805
characters developed: 1.4477
fast paced: 1.4188
new series: 1.3964
laugh loud: 1.2852
good job: 1.2246
screen protector: 1.2246
love scenes: 1.1601
read series: 1.1601
quick read: 1.1376
loved story: 1.0911
turning pages: 1.0911
honest review: 1.0800

"Serial Killer" is overwhelmingly important! Apart from murder-mystery, books with love scenes seem to be important. And I wonder why "Screen protector" was picked up... hmm... uhh..

The conclusions are clear..!:
1) Write reviews for mystery books about serial-killers!
2) Also, use the words "fun, easy, recommended"
3) Talk about the love scene (if there is one), and demons (if they exist).

In all seriousness, we must take some of these with a grain of salt:
  - It is possible that Mystery and Love stories are over-represented in the filtered (>20 helpful ratings) dataset.
  - Likewise, most of the reviews are positive anyway, so we would expect that they would prominently feature in the word clouds even if we choose words are random.
  - More experimentation with the featuers on the Vectorizer (max_features, e.t.c.) and splitting the dataset by category could help soften these issues.

## Model Optimizing + Limitations

We could try to make our above solutions better by:
- Removing stopwords (especially before the naive "word complexity" feature is added.)
- Using a more refined "word complexity" algorithm. (see Claude's suggestions in the beginning)
- Adding/substituting another more robust sentiment analysis method (e.g. querying a LLM "Hey ChatGPT, is this a positive or negative review? Score it!")
- More feature engineering, e.g. separating between high and low scores/sentiments.
- **Applying the model category-wise** (Helpful science fiction reviews may be different than helpful self-help reviews) **(I reckon this would help the most and be the most informative)**
- Trying to incorporate other features I ignored, such as:
   - Author Popularity (authors who post a lot may be more helpful?)
   - Day of Year and/or Day of Week the review is posted. Maybe posts around Christmas are more positive?
   - Book popularity (how common are reviews for the book?)
 
# Conclusion

**If you want a high "helpful" score on a kindle review:**

- Use longer reviews.
- Give a high score.
- Use the following words (presumably if applicable): "serial killer", "murder", "easy", "fun", "recommended", "love scene", "demon"
- Provide more emotionally charged answers (higher sentiment)

(Take above answers with a grain of salt. Limitations apply)

