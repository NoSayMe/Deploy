pipeline {
    agent any

    stages {
        stage('Deploy Changed Services') {
            steps {
                script {
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
                        def containerName = config.name
                        def image = config.image
                        def portFlags = config.ports.collect { "-p ${it}" }.join(" ")
                        def envFlags = config.env.collect { "-e ${it.key}=${it.value}" }.join(" ")

                        echo "🚀 Deploying ${containerName} with image ${image}"

                        def freeMem = sh(script: "free -m | awk '/Mem:/ { print \$7 }'", returnStdout: true).trim().toInteger()

                        if (freeMem < 500) {
                            echo "⚠️ Not enough memory to deploy ${containerName}"
                            continue
                        }

                        try {
                            sh """
                                docker stop ${containerName} || true
                                docker rm ${containerName} || true
                                docker pull ${image}
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

