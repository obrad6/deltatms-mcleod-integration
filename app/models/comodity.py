from app import db


class Commodity(db.Model):
    __tablename__ = 'commodities'
    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(), nullable=False, unique=True)
    commodity_id = db.Column(db.String(), nullable=False, unique=True)
    commodity_description = db.Column(db.String(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'product_type': self.product_type,
            'commodity_id': self.commodity_id,
            'commodity_description': self.commodity_description
        }

    def __repr__(self):
        return f"<Commodity: {self.to_dict()}>"

    @classmethod
    def get_commodity_by_product_type(cls, product_type):
        return cls.query.filter_by(product_type=product_type).first()


