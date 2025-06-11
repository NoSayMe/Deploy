pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "nginx:latest"     // Change if you want dynamic behavior
        CONTAINER_NAME = "Deployer"   // Or make it dynamic via Git commit or metadata
    }

    stages {
        stage('Check System Resources') {
            steps {
                script {
                    def mem = sh(script: "free -m | awk '/Mem:/ { print \$7 }'", returnStdout: true).trim()
                    echo "Free memory: ${mem} MB"

                    if (mem.toInteger() < 500) {
                        error("Not enough memory to deploy.")
                    }
                }
            }
        }

        stage('Deploy Container') {
            steps {
                sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker pull ${DOCKER_IMAGE}
                    docker run -d --name ${CONTAINER_NAME} ${DOCKER_IMAGE}
                """
            }
        }
    }

    post {
        success {
            echo "✅ Deployed ${DOCKER_IMAGE} as ${CONTAINER_NAME}"
        }
        failure {
            echo "❌ Deployment failed"
        }
    }
}

