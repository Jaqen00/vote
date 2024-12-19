from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# 存储投票数据
votes = {
    'votes': [],  # 存储所有投票
    'revealed': False  # 控制是否显示投票结果
}

@app.route('/')
def index():
    return render_template('index.html', 
                         votes=votes,
                         total_votes=len(votes['votes']),
                         yes_votes=votes['votes'].count('yes'),
                         no_votes=votes['votes'].count('no'))

@app.route('/vote', methods=['POST'])
def vote():
    if not votes['revealed']:
        vote_choice = request.form.get('vote')
        votes['votes'].append(vote_choice)
        flash('投票成功！', 'success')
    else:
        flash('投票已结束，无法继续投票', 'error')
    return redirect(url_for('index'))

@app.route('/reveal', methods=['POST'])
def reveal():
    if len(votes['votes']) == 0:
        flash('还没有人投票！', 'error')
        return redirect(url_for('index'))
    votes['revealed'] = True
    flash('投票结果已公布！', 'success')
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    votes['votes'].clear()
    votes['revealed'] = False
    flash('投票已重置，可以开始新的投票', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
