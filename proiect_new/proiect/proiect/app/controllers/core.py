from typing import List, Optional, Tuple
from flask import jsonify, render_template, request, redirect, url_for, session, flash
from app.models import Comment, User
from app import db, bcrypt
from typing import Dict, Optional, List
from app.models import Load

def login():
    email = request.form['email']
    password = request.form['password']
    success, user = authenticate_user(email, password)
    if success:
        session['userid'] = user.id
        session['role'] = user.role  # Stocăm rolul în sesiune pentru a-l utiliza în redirecționare
        return redirect(url_for('dashboard'))
    else:
        fail_message = 'E-mail sau parolă incorectă!'
    return render_template('login.html', fail_message=fail_message)

def authenticate_user(email:str, password:str) -> Tuple[bool, User]:
    user:User = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        return True, user
    bcrypt.generate_password_hash
    return False, None

def register():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    cargo_type = request.form['cargo_type'] if role == "driver" else ''
    license_plate = request.form['license_plate'] if role == "driver" else ''
    success, message = register_user(firstname, lastname, email, password, role, cargo_type, license_plate)
    if success:
        return render_template('login.html', email=email, password=password, success_message=message)
    else:
        return render_template('register.html', fail_message=message, form=request.form, role=role, truck_type=cargo_type, license_plate=license_plate) 
    
def register_user(firstname:str, lastname:str, email:str, password:str, role:str, cargo_type:Optional[str] = None, license_plate:Optional[str]=None) -> Tuple[bool, str]:
    if User.query.filter_by(email=email).first() is not None:
        return False, "Utilizatorul există deja."

    new_user:User = User.create(email, role, firstname, lastname, cargo_type, license_plate)
    new_user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    db.session.add(new_user)
    try:
        db.session.commit()
        return True, "Înregistrare reușită."
    except Exception as e:
        db.session.rollback()
        return False, "Eroare la înregistrare."    
    
def dashboard(user_id:str, role:str):
    user = User.get_by_id(user_id)
    load_items = get_loads_list(user_id if role == "driver" else None) 
    firstname = user.firstname
    lastname = user.lastname
    drivers = User.get_by_role("driver")
    users = User.query.all()
    comments = get_comment_list()
    return render_template('dashboard.html', loads=load_items, firstname=firstname, lastname=lastname, drivers=drivers, comments=comments, users=users)

def get_loads_list(driver_id: Optional[int] = None) -> List[Load]:
    result:List[Load] = []
    if driver_id is not None:
        result = Load.query.filter_by(driver_id=driver_id).all()
    else:
        result = Load.query.all()
    return sorted(result, key=lambda x: x.status_order())

def add_load(user_id: str, form: Dict[str, str]):
    company_name = form['company_name']
    pickup_address = form['pickup_address']
    delivery_address = form['delivery_address']
    pallet_count = int(form['pallet_count'])
    pallet_dimensions = form['pallet_dimensions']
    truck_arrangement = form['truck_arrangement']
    cargo_type = form['cargo_type']
    contract_number = form['contract_number']
    delivery_price = int(form['delivery_price'])
    truck_type = form['truck_type']
        # logică pentru adăugarea încărcăturii în baza de date
    new_load = Load.create(user_id, company_name, pickup_address, delivery_address,pallet_count,pallet_dimensions, truck_arrangement, cargo_type, contract_number, delivery_price, truck_type)
    if new_load:
        return redirect(url_for('dashboard'))
    return jsonify({'error': 'Eroare la adăugarea încărcăturii'}), 500    

def edit_load(load_id:int, form: Dict[str, str]):
    load:Load = Load.query.filter_by(id=load_id).first()
    for k, v in form.items():
        load.__setattr__(k, v)

    if load.status == 'pending' and load.driver_id is not None:
        load.status = 'assigned'
        
    db.session.commit()
    return redirect(url_for('dashboard'))

def delete_load(load_id:str):
    load_to_delete:Load = Load.query.get(load_id)
    if load_to_delete:
        db.session.delete(load_to_delete)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return jsonify({'error': 'Încărcătura nu a fost găsită'}), 404
    

def get_comment_list() -> List[Load]:
    result = Comment.query.all()
    return sorted(result, key=lambda x: x.contract_number)

def add_comment(user_id: int, form: Dict[str, str]):
    comment = form['comment']
    contract_number = form['contract_number']
    # logică pentru adăugarea încărcăturii în baza de date
    new_comment = Comment.add_comment(contract_number, user_id, comment)
    if new_comment:
        return redirect(url_for('dashboard'))
    return jsonify({'error': 'Eroare la adăugarea încărcăturii'}), 500    

def profile(user_id: int):
    user = User.get_by_id(user_id)
    return render_template('profile.html', user=user)

def update_user(user_id:int, form:Dict[str,str]):
    user:User = User.query.get(user_id)

    success, user = authenticate_user(user.email, form['old_password'])
    if not success:
        return render_template('profile.html', user=user, fail_message="Parola este gresita!")

    for k, v in form.items():
        user.__setattr__(k, v)

    if form['new_password'] != '':
        user.password_hash = bcrypt.generate_password_hash(form['new_password']).decode('utf-8')
    
    db.session.commit()
    return render_template('profile.html', user=user, success_message="Modificarile au fost salvate cu success!")

def create_user(form:Dict[str,str]):
    email = form['email']
    password = form['password']
    role = form['role']
    firstname = form['firstname']
    lastname = form['lastname']
    cargo_type = form['cargo_type'] if role == "driver" else ''
    license_plate = form['license_plate'] if role == "driver" else ''

    success, message = register_user(firstname, lastname, email, password, role, cargo_type, license_plate)
    if success:
        return redirect(url_for('dashboard'))
    raise Exception(message)

def delete_user(user_id:int):
    user_to_delete:User = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return jsonify({'error': 'Utilizatorul nu a fost găsit'}), 404

def edit_user(user_id:int, form: Dict[str, str]):
    user:User = User.query.filter_by(id=user_id).first()
    for k, v in form.items():
        user.__setattr__(k, v)
    if form['password'] != '':
        user.password_hash = bcrypt.generate_password_hash(form['password']).decode('utf-8')
    db.session.commit()
    return redirect(url_for('dashboard'))

# def reset_password():
#     email = request.form['email']
#     new_password = request.form['new_password']
#     success, mesage = reset_password(email, new_password)
#     if success:
#         return render_template('login.html', email=email, success_message=mesage)   
#     else:
#         return render_template('reset_password.html', fail_message=mesage)        
# 
# 
# def reset_password(email:str, new_password:str) -> Tuple[bool, str]:
#     user:User = User.query.filter_by(email=email).first()
#     if not user:
#         return False, "Utilizatorul nu a fost găsit."
#     user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
#     try:
#         db.session.commit()
#         return True, "Parola a fost resetată cu succes."
#     except Exception as e:
#         db.session.rollback()
#         return False, "Eroare la resetarea parolei."