from typing import Optional
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class User(db.Model):
    # Definirea câmpurilor tabelei User
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    firstname = db.Column(db.String(80), nullable=True)
    lastname = db.Column(db.String(80), nullable=True)
    role = db.Column(db.String(50), nullable=False) # Adăugare atribut role
    cargo_type = db.Column(db.String(50), nullable=True) # Adăugare tip camion
    license_plate = db.Column(db.String(50), nullable=True) # Adăugare nr înmatriculare camion

    # Metoda pentru crearea unui nou utilizator în baza de date
    @staticmethod
    def create(email:str, role:str, firstname:Optional[str]=None, lastname:Optional[str]=None, cargo_type:Optional[str]=None, license_plate:Optional[str]=None):
        user = User(email=email, firstname=firstname, lastname=lastname, role=role, cargo_type=cargo_type, license_plate=license_plate)  # Setare atribut role
        db.session.add(user)
        db.session.commit()
        return user


    # Metoda pentru a obține un utilizator după adresa de email
    @staticmethod
    def get_by_email(email:str)->'User':
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_by_id(id:int)->'User':
        return User.query.filter_by(id=id).first()

    @staticmethod
    def get_by_role(role:str)->'User':
        return User.query.filter_by(role=role).all()
    
    # Metoda pentru setarea parolei utilizatorului
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    
    def desc(self):
        if self.cargo_type:
            return f'{self.firstname} {self.lastname} ({self.cargo_type})'
        else:
            return f'{self.firstname} {self.lastname}'

    
class Load(db.Model):
    __tablename__ = 'loads'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, nullable=False) # id utilizator - autor
    status = db.Column(db.String(50), nullable=True) # statut livrare
    company_name = db.Column(db.String(120), nullable=False)  # Numele Companiei Client
    pickup_address = db.Column(db.String(255), nullable=False)  # Adresa de ridicare
    delivery_address = db.Column(db.String(255), nullable=False)  # Adresa de livrare
    pallet_count = db.Column(db.Integer, nullable=False)  # Numărul de palete
    pallet_dimensions = db.Column(db.String(80), nullable=False)  # Dimensiuni palete (înălțime, lățime, lungime)
    truck_arrangement = db.Column(db.String(255), nullable=False)  # Aranjarea în camion
    cargo_type = db.Column(db.String(50), nullable=False)  # Tipul de marfă
    contract_number = db.Column(db.String(120), nullable=False)  # Numărul Contractului
    delivery_price = db.Column(db.Float, nullable=False)  # Prețul livrării
    truck_type = db.Column(db.String(50), nullable=False)  # Tipul Comionului
    driver_id = db.Column(db.Integer, nullable=True)  # Id-ul soferului

    # Metodă pentru crearea unei noi încărcături în baza de date
    @staticmethod
    def create(user_id:int, company_name:str, pickup_address:str, delivery_address:str, pallet_count:int, pallet_dimensions:str, 
               truck_arrangement:str, cargo_type:str, contract_number:str, delivery_price:float, truck_type:str):
        load = Load(
            author_id=user_id,
            status="pending",
            company_name=company_name, 
            pickup_address=pickup_address, 
            delivery_address=delivery_address,
            pallet_count=pallet_count,
            pallet_dimensions=pallet_dimensions,
            truck_arrangement=truck_arrangement,
            cargo_type=cargo_type,
            contract_number=contract_number,
            delivery_price=delivery_price,
            truck_type=truck_type
        )
        db.session.add(load)
        db.session.commit()
        return load

    # Metodă pentru obținerea unei încărcături după numărul contractului
    @staticmethod
    def get_by_contract_number(contract_number):
        return Load.query.filter_by(contract_number=contract_number).first()
    

    def status_desc(self):
        if self.status == "pending":
            return "In asteptare"
        if self.status == "assigned":
            return "Alocat"
        if self.status == "delivered":
            return "Livrat"
        if self.status == "onway":
            return "In livrare"
    
    def status_order(self) -> int: 
        if self.status == "pending":
            return 0
        if self.status == "assigned":
            return 1
        if self.status == "onway":
            return 2
        if self.status == "delivered":
            return 3

        
    def driver_name(self):
        if self.driver_id:
            user:User = User.query.filter_by(id=self.driver_id).first()
            if user:
                return f'[{user.id}] {user.firstname} {user.lastname}'
            else:
                return "[] Unknown Driver"
        return ''




class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(120), nullable=False)  # Numărul Contractului
    user_id = db.Column(db.Integer, nullable=False) # statut livrare
    comment = db.Column(db.String(1000), nullable=True)  # Numele Companiei Client

    @staticmethod
    def add_comment(contract_number:int, user_id:int, comment:str):
        comment = Comment(contract_number=contract_number, user_id=user_id, comment=comment)
        db.session.add(comment)
        db.session.commit()
        return comment
    
    def user_name(self):
        if self.user_id:
            user:User = User.query.filter_by(id=self.user_id).first()
            if user:
                return f'[{user.id}] {user.firstname} {user.lastname}'
            else:
                return '[] Unknown User'
        return ''
