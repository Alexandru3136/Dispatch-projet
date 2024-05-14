from flask import jsonify, render_template, request, redirect, url_for, session, flash
from app.controllers import core as core_controller


def setup_routes(app):


    @app.route('/', methods=['GET', 'POST'])
    def home():
        return render_template('home.html')


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return render_template("login.html") if request.method == 'GET' else core_controller.login()

        

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        return render_template('register.html') if request.method == 'GET' else core_controller.register()
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('Ai fost deconectat.')
        return redirect(url_for('home'))
    

    # @app.route('/reset_password', methods=['GET', 'POST'])
    # def reset_password_route():
    #     return render_template('reset_password.html') if request.method == 'GET' else core_controller.reset_password()

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        if is_auth():
            return core_controller.dashboard(session['userid'], session['role'])
        return redirect(url_for('home'))
        

    @app.route('/load/add', methods=['POST'])
    def add_load():
        if is_auth() and session['role'] in ['dispatcher','admin']:
            return core_controller.add_load(int(session["userid"]), request.form)
        return jsonify({'error': 'Acces neautorizat'}), 403

    @app.route('/load/<load_id>/update', methods=['POST'])
    def edit_load(load_id:str):
        if is_auth() and session['role'] in ['dispatcher','admin']:
            return core_controller.edit_load(int(load_id), request.form)
        return jsonify({'error': 'Acces neautorizat'}), 403


    @app.route('/load/<load_id>/delete', methods=['POST'])
    def delete_load(load_id:str):
        if is_auth() and session['role'] in ['dispatcher','admin']:            
            return core_controller.delete_load(load_id)        
        return jsonify({'error': 'Acces neautorizat'}), 403



    @app.route('/comment/add', methods=['POST'])
    def add_comment():
        if is_auth():
            return core_controller.add_comment(int(session["userid"]), request.form)
        else:
            return jsonify({'error': 'Acces neautorizat'}), 403


    @app.route('/profile', methods=['GET'])
    def profile():
        if is_auth():
            return core_controller.profile(session['userid'])
        return redirect(url_for('home'))



    @app.route('/user/<int:user_id>/update', methods=['POST'])
    def update_user(user_id):
        if is_auth():
            return core_controller.update_user(user_id, request.form)
        return redirect(url_for('home'))
    
    @app.route('/user/add', methods=['POST'])
    def create_user():
        if is_auth() and session['role'] == 'admin':
            return core_controller.create_user(request.form)
        return jsonify({'error': 'Acces neautorizat'}), 403
        

    @app.route('/user/<user_id>/delete', methods=['POST'])
    def delete_user(user_id:str):
        if is_auth() and session['role'] in ['admin']:            
            return core_controller.delete_user(int(user_id))        
        return jsonify({'error': 'Acces neautorizat'}), 40

    @app.route('/user/<user_id>/edit', methods=['POST'])
    def edit_user(user_id:str):
        if is_auth() and session['role'] in ['admin']:            
            return core_controller.edit_user(int(user_id), request.form)        
        return jsonify({'error': 'Acces neautorizat'}), 40









    


def is_auth() -> bool:
    return 'userid' in session