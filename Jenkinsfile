pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
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
                    
                    // Use credentials binding to securely access DOCKER_REGISTRY
                    withCredentials([string(credentialsId: 'docker-registry', variable: 'DOCKER_REGISTRY')]) {
                        def services = ['handler', 'mcp_server', 'nginx']
                        
                        for (service in services) {
                            if (fileExists("services/${service}/Dockerfile")) {
                                echo "Building ${service}..."
                                sh """
                                    cd services/${service}
                                    docker build -t \${DOCKER_REGISTRY}/${service}:latest .
                                    docker build -t \${DOCKER_REGISTRY}/${service}:${BUILD_NUMBER} .
                                """
                            }
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
                    
                    // Use credentials binding for pushing
                    withCredentials([string(credentialsId: 'docker-registry', variable: 'DOCKER_REGISTRY')]) {
                        def services = ['handler', 'mcp_server', 'nginx']
                        
                        for (service in services) {
                            if (fileExists("services/${service}/Dockerfile")) {
                                echo "Pushing ${service}..."
                                sh """
                                    docker push \${DOCKER_REGISTRY}/${service}:latest
                                    docker push \${DOCKER_REGISTRY}/${service}:${BUILD_NUMBER}
                                """
                            }
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
                    withCredentials([
                        sshUserPrivateKey(credentialsId: 'ssh-remote-server-hostinger-deploy', keyFileVariable: 'SSH_KEY'),
                        string(credentialsId: 'remote-user', variable: 'REMOTE_USER'),
                        string(credentialsId: 'remote-hostinger-deploy-ip', variable: 'REMOTE_HOST'),
                        string(credentialsId: 'docker-registry', variable: 'DOCKER_REGISTRY')
                    ]) {
                        // Create directory and copy files to remote server
                        sh '''
                            # Create directory first
                            ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "sudo mkdir -p /opt/app && sudo chown ${REMOTE_USER}:${REMOTE_USER} /opt/app"
                            
                            # Copy files
                            scp -i "$SSH_KEY" -o StrictHostKeyChecking=no docker-compose.yml "$REMOTE_USER@$REMOTE_HOST:/opt/app/"
                            scp -i "$SSH_KEY" -o StrictHostKeyChecking=no deploy-script.sh "$REMOTE_USER@$REMOTE_HOST:/opt/app/"
                        '''
                        
                        // Run deployment script on remote server
                        sh '''
                            ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "
                                cd /opt/app
                                chmod +x deploy-script.sh
                                ./deploy-script.sh '$DOCKER_REGISTRY' '$REMOTE_HOST'
                            "
                        '''
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
                docker image prune -a -f
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