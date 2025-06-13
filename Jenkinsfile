pipeline {
    agent any  // Use any available Jenkins agent (in this case, the single VPS node)

    stages {
        stage('Deploy Changed Services') {
            steps {
                script {
                    // 🧠 Identify services that have changed in the last commit
                    def changedServices = sh(
                        script: "git diff --name-only HEAD~1 HEAD | grep '^services/' | cut -d/ -f2 | uniq",
                        returnStdout: true
                    ).trim().split("\n").findAll { it }

                    // 🛑 If no services changed, exit early
                    if (changedServices.isEmpty()) {
                        echo "No service changes detected. Skipping deployment."
                        currentBuild.result = 'SUCCESS'
                        return
                    }

                    // 📡 Ensure a dedicated network exists for inter-service communication
                    sh 'docker network create ci-network || true'

                    // 🔁 Iterate over each changed service
                    for (service in changedServices) {
                        def serviceDir = "services/${service}"
                        def serviceFile = "${serviceDir}/deploy.json"

                        // 🚫 Skip if no deploy.json present
                        if (!fileExists(serviceFile)) {
                            echo "⚠️ Skipping ${service}: no deploy.json found"
                            continue
                        }

                        // 📄 Load service configuration
                        def config = readJSON file: serviceFile
                        def image = config.image
                        def containerName = service
                        def portFlags = config.ports.collect { "-p ${it}" }.join(" ")

                        // ✅ Quote environment values to handle spaces or special characters
                        def envFlags = config.containsKey('env') ? config.env.collect { "-e \"${it.key}=${it.value}\"" }.join(" ") : ''

                        // 💾 Mount host volumes when defined
                        def volumeFlags = ''
                        if (config.containsKey('volumes')) {
                            volumeFlags = config.volumes.collect { "-v ${it.key}:${it.value}" }.join(' ')
                        }

                        // 📦 Start any container dependencies if defined
                        if (config.containsKey('depends_on')) {
                            for (dep in config.depends_on) {
                                def running = sh(script: "docker ps --filter 'name=${dep}' -q", returnStdout: true).trim()
                                if (!running) {
                                    echo "🔗 Starting dependency ${dep}"
                                    sh "docker start ${dep} || true"
                                }
                            }
                        }

                        // 🏗️ Determine if the image needs to be built locally
                        def shouldBuild = config.containsKey("build") && config.build == true

                        echo "🚀 Deploying ${containerName} with image ${image}"

                        // 📉 Check if enough memory is available before deploying
                        def freeMem = sh(script: "free -m | awk '/Mem:/ { print \$7 }'", returnStdout: true).trim().toInteger()
                        if (freeMem < 500) {
                            echo "⚠️ Not enough memory to deploy ${containerName} (available: ${freeMem}MB)"
                            continue
                        }

                        try {
                            // 🔨 Build the image locally if specified
                            if (shouldBuild) {
                                echo "🔧 Building image locally from ${serviceDir}"
                                sh "docker buildx build --load -t ${image} ${serviceDir}"
                            } else {
                                // 🔄 Pull the image from registry only if not already present
                                def imageExists = sh(script: "docker images -q ${image}", returnStdout: true).trim()
                                if (!imageExists) {
                                    echo "📦 Pulling image ${image}"
                                    sh "docker pull ${image}"
                                } else {
                                    echo "✅ Image ${image} found locally, skipping pull"
                                }
                            }

                            // 🧼 Stop and remove old container (if exists), then run new one
                            sh """
                                docker stop ${containerName} || true
                                docker rm ${containerName} || true
                                echo "🛠️ Running container ${containerName} from image ${image}"
                                docker run -d --restart unless-stopped --name ${containerName} --network ci-network ${portFlags} ${envFlags} ${volumeFlags} ${image}
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

