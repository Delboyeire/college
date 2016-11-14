import html

from flask import Flask, session, render_template, request

app = Flask(__name__)


@app.route('/')
@app.route('/welcomePage', methods=['GET', 'POST'])
def welcome() -> 'html':
    session.clear()
    return render_template('welcomePage.html',
                           title='Welcome To My Project',
                           instructions='To play enter your name and continue',
                           header='The Game Must Go On')


@app.route('/startgame', methods=['GET', 'POST'])
def startgame() -> 'html':
    import random
    if request.method == 'POST':
        session['name'] = request.form['name']

    with open('words.txt', 'r') as f:
        words = [line.strip() for line in f]
    longwordlist = []
    for word in words:
        if len(word) > 7:
            longwordlist.append(word)
    session['wordselected'] = random.choice(longwordlist)
    import time
    session['starttime'] = time.clock()

    return render_template('welcomeFormPage.html',
                           title='Lets Play',
                           instructions='Make 7 anagrams as quick as you can',
                           header='Your word :' + session['wordselected'],
                           word=session['wordselected'],
                           starttime=session['starttime'])


@app.route('/sendToGame', methods=['GET', 'POST'])
def process_the_data() -> 'html':
    import time
    session['endtime'] = time.clock()
    session['timeTaken'] = session['endtime'] - session['starttime']


    with open('words.txt', 'r') as f:
        words = [line.strip() for line in f]
    session['wordList'] = [request.form.get("word1"), request.form.get("word2"), request.form.get("word3"),
                request.form.get("word4"), request.form.get("word5"), request.form.get("word6")]

    session['validwordsentered'] = []
    session['invalidwordsentered'] = []
    for word in session['wordList']:
        if word in words:
            if len(word) > 3:
                if all(session['wordselected'].count(c) >= word.count(c) for c in word):
                    session['validwordsentered'].append(word)
        else:
            session['invalidwordsentered'].append(word)

    if len(session['invalidwordsentered']) == 0:
        import pickle
        scores = open("scoreList.txt", "rb")
        try:
            session['leaderList'] = pickle.load(scores)
        except EOFError:
            session['leaderList'] = []
        scores.close()
        session['currentPlay'] = dict(time=session['timeTaken'], name=session['name'], word=session['wordselected'])
        session['leaderList'].append(session['currentPlay'])
        session['newlist'] = sorted(session['leaderList'], key=lambda k: k['time'])
        scores = open("scoreList.txt", "wb")
        pickle.dump(session['newlist'], scores)
        scores.close()
        session['place'] = session['newlist'].index(session['currentPlay'])+1
        session['toptenlist'] = session['newlist'][:10]

        return render_template('resultPage.html',
                               title='Your Results',
                               timeTaken=session['timeTaken'],
                               instructions='Enter Your Name To Submit result',
                               scoreList=session['toptenlist'],
                               place=session['place'],
                               header='Your Results')
    else:
        return render_template('failedResultPage.html',
                               title='Hardluck!',
                               time=session['timeTaken'],
                               invalidwords=session['invalidwordsentered'],
                               instructions='Please try again',
                               header='Better Luck Next Time')



@app.route('/crash')
def what_a_mess() -> str:
    # 1 / 0
    return "Life's a mess, isn't it?"


app.secret_key = 'sju37dn82m/sunkdu6/a8n3u'
if __name__ == '__main__':
    app.run(debug=True)