from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_socketio import SocketIO, emit
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')
socketio = SocketIO(app)

# 存储投票数据
votes = {
    'votes': [],  # 存储所有投票
    'revealed': False,  # 控制是否显示投票结果
    'voters': set(),  # 存储已投票的会话ID
    'online_users': set()  # 存储在线用户的会话ID
}

@app.route('/')
def index():
    # 为新用户生成唯一的会话ID
    if 'user_id' not in request.cookies:
        user_id = secrets.token_urlsafe(16)
    else:
        user_id = request.cookies.get('user_id')
        
    response = make_response(render_template('index.html', 
                         votes=votes,
                         total_votes=len(votes['votes']),
                         yes_votes=votes['votes'].count('yes'),
                         no_votes=votes['votes'].count('no'),
                         online_count=len(votes['online_users']),
                         user_id=user_id,
                         has_voted=(user_id in votes['voters'])))
    
    response.set_cookie('user_id', user_id)
    return response

@app.route('/vote', methods=['POST'])
def vote():
    user_id = request.cookies.get('user_id')
    
    if user_id in votes['voters']:
        flash('你已经投过票了', 'error')
        return redirect(url_for('index'))
    
    if not votes['revealed']:
        vote_choice = request.form.get('vote')
        votes['votes'].append(vote_choice)
        votes['voters'].add(user_id)
        flash('投票成功！', 'success')
        
        # 通过WebSocket广播更新
        socketio.emit('vote_update', {
            'total_votes': len(votes['votes']),
            'yes_votes': votes['votes'].count('yes'),
            'no_votes': votes['votes'].count('no')
        })
    
    return redirect(url_for('index'))

@app.route('/reveal', methods=['POST'])
def reveal():
    votes['revealed'] = True
    socketio.emit('reveal_votes')
    flash('投票结果已公布！', 'success')
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    votes['votes'].clear()
    votes['voters'].clear()
    votes['revealed'] = False
    socketio.emit('reset_votes')
    flash('投票已重置，可以开始新的投票', 'success')
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    user_id = request.cookies.get('user_id')
    votes['online_users'].add(user_id)
    emit('user_count', {'count': len(votes['online_users'])}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.cookies.get('user_id')
    votes['online_users'].discard(user_id)
    emit('user_count', {'count': len(votes['online_users'])}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
