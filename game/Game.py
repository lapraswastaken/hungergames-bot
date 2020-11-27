
from random import randint
from typing import Optional

from game.Character import Character
from game.Event import Event
from game.Item import Item, Item
from game.Map import Map
from game.State import State


class Game:
    def __init__(self, items: list[Item], events: list[Event], tributes: list[Character], map: Map):
        self.tributes = tributes
        self.items = items
        self.events = events
        self.map = map
        
        self.start()
    
    def start(self):
        for tribute in self.tributes:
            tribute.move(self.map.getStartingZone())
            tribute.addTag("running")
    
    def getTributeByName(self, name: str):
        for tribute in self.tributes:
            if tribute.string() == name:
                return tribute
        return None
    
    def getItemByName(self, name: str):
        for item in self.items:
            if item.string() == name:
                return item
        return None
    
    def triggerByName(self, charName, eventName) -> list[tuple[str, list[tuple[Character, str]]]]:
        char = None
        for tribute in self.tributes:
            if tribute.string() == charName:
                char = tribute
                break
        if not char:
            return [(f"unable to find character named {charName}", [])]
        event = None
        for e in self.events:
            if e.getName() == eventName:
                event = e
                break
        if not event:
            return [(f"unable to find event named {eventName}", [])]
        if event.prepare(char, self.tributes):
            return self.trigger(char, event)
        
        return [("Trigger failed", [])]
    
    def trigger(self, char: Character, event: Event) -> list[tuple[str, list[tuple[Character, str]]]]:
        state, subEvents = event.trigger()
        textResults: list[tuple[str, list[tuple[Character, str]]]] = [(state.getReplacedText(event.text), state.getResultStrs())]
        #print(textResults)
        if subEvents:
            sub = self.chooseFromEvents(char, subEvents, state)
            textResults += self.trigger(char, sub)
        return textResults
        
    def chooseFromEvents(self, char: Character, events: list[Event]=None, state: State=None):
        if not events:
            events = self.events
        
        possibleEvents: list[Event] = []
        totalChance = 0
        defaultEvent: Optional[Event] = None
        
        for event in events:
            if event.prepare(char, self.tributes, state):
                if event.getChance() == 0:
                    defaultEvent = event
                    continue
                totalChance += event.getChance()
                possibleEvents.append(event)
        
        if not possibleEvents:
            if defaultEvent:
                return defaultEvent
            else:
                raise Exception("No events matched when choosing from events")
                
        choice = randint(0, totalChance - 1)
        
        count = 0
        for event in possibleEvents:
            if choice >= count and choice < (count + event.getChance()):
                return event
            count = count + event.getChance()
        raise Exception(f"Invalid choice when choosing from events ({choice} out of {totalChance})")
    
    def round(self) -> list[tuple[Character, list[tuple[str, list[tuple[Character, str]]]]]]:
        allresults = []
        for tribute in self.tributes:
            if not tribute.isAlive():
                continue
            event = self.chooseFromEvents(tribute)
            allresults.append((tribute, self.trigger(tribute, event)))
        return allresults
            
        
