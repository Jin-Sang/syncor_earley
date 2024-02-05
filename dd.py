state = ({"γ": "•S"}, 0)

def finish_check(state):
    next = list(state[0].values())[0]
    if next.find("•") != len(state):
        print(False)
    else:
        print(True)
    
    
finish_check(state)
    