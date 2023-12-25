from app import db
from sqlalchemy import cast, Integer


class Load(db.Model):
    __tablename__ = 'loads'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(), nullable=False, unique=True)
    order_mcleod_status = db.Column(db.String())
    delta_load_id = db.Column(db.Integer, nullable=False, unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'order_mcleod_status': self.order_mcleod_status,
            'delta_load_id': self.delta_load_id
        }

    def __repr__(self):
        return f"<Load {self.to_dict()}>"

    @classmethod
    def get_last_inserted_load_by_order_id(cls):
        return cls.query.order_by(cast(cls.order_id, Integer).desc()).first()



