# Developing a machine learning-based instrument for subjective well-being assessment on Weibo and its psychological significance: An evaluative and interpretive research

## METHOD

## Data collection

The user data for this study were collected and processed in parallel with the data utilized in the previous study conducted between September 2012 and February 2013 (see [Han, Li, Huang, Wen, Wang, et al., 2023] for more details). We conducted data collection based on the convenience sampling method. The complete procedure is depicted in Figure 1. First, we ran domly sent invitations to approximately 20,000 Weibo users via private messages on the plat form. Subsequently, users who were willing to participate in our experiment were instructed to use our online experiment platform to provide informed consent and complete a psychological questionnaire, allowing us to access their SWB scores. Finally, the social media data of these users (Weibo posts since the account creation and user profiles) were downloaded via the Sina Weibo API. The online experiment needed to be completed in a single session without interruptions. We excluded users who (1) were disconnected or logged out in the middle, (2) were unde 18 years old, (3) did not have public Weibo accounts, and (4) declined to provide informed consent. 

Participants were informed that their participation was voluntary and that they could withdraw at any time. Users who completed the psychological questionnaire were given a monetary reward. All data were anonymized, and personal identifiers were removed to ensure confidenti ality. All users' privacy was strictly guaranteed in this process according to the ethical principles proposed by Kosinski et al. (Kosinski et al., 2015). The ethics code, identified as H15009, has been officially approved by the Institutional Review Board at the Institute of Psychology, Chi nese Academy of Sciences. 

![image](https://timisic.oss-cn-hangzhou.aliyuncs.com/pic/05513215358b3e81f5c1680bb41277d514c8f3825ee621adead7aae7366eec6a.jpg)



F I G U R E 1 Participant recruitment and data acquisition process.


## Instruments

## Psychological scales

This study collected users' age, gender, location, and education level as demographic factors for reference. Participants' SWB scores were assessed using the Chinese version of the Satisfaction with Life Scale (SWLS) (Diener et al., 1985) and the Positive and Negative Affect Schedule (PANAS) (Crawford & Henry, 2004). We selected these two instruments because they are wellestablished in the literature (Carvalho et al., 2013; Pavot & Diener, 2008; von Humboldt et al., 2017) and provide comprehensive measures of both affective and cognitive components of SWB (Diener, 2009). Both questionnaires were adapted from the English versions, and their validity, reliability, and cross-cultural consistency have been proven in the Chinese context (Qiu et al., 2008; Weidong et al., 2004; Xiong & Xu, 2009). Table 1 depicts the description of each dimension of the questionnaire. 

## Psycholinguistic lexicons

To enhance the prediction process and deepen our understanding of how language reflects SWB, we used psycholinguistic lexicons to capture psychological expressions in social media content. Based on current knowledge and available resources, this study employed five dis tinct psycholinguistic lexicons for the extraction of psycholinguistic features: the Simplified Chinese version of LIWC (SC-LIWC) (Gao et al., n.d.), the Moral Foundations Dictionary (MFD) (Wu et al., 2019), the Moral Motivation Dictionary (MMD) (Zhang & Yu, 2018), the Culture Value Dictionary (CVD) (Ren et al., 2017), and the Weibo Basic Mood Lexicon (Weibo-5BML) (Dong et al., 2015). According to the definition, SWB comprises the scientific analysis of people's emotional reactions to events, their moods, and the judgments they form about their life satisfaction (Diener et al., 2003). Therefore, it is necessary to include Weibo 5BML, an emotion-related lexicon annotated with five emotions: happiness, sadness, anger, fear, and disgust. Considering that virtue is a central component of well-being (VanderWeele, 2017) and the influence of moral value on assessments of SWB is highly robust (Cui et al., 2021; Phillips et al., 2017), the MMD and MFD were also included. Moreover, we also involved CVD in our feature extraction process, acknowledging the association between culture and people's SWB, as suggested by Ryan and Deci (2001). This approach i also supported by studies indicating that individualism–collectivism influences people's SWB (Hofstede, 1984; Ogihara & Uchida, 2014). Finally, we kept SC-LIWC because it provides abundant linguistic features that can be used to assess people's psychological state based on their writing. 


T A B L E 1 The introduction of the psychological scales.


<table><tr><td colspan="2">Dimension</td><td>Description</td><td>Interval</td></tr><tr><td rowspan="2">Affective well-being</td><td>Positive Affecta</td><td>The extent to of an individual subjectively experiences positive moods such as joy, interest, and alertness.</td><td rowspan="2">[10,50]</td></tr><tr><td>Negative Affecta</td><td>The extent to of an individual subjectively experiences negative moods such as anxiety, depression, and envy.</td></tr><tr><td>Cognitive well-being</td><td>Life Satisfactionb</td><td>The degree to which a person positively evaluates the overall quality of his/her life.</td><td>[5,35]</td></tr></table>


<sup>a</sup>Source: PANAS. 



<sup>b</sup>Source: SWLS. 


## Modeling procedure

## Data preprocessing

As shown in Figure 2, in this step, each participant's posts and SWB scores were first matched according to their user IDs. Then, 90% of the participants were randomly selected as the train ing set, while the remaining participants served as the test set. All posts from each participant were merged into a single document. For the participants in the test set, considering that time is one of the significant factors influencing individuals' SWB, we sorted each participant's posts by time. Then, we merged all odd-numbered posts of each participant into one document and all even-numbered posts into another document. 

## Feature extraction

We used psycholinguistic lexicons to extract text features, which rely on a priori word categori zation based on human judgment. Specifically, each document underwent the matching pro cess, after which all the matched words formed a bag-of-words. For each bag-of-words, the word usage frequencies across pre-chosen language categories were counted. For example, words like ‘sister’, ‘grandma’, ‘father’, and ‘son’ are categorized under ‘family’. We then determine who talks about family more often by counting the frequency of these ‘family words in each bag-of-words. The word frequency of a category was calculated by summing the counts of all words in this category and then dividing by the total number of words in the document. 

## Word cloud

To visually represent the most common words among individuals with high SWB, we generated word clouds based on the word frequency. On the one hand, we identified three-word groups based on users' scores: one group consisted of words from users whose positive affect scores were above average, another included words from users with life satisfaction scores above average and a third comprised words from users whose negative affect scores were below average. On the other hand, we maintained word groups for key text categories, with each group con sisting of words from the entire training set for that specific category. 

## Model training

Before the model training and parameter tuning, the max-min normalization on the train ing set was implemented, and the normalization model was saved. We then used various ensemble ML algorithms for model training based on normalized training sets and tuned parameters using Grid Search based on the results of five-fold cross-validation. The multi-task model used the text feature as input and produced a matrix of three SWB labels as output. The single-task models only focused on one of the three labels as it output. After determining the best algorithm and parameters, the test feature set, odd feature set, and even feature set were respectively inputted to the reserved normalization model and prediction model. Finally, the prediction scores were kept for the model' evaluation. 

![image](https://timisic.oss-cn-hangzhou.aliyuncs.com/pic/0be89c27bea1c476dafb1254e478465cac1a997d45d563bab349cd9b1fe9e954.jpg)



F I G U R E 2 Data preprocessing, feature extraction, model training, and prediction.


## Model evaluation

The Pearson correlation coefficients, RMSEs, and P-values of the prediction models were calculated for criterion validity evaluation. Drawing on the psychological scale reliability assessment method, we chose the split-half reliability measurement method, which is suitable for ML modeling. Like the correlation analysis of the measurement results of odd numbered and even-numbered questions in psychological questionnaires, we performed correlation calculations on the predicted SWB scores of odd and even-numbered posts (listed by post time) of each user. The split-half reliability for the prediction model was assessed between the odd set and even set using Pearson correlation coefficients and P-values. 

## Model interpretation

This study used a data-driven approach for model interpretation by identifying the important linguistic features contributing to SWB prediction. TreeExplainer from the SHapley Additive exPlanations (SHAP) package (Lundberg et al., 2020) was used to evaluate the feature importance and for visualization (Lundberg et al., 2018). SHAP values provide a unique additive feature importance measure (Lundberg & Lee, 2017). This method connects optimal credit allocation with local explanations using the classic Shapley values from game theory and their related extensions