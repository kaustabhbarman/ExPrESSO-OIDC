# ESPRESSO
## Requirements
- Docker with Docker compose
## Setup
At the command prompt, 

`docker compose up`

This will setup the various services as following:

- `localhost:8000` as OIDF Server  
- `localhost:8001` as IdentityProvider Server  
- `localhost:8002` as RelyingParty Server  

it also migrates the tables and creates a super user:

user: admin  
password: snet2025

## JS Config
Relyingparty->temapltes->landing.html must have correct credentails:
```

var clientInfo = {
    // client id just to bypass library validation
    client_id : '002084',
    redirect_uri : 'http://localhost:8002/welcome/',
    proof: "extra-id-for-express-framework"
    // add cryptographic key information here

};
```
