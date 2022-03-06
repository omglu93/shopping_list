from flask_restful import reqparse, Resource
from src.token_val import token_required
from src.app_database import ShoppingList, Item
import ast
import re



create_items = reqparse.RequestParser()
create_items.add_argument("list_name",
                                type=str,
                                location="json",
                                required=True
                                )
create_items.add_argument("item_list",
                          location="json",
                          action="append",
                          required=True)

get_items = reqparse.RequestParser()
get_items.add_argument("list_name",
                       type=str,
                       location="json")

alter_items = reqparse.RequestParser()
alter_items.add_argument("item_name",
                         type=str,
                         location="json",
                         required=True)

alter_items.add_argument("quantity",
                          location="json",
                          type=int,
                          required=True)

alter_items.add_argument("id",
                          location="json",
                          type=int,
                          required=True)

delete_items = reqparse.RequestParser()
delete_items.add_argument("id",
                          location="json",
                          type=int,
                          required=True)

class ItemManipulation(Resource):
    
    """ Class handles item requests
    
    Endpoints: /api/v1/shopping-lists/items
    
    HTTP methods: POST, GET, PUT, DELETE
    """
    
    REGEX_CHECK = "[@_!#$%^&*()<>?/\|}{~:]"
    
    
    @token_required
    def post(self, user):
        
        """ Creates items for the requested shopping list. One
        or more items can be added at once.

        Example request:
            {"list_name" : "New_list",
            "item_list" : [
                {"Item" : "TV",
                "Quantity": 2},
                {"Item" : "Computer",
                "Quantity": 1}
                ]}
        """
        
        args = create_items.parse_args()
        list_name = args["list_name"]
        item_list = args["item_list"]
        try:
            shopping_list = ShoppingList.query.filter_by(user_id = user,
                                                        name = list_name).first()
            if shopping_list is None:
                    return {"error": "List name does not exit!"}, 409
            
            for item in item_list:
                item = ast.literal_eval(item)
                        
                item_name, msg_item = self._validate_item(item["Item"])
                if msg_item is not None:
                    return {"error" : msg_item}, 400
                
                item_qunt, msg_quant = self._validate_quantity(item["Quantity"])
                if msg_quant is not None:
                    return {"error" : msg_quant}, 400
                  
                new_item = Item(name=item_name,
                                quantity=item_qunt,
                                owner=shopping_list.id)
                new_item.save()
            return {"msg": "New items added succesfully!"}, 200
        
        except Exception as e:
            print(e)
            return {"error", "Issues with processing items."}, 500
        
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
    
    @token_required
    def get(self, user):
        
        """ Returns a list of all items in a shopping list, if no
        name is given returns items from all shopping lists.

        Example request:
            {"list_name" : "New_list22222222"} Optional
        """
        
        args = get_items.parse_args()
        list_name = args["list_name"]
        
        if list_name is None:
        
            try:
                shopping_list = ShoppingList.query.filter_by(user_id = user).all()
                
                if not shopping_list:
                        return {"error": "Not items on this user!"}, 409
                
                all_items = []
                final_dict = {}
                for row in shopping_list:
                    
                    items_per_list = Item.query.filter_by(owner = row.id).all()
                    
                    if not items_per_list:
                        return {"error": "Not items on this user!"}, 409
                    
                    for item_row in items_per_list:
                        item_dict = {}
                        item_dict["Name"] = item_row.name
                        item_dict["Quantity"] = item_row.quantity
                        item_dict["Id"] = item_row.id
                    
                        all_items.append(item_dict)
                    final_dict[row.name] = all_items

                return final_dict, 200
            
            except Exception as e:
                print(e)
                return {"error": "Issues with processing get request."}, 500
            
        else:
            try:
                shopping_list = ShoppingList.query.filter_by(user_id = user,
                                                             name = list_name).first()
                if shopping_list is None:
                        return {"error": "Not items on this user!"}, 409
                items_per_list = Item.query.filter_by(owner = shopping_list.id).all()
                
                if not items_per_list:
                        return {"error": "Not items on this list!"}, 409
                
                final_dict = {}
                all_items = []
                
                for item_row in items_per_list:
                    
                    item_dict = {}
                    item_dict["Name"] = item_row.name
                    item_dict["Quantity"] = item_row.quantity
                    item_dict["Id"] = item_row.id
                    
                    all_items.append(item_dict)
                    
                final_dict[shopping_list.name] = all_items
                
                return final_dict, 200
            
            except Exception as e:
                print(e)
                return {"error": "Issues with processing get request."}, 500
    
    @token_required
    def put(self, user):
        """ Changes a item attribute in the database, this is done
        via Id as there can be multiple items with the same name within
        a shopping list.

        Example request:
            {"id" : 8,
            "item_name": "Vise_nije_kasik2a",
            "quantity": 1500}
        """
        args = alter_items.parse_args()
        
        item_id = args["id"]
        item_name = args["item_name"]
        item_quantity = args["quantity"]
        try:
            all_shopping_list = ShoppingList.query.filter_by(user_id = user).all()
            
            if not all_shopping_list:
                return {"error": "Not shopping lists on this user!"}, 409
            
            for shopping_list in all_shopping_list:
                items_per_list = Item.query.filter_by(owner = shopping_list.id,
                                                    id = item_id).first()
                if items_per_list is None:
                    continue
                else:
                    break
            if items_per_list is None:
                return {"error": "Not item with those parameters on this user!"}, 409
            
            old_name = items_per_list.name
            old_quantity = items_per_list.quantity 
            items_per_list.name = item_name
            items_per_list.quantity = item_quantity
            items_per_list.save()
            
            response = (f"Item data sucessfully updated from {old_name} -> " 
                        f"{item_name} and {old_quantity} -> {item_quantity}")
            
            return {"msg": response}, 200
        
        except Exception as e:
            print(e)
            return {"error": "Issues with processing put request."}, 500
        
    @token_required
    def delete(self, user):
        """ Deletes item by id
        
        Example request:
            {"id" : "6"}
        """
        
        args = delete_items.parse_args()
            
        item_id = args["id"]
        
        try:
            all_shopping_list = ShoppingList.query.filter_by(user_id = user).all()
            
            if not all_shopping_list:
                return {"error": "No shopping lists on this user!"}, 409
            
            for shopping_list in all_shopping_list:
                items_per_list = Item.query.filter_by(owner = shopping_list.id,
                                                    id = item_id).first()
                if items_per_list is None:
                    continue
                else:
                    break
            if items_per_list is None:
                return {"error": "Not item with those parameters on this user!"}, 409
            items_per_list.delete()
            
            return {"msg": "Item succesfully deleted!"}, 200
        
        except Exception as e:
            print(e)
            return {"error": "Issues with processing delete request."}, 500