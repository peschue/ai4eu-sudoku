# define the versions to be used for docker images (building, running, pushing)

export GUI_IMAGE_VERSION=1.3
export EVALUATOR_IMAGE_VERSION=1.3
export ASPSOLVER_IMAGE_VERSION=1.0

# remote repository for pushing images

# you need to login first! (accounts given by Martin, or you use another registry, e.g., dockerhub)
# docker login cicd.ai4eu-dev.eu:7444
export REMOTE_REPO=cicd.ai4eu-dev.eu:7444
