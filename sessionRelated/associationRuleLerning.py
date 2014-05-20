import sys
import helpers

col = helpers.getCollection('sessions')

def main():
    sessions = groupSessionsForUsers()

    for session in sessions:

    print ('lol')

def groupSessionsForUsers():
    gReducer = Code("""
        function (cur,result) {
            tmpts = (cur.ts);
            tmpev = cur.event_id;
            event = {
                ev:tmpev,
                ts:tmpts
            };
            result.events[tmpts] = tmpev;
        }
    """)

    eventGoups = col.group(
        key = {
            'user_id':1,
            'session':1,
        },
        condition = {
            # 'user_id':user,
        },
        reduce = gReducer,
        initial = {
            'events':{},
            # 'weight':0.6
        }
    )
    return eventGoups

if __name__ == "__main__":
    main()
