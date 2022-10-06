
class GameBoard():


    def __init__(self,opponents,dora_indicator,round_wind,self_wind):
        self.opponents_list = opponents
        self.dora_indicator = dora_indicator
        self.round_wind = round_wind
        self.self_wind = self_wind


    def opponent_getter(self,num):
        return self.opponents_list[num-1]
    
    def dora_indicator_getter(self):
        return self.dora_indicator

    def round_wind_getter(self):
        return self.round_wind
    
    def self_wind_getter(self):
        return self.self_wind
    


