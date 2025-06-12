pipeline {
    agent any

    stages {
        stage('Deploy Changed Services') {
            steps {
                script {
                    // Detect changed services in the last commit
                    def changedServices = sh(
                        script: "git diff --name-only HEAD~1 HEAD | grep '^services/' | cut -d/ -f2 | uniq",
                        returnStdout: true
                    ).trim().split("\n").findAll { it }

                    if (changedServices.isEmpty()) {
                        echo "No service changes detected. Skipping deployment."
                        currentBuild.result = 'SUCCESS'
                        return
                    }

                    for (service in changedServices) {
                        def serviceFile = "services/${service}/deploy.json"
                        if (!fileExists(serviceFile)) {
                            echo "⚠️ Skipping ${service}: no deploy.json found"
                            continue
                        }

                        def config = readJSON file: serviceFile
                        def image = config.image
                        def containerName = service // Use folder name for container
                        def portFlags = config.ports.collect { "-p ${it}" }.join(" ")
                        def envFlags = config.env.collect { "-e ${it.key}=${it.value}" }.join(" ")

                        echo "🚀 Deploying ${containerName} with image ${image}"

                        // Check available memory
                        def freeMem = sh(script: "free -m | awk '/Mem:/ { print \$7 }'", returnStdout: true).trim().toInteger()
                        if (freeMem < 500) {
                            echo "⚠️ Not enough memory to deploy ${containerName} (available: ${freeMem}MB)"
                            continue
                        }

                        try {
                            // Check if image is local; pull only if not
                            def imageExists = sh(script: "docker images -q ${image}", returnStdout: true).trim()
                            if (!imageExists) {
                                echo "📦 Pulling image ${image}"
                                sh "docker pull ${image}"
                            } else {
                                echo "✅ Image ${image} found locally, skipping pull"
                            }

                            // Stop, remove, and redeploy the container
                            sh """
                                docker stop ${containerName} || true
                                docker rm ${containerName} || true
                                docker run -d --restart unless-stopped --name ${containerName} ${portFlags} ${envFlags} ${image}
                            """
                            echo "✅ ${containerName} deployed"
                        } catch (err) {
                            echo "❌ Deployment failed for ${containerName}: ${err}"
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ All changed services deployed successfully.'
        }
        failure {
            echo '❌ One or more deployments failed.'
        }
    }
}

