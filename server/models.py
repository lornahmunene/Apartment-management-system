from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# ------------------- USER ------------------- #
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)   # manager / landlord
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "role": self.role
        }

# ------------------- ROOM ------------------- #
class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(100), nullable=False, unique=True)  # FIXED: was room_id
    status = db.Column(db.String(50), nullable=False, default="vacant")
    room_type = db.Column(db.String(50), nullable=False, default="single")  # FIXED: was type
    rent_amount = db.Column(db.Float, nullable=False)

    # A room belongs to ONE tenant
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))

    # A room has many payments
    payments = db.relationship("Payment", backref="room", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "room_number": self.room_number,  # FIXED
            "status": self.status,
            "room_type": self.room_type,  # FIXED
            "rent_amount": self.rent_amount,
            "tenant_id": self.tenant_id
        }

# ------------------- TENANT ------------------- #
class Tenant(db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  # FIXED: was tenant_name
    email = db.Column(db.String(255), nullable=False)  # FIXED: was tenant_email
    phone = db.Column(db.String(50), nullable=True)  # FIXED: was phone_number
    national_id = db.Column(db.String(100), nullable=True)

    moving_in_date = db.Column(db.Date, nullable=False)
    moving_out_date = db.Column(db.Date, nullable=True)
    
    # Email notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    last_reminder_sent = db.Column(db.Date, nullable=True)

    # A tenant can have only one room
    rooms = db.relationship("Room", backref="tenant", uselist=False)

    # A tenant has many payments
    payments = db.relationship("Payment", backref="tenant_payments", lazy=True)

    def to_dict(self):
        # Get room info if tenant has a room
        room = Room.query.filter_by(tenant_id=self.id).first()
        
        return {
            "id": self.id,
            "name": self.name,  # FIXED
            "email": self.email,  # FIXED
            "phone": self.phone,  # FIXED
            "national_id": self.national_id,
            "moving_in_date": self.moving_in_date.isoformat(),
            "moving_out_date": self.moving_out_date.isoformat() if self.moving_out_date else None,
            "room_number": room.room_number if room else None,  # Add room info
            "email_notifications": self.email_notifications
        }

# ------------------- PAYMENT ------------------- #
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)  # FIXED: was payment_price
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)  # FIXED: was payment_date
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    room_id=db.Column(db.Integer,db.ForeignKey('rooms.id'),nullable=True)
    # Payment method (simplified - no M-Pesa)
    payment_method = db.Column(db.String(20), default='cash')  # 'cash' or 'bank'
    reference_number = db.Column(db.String(100), nullable=True)  # Bank reference or receipt number
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,  # FIXED
            'date': self.date.isoformat(),  # FIXED
            'tenant_id': self.tenant_id,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'notes': self.notes
        }


# ------------------- PASSWORD RESET TOKEN ------------------- #
class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='reset_tokens')
    
    def is_valid(self):
        return not self.used and datetime.datetime.utcnow() < self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat(),
            'used': self.used
        }