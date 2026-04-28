#defines a UI so it can be updated easily

class UI:
    def __init__(self):
        self.UI_Screen=""
        self.UI_Elements=[]
        pass
    
    def create_UI(self,options=[])->str:
        self.UI_Elements=options
        FinalUIString=""
        for i, item in enumerate(options):
            FinalUIString+=f"{i+1}: {item}\n"
        self.UI_Screen=FinalUIString
        return FinalUIString
    
    def update(self)->None:...





if __name__ == "__main__":
    print(UI().create_UI(["List drives", "Open drives"]))