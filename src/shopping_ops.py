from flask_restful import reqparse, Resource
from werkzeug.security import check_password_hash
from src.app_database import ShoppingList, Item, UserData
from src.token_val import token_required
from sqlalchemy import and_
from datetime import datetime
import ast
import re
import pandas as pd


create_shopping_args = reqparse.RequestParser()
create_shopping_args.add_argument("list_name",
                                  type=str,
                                  location="json",
                                  required=True
                                )
create_shopping_args.add_argument("item_list",
                                  location="json",
                                  action="append")


alter_shopping_args = reqparse.RequestParser()
alter_shopping_args.add_argument("old_name",
                                  type=str,
                                  location="json",
                                  required=True
                                )
alter_shopping_args.add_argument("new_name",
                                  type=str,
                                  location="json",
                                  required=True
                                )

delete_shopping_args = reqparse.RequestParser()
delete_shopping_args.add_argument("list_name",
                                  type=str,
                                  location="json",
                                  required=True)
delete_shopping_args.add_argument("user_password",
                                  type=str,
                                  location="json",
                                  required=True)

analytics_shopping_args =reqparse.RequestParser()
analytics_shopping_args.add_argument("start_date",
                                     type=str,
                                     location="json",
                                     required=True,
                                     help="Desired format is  yyyy-mm-dd")
analytics_shopping_args.add_argument("end_date",
                                     location="json",
                                     type=str,
                                     required=True,
                                     help="Desired format is  yyyy-mm-dd")
analytics_shopping_args.add_argument("agg",
                                     type=str,
                                     location="json",
                                     help="")
class ShoppingListClass(Resource):

    """ Class handles shopping list requests
    
    Endpoints: /api/v1/shopping-lists
    
    HTTP methods: POST, GET, PUT, DELETE
    """
    
    @token_required  
    def post(self, user):
        
        """ Creates new shopping list in the database, it can
        also directly add items to the shopping list with the 
        help of nested jsons. There is no limit to the amount of items
        that can be added. Items are optional.

        Example request:
            {
                "list_name" : "New_list",
                "item_list" : [
                {
                "Item" : "TV",
                "Quantity": 2
                },
                {
                "Item" : "Computer",
                "Quantity": 16
                }]}
        """
        
        args = create_shopping_args.parse_args()
        self.list_name = args["list_name"]
        self.item_list = args["item_list"]
        
        if len(self.list_name) < 2:
                return {"error" : "List name is too short!"}, 400
            
        if ShoppingList.query.filter_by(name=self.list_name).first() is not None:
                return {"error": "List name already taken!"}, 409
            
        ### Add new Shopping List ###
        try:
            new_shopping = ShoppingList(name=self.list_name,
                                        user_id = user)
            new_shopping.save()
        except Exception as e:
            print(e)
            return {"error" : "Issues while processing new shopping list."}, 500
        
        ### Add items to Shopping List ###
        try:
            if self.item_list is not None:
                
                shopping_id = ShoppingList.query.filter(and_(ShoppingList.user_id == user,
                                                             ShoppingList.name == self.list_name)).first()
                    
                for item in self.item_list:
                    item = ast.literal_eval(item)
                    
                    item_name, msg_item = self._validate_item(item["Item"])
                    if msg_item is not None:
                        return {"error" : msg_item}, 400
                    
                    item_qunt, msg_quant = self._validate_quantity(item["Quantity"])
                    if msg_quant is not None:
                        return {"error" : msg_quant}, 400
                        
                    new_item = Item(name=item_name,
                                    quantity=item_qunt,
                                    owner=shopping_id.id)
                    new_item.save()
                    
            return {"msg": "Shopping list added succesfully!"}, 200
        
        except Exception as e:
            print(e)
            return {"error", "Issues with processing items."}, 500
        
    @token_required
    def put(self, user):
        
        """Changes the name of a selected shopping list

        Example request:
            {"old_name":"New_list",
            "new_name":"New_New_List"}
        """
        args = alter_shopping_args.parse_args()
        self.old_name = args["old_name"]
        self.new_name = args["new_name"]
        
        try:
            shopping_list = ShoppingList.query.filter_by(name=self.old_name,
                                                        user_id = user).first()
            if shopping_list is None:
                return {"error": "List name does not exit!"}, 409
            else:
                
                if len(self.new_name) < 2:
                    return {"error" : "List name is too short!"}, 400
                
                if ShoppingList.query.filter_by(name=self.new_name).first() is not None:
                    return {"error": "List name already taken!"}, 409
                
                new_name = self.new_name
                shopping_list.name = new_name
                shopping_list.save()
                return {"msg": "Shopping list name updated!"}, 200
            
        except Exception as e:
            print(e)
            return {"error", "Issues with processing name change."}, 500
        
        
    @token_required
    def delete(self,user):
        
        """ Deletes a selected shopping list from
        the database. It requires the users password to
        process with the request

        Example request:
            {"list_name" : "12344",
            "user_password": "thisisapassword"}
        """
        
        try:
            args = delete_shopping_args.parse_args()
            shopping_name = args["list_name"]
            password = args["user_password"]
            
            shopping_list = ShoppingList.query.filter_by(name=shopping_name,
                                                            user_id = user).first()
            
            if shopping_list is None:
                return {"error": "List name does not exit!"}, 409
            
            user = UserData.query.filter_by(id=user).first()
            
            if check_password_hash(user.password, password):
                shopping_list.delete()
                return {"msg": "Shopping list succesfully deleted!"}, 200
            else:
                return {"error" : "Could not verify!"}, 401
            
        except Exception as e:
            print(e)
            return {"error": "Issues with processing removal."}, 500
    
    @token_required
    def get(self, user):
        
        """ Returns all shopping lists that the user has on
        its account. No input parameters needed.

        """
        
        try:
            shopping_list = ShoppingList.query.filter_by(user_id = user).all()
            
            if not shopping_list:
                    return {"error": "Not shopping lists on this user!"}, 409
            response = {}
            for i, row in enumerate(shopping_list):
                response[i] = row.name
            return {"all_lists" : response}, 200
        except Exception as e:
            print(e)
            return {"error": "Issues with processing get request."}, 500
        
        
    def _validate_item(self, item):
        """ Validates item for special characters and len

        Args:
            item (str): item in the shopping list

        Returns:
            returns either a msg or the item depending
            if the item passes the validation or not
        """
        if len(item) < 2:
            msg = "Item name is too short!"
            return None, msg
        string_check= re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        
        if(string_check.search(item) != None):
            msg = "Item name contains special characters!"
            return None, msg
        return str(item), None
    
    def _validate_quantity(self, quantity):
        
        """ Validates item for quantaty and type

        Args:
            item (str): item in the shopping list

        Returns:
            returns either a msg or the item depending
            if the item passes the validation or not
        """
          
        try:
            quantity = int(quantity)
        except:
            msg="Quantity must be numeric!"
            return None, msg
        if quantity < 0:
            msg="Quantity cannot be negative!"
            return None, msg
        return quantity, None
    
class ShoppingListAnalytics(Resource):
    
    """ Allows the user to request resampled data about the all items
    in all shopping lists. The current version supports resampling on
    a minute, hour and day basis with a sum aggregator.

    Endpoints: /api/v1/shopping-lists/overview"
    
    HTTP methods: GET
    """
    AGG_OPTIONS = ["minute", "hour", "day"]
    
    @token_required
    def get(self, user):
        
        """ Returns a resampled overview of all items
        of the user. The default resample value is hour.

        Example request:
            {"start_date" : "2021-03-01",
            "end_date" : "2021-03-15"}
        """
        
        args = analytics_shopping_args.parse_args()
        
        start_date = args["start_date"]
        end_date = args["end_date"]
        agg = args["agg"]
        
        if agg is None:
            agg = "hour"
        elif agg not in self.AGG_OPTIONS:
            msg = ("No aggregation of this type."
                   "The ones available are: minute, hour, day")
            return {"error" : msg}, 400
            
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            msg = ("Date needs to have the"
                   "following format yyyy-mm-dd")
            return {"error" : msg}, 400
        
        try:
            shopping_list = ShoppingList.query.filter(ShoppingList.user_id == user).all()
            
            if not shopping_list:
                return {"error": "No items on this user!"}, 409

            column_list = []
            for list in shopping_list:
                
                items = Item.query.filter(and_(Item.owner == list.id,
                                               Item.date_created < end_date,
                                               Item.date_created > start_date)).all()
                
                # items = Item.query.filter(Item.owner == list.id).all()
                
                if not items:
                    continue
                    #return {"error": "No items on this user!"}, 409
                
                row_list = []
                for item in items:
                    row_list.append(list.name)
                    row_list.append(item.name)
                    row_list.append(item.quantity)
                    row_list.append(item.date_created)
                    column_list.append(row_list)
                    row_list = []
            
            df = pd.DataFrame(column_list, columns=["list_name", "item_namee",
                                                    "item_quantity", "date_created"])
            
            
            df["date_created"] = pd.to_datetime(df["date_created"])  
            df = df.set_index("date_created")
            if agg == "day":
                df = df.groupby(["item_namee"]).resample("D").sum()
                
            elif agg == "hour":
                df = df.groupby(["item_namee"]).resample("60Min").sum()

            elif agg == "minute":
                df = df.groupby(["item_namee"]).resample("1Min").sum()
                
            df.reset_index(inplace=True)
            df["date_created"] = df["date_created"].astype("string")
                 
            json_payload = df.to_dict(orient="index")
            
            return json_payload, 200
                 
        except Exception as e :
            print(e, e.args)
            return {str(e): str(e.args)}, 500
            