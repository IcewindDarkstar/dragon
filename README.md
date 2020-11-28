# dragon
Discord RestyA inteGratiON bot

## deployment
### dev
1. Execute `run-dev.sh` to build image and run container 'dragon-dev'

### prod
Since we do not use dockerhub, the prod package needs to be moved to the application server manually.

1. Execute `package-prod.sh` to build and package images, env file and run script
2. Move `/tmp/dragon-prod/dragon-prod.tar.gz` to application server
3. Extract files from 'dragon-prod.tar.gz' on application server
4. Execute `run-prod.sh` on application server to load images and run container 'dragon-prod'
