from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于flash消息

# 存储投票数据
votes = {
    'votes': [],  # 存储所有投票
    'revealed': False,  # 控制是否显示投票结果
    'can_vote': True  # 控制是否可以投票
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
    if not votes['can_vote']:
        flash('当前已有人投票，请等待投票结果公布后再开始新的投票', 'error')
        return redirect(url_for('index'))
    
    vote_choice = request.form.get('vote')
    if not votes['revealed']:
        votes['votes'].append(vote_choice)
        votes['can_vote'] = False  # 投票后禁止继续投票
        flash('投票成功！请等待其他人查看结果', 'success')
    return redirect(url_for('index'))

@app.route('/reveal', methods=['POST'])
def reveal():
    votes['revealed'] = True
    flash('投票结果已公布！', 'success')
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    votes['votes'].clear()
    votes['revealed'] = False
    votes['can_vote'] = True
    flash('投票已重置，可以开始新的投票', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
