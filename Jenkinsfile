pipeline {
    agent any
    
    environment {
        // 🔐 All sensitive data stored securely in Jenkins
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        REMOTE_HOST = credentials('remote-host')
        REMOTE_USER = credentials('remote-user')
        DOCKER_REGISTRY = credentials('docker-registry')
    }
    
    stages {
        stage('1. Pull Repo') {
            steps {
                echo '📥 Pulling latest code...'
                checkout scm
            }
        }
        
        stage('2. Build Images') {
            steps {
                script {
                    echo '🏗️ Building Docker images...'
                    
                    // Build each service that has build: true
                    def services = ['handler', 'mcp_server', 'nginx']
                    
                    for (service in services) {
                        if (fileExists("services/${service}/Dockerfile")) {
                            echo "Building ${service}..."
                            sh """
                                cd services/${service}
                                docker build -t ${DOCKER_REGISTRY}/${service}:latest .
                                docker build -t ${DOCKER_REGISTRY}/${service}:${BUILD_NUMBER} .
                            """
                        }
                    }
                }
            }
        }
        
        stage('3. Push to DockerHub') {
            steps {
                script {
                    echo '📤 Pushing images to DockerHub...'
                    
                    // Login to DockerHub using secure credentials
                    sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                    
                    // Push images
                    def services = ['handler', 'mcp_server', 'nginx']
                    
                    for (service in services) {
                        if (fileExists("services/${service}/Dockerfile")) {
                            echo "Pushing ${service}..."
                            sh """
                                docker push ${DOCKER_REGISTRY}/${service}:latest
                                docker push ${DOCKER_REGISTRY}/${service}:${BUILD_NUMBER}
                            """
                        }
                    }
                }
            }
        }
        
        stage('4. Deploy to Remote Server') {
            steps {
                script {
                    echo '🚀 Deploying to remote server...'
                    
                    // 🔐 Use SSH credentials securely
                    sshagent(['ssh-remote-server-1-Azure']) {
                        // Copy files to remote server
                        sh """
                            scp -o StrictHostKeyChecking=no docker-compose.yml ${REMOTE_USER}@${REMOTE_HOST}:/opt/app/
                            scp -o StrictHostKeyChecking=no deploy-script.sh ${REMOTE_USER}@${REMOTE_HOST}:/opt/app/
                        """
                        
                        // Run deployment script on remote server
                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} '
                                cd /opt/app
                                chmod +x deploy-script.sh
                                ./deploy-script.sh ${DOCKER_REGISTRY} ${REMOTE_HOST}
                            '
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up local images...'
            sh '''
                # Remove local images to save space
                docker image prune -f
                docker logout
            '''
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}