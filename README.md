# image_inventory
A utility to fetch image definitions from kubernetes, rancher, etc.

The best way to use this is to use it in Docker:

    docker build -t imageinv .
    
Then run in bash -- or fix up to use with cron:

```
#> docker run --rm -it \
   -e RANCHER_ACCESS_KEY="***user_key***"  \
   -e RANCHER_SECRET_KEY="***user_secret***"  \
   -e RANCHER_URL="https://rancher.local/v2-beta"  \
   -e ANCHORE_CLI_USER=admin \
   -e ANCHORE_CLI_PASS=*****  \
   -e ANCHORE_CLI_URL=http://anchore-engine.local:8228/v1 \
   imageenv /bin/bash
```

The previous snip example is for testing rancher images. Note that Rancher requires /v1 or /v2-beta for the API.

//TODO replace that `/bin/bash` with a proper entrypoint that runs the whole output
//TODO k8s example
