from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserData(db.Model):
    
    """ Table that contains user data
    """
    
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    
    shoppinglist = db.relationship("ShoppingList",
                                   order_by="ShoppingList.id",
                                   cascade="all, delete-orphan",
                                   )
    
    user_credentials = db.relationship("UserCredentials",
                                       order_by="UserCredentials.id",
                                       cascade="all, delete-orphan")
    
    date_created = db.Column(db.DateTime,
                             default=db.func.current_timestamp())
    
    date_modified = db.Column(db.DateTime,
                              default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    
    
    def __repr__(self) -> str:
        return f"User: {self.username} /n email: {self.email}"
    
    def __init__(self, username, email, password, public_id) -> None:
        
        self.username = username
        self.email = email
        self.password = password
        self.public_id = public_id
        
    def save(self):
        """Saves user to database
        """
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        """Deletes user from database
        """
        db.session.delete(self)
        db.session.commit()
    
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
    
    user_id = db.Column(db.Integer, db.ForeignKey(UserData.id))
    
    def __repr__(self) -> str:
        return f"User: {self.name} /n items: {self.items}"
    

    def __init__(self, name, user_id) -> None:
        
        self.name = name
        self.user_id = user_id
      
    def save(self):
        """Saves list to database
        """
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        """Deletes list from database
        """
        db.session.delete(self)
        db.session.commit()
    
    
class Item(db.Model):
    
    """Table that contains the items for each shopping list
    """
    
    __tablename__ = "item_table"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    quantity = db.Column(db.Float())
    owner = db.Column(db.Integer,
                      db.ForeignKey(ShoppingList.id))
    
    date_created = db.Column(db.DateTime,
                             default=db.func.current_timestamp())
    
    date_modified = db.Column(db.DateTime,
                              default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    
    def __repr__(self) -> str:
        return f"Item name: {self.name} " \
               f"item quantity{self.quantity}"
    
    def __init__(self, name, quantity, owner) -> None:
        
        self.name = name
        self.quantity = quantity
        self.owner = owner
      
    def save(self):
        """Saves item info to database
        """
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        """Deletes item info from database
        """
        db.session.delete(self)
        db.session.commit()
               
class UserCredentials(db.Model):
    
    """ This database stores user credentials
    """
    
    __tablename__ = "user_credentials"
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer,
                      db.ForeignKey(UserData.id))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    
    def __init__(self, first_name, last_name, user) -> None:
        
        self.first_name = first_name
        self.last_name = last_name
        self.user = user
      
    def save(self):
        """Saves user info to database
        """
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        """Deletes user info from database
        """
        db.session.delete(self)
        db.session.commit()