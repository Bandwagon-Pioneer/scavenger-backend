# User document

    {

        userinfo:{
            //output of Auth0
            "sub": "google-oauth2|102790077983251015183",
            "given_name": "Jeremi",
            "family_name": "F",
            "nickname": "jjfd428",
            "name": "Jeremi F",
            "picture": "https://lh3.googleusercontent.com/a-/AOh14GggTM2tPyqG74N30FcnGWssuo2Ys6NBQsIsACQP=s96-c",
            "locale": "en",
            "updated_at": "2021-05-08T18:39:08.991Z"
        },

        score: 1232, // updated every so often based off of timing and whatnot


        start: Datetime(),
        
        nodes : [
            {
                "nodeid":3,
                "found":true,
                "foundwhen": "someUTCNowString"
            },
            {
                "nodeid":2,
                "found":false,
                "foundwhen": null
            },
            {
                "nodeid":1,
                "found":false,
                "foundwhen": null
            },
            {
                "nodeid":4,
                "found":false,
                "foundwhen": null
            }
        ]
    }


# Node document

    {
        "nodeid": int,
        "code": "s6", // db.get_node_code(nodeid)
        "latitude": float,
        "longitude": float,
        "clue1": string, // "img|"+"https://cdn.asdaad.com" OR "txt|"+"some fantastic clue"
        "clue2": string
    }


# API

## App sends to server when user gets to a node

    {
        "uuid": 018932,   // some unique identifier for the user
        "code": 123,       // the code of the node to verify
    }

## Server sends back to app 

    {
        "text": "",  // whatever the text for the clue of the next node is
        "time": 300  // the calculated time 'par', in seconds
    }