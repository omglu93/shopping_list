from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class UserData(db.Model):
    
    """ Table that contains user data
    """
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    
    shoppinglist = db.relationship("Shoppinglist",
                                   order_by="Shoppinglist.id",
                                   cascade="all, delete-orphan")
    
    date_created = db.Column(db.DateTime,
                             default=db.func.current_timestamp())
    
    date_modified = db.Column(db.DateTime,
                              default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    
    
    def __repr__(self) -> str:
        return f"User: {self.username} /n email: {self.email}"
    
    
class ShoppingList(db.Model):
    
    """Table that contains the shopping list for each user
    """
    
    __tablename__ = "shopinglist_table"
    
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    
    date_created = db.Column(db.DateTime,
                             default=db.func.current_timestamp())
    
    date_modified = db.Column(db.DateTime,
                              default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    
    items = db.relationship("Item", order_by="Item.id",
                            cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"User: {self.name} /n items: {self.items}"
    
class Item(db.Model):
    
    """Table that contains the items for each shopping list
    """
    
    __tablename__ = "item_table"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Float())
    quantity = db.Column(db.Float())
    owner = db.Column(db.Integer,
                      db.ForeignKey(ShoppingList.id))
    
    date_created = db.Column(db.DateTime,
                             default=db.func.current_timestamp())
    
    date_modified = db.Column(db.DateTime,
                              default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    
    def __repr__(self) -> str:
        return f"Item name: {self.name} /n price: {self.price}" \
               f" /n item quantity{self.quantity}"