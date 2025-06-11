pipeline {
    agent any

    stages {
        stage('Deploy All Services') {
            steps {
                script {
                    def services = sh(script: "find services -name 'deploy.json'", returnStdout: true).trim().split("\n")

                    for (serviceFile in services) {
                        def config = readJSON file: serviceFile
                        def containerName = config.name
                        def image = config.image
                        def portFlags = config.ports.collect { "-p ${it}" }.join(" ")
                        def envFlags = config.env.collect { "-e ${it.key}=${it.value}" }.join(" ")

                        echo "Deploying ${containerName} with image ${image}"

                        def freeMem = sh(script: "free -m | awk '/Mem:/ { print \$7 }'", returnStdout: true).trim().toInteger()

                        if (freeMem < 500) {
                            echo "⚠️ Not enough memory to deploy ${containerName}"
                            continue
                        }

                        sh """
                            docker stop ${containerName} || true
                            docker rm ${containerName} || true
                            docker pull ${image}
                            docker run -d --name ${containerName} ${portFlags} ${envFlags} ${image}
                        """
                    }
                }
            }
        }
    }
}

