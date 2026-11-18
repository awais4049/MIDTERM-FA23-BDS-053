pipeline {
    agent any
    options { timestamps(); disableConcurrentBuilds() }
    triggers { githubPush() }
    environment {
        IMAGE = 'midterm-app'
        CONTAINER = 'midterm-app'
        HUB_REPO = 'midterm-fa23-bds-053'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Record previous model metrics') {
            steps {
                sh '''
                    mkdir -p reports
                    docker exec ${CONTAINER} cat /app/artifacts/metrics.json > reports/old_metrics.json 2>/dev/null || echo '{}' > reports/old_metrics.json
                    cat reports/old_metrics.json
                '''
            }
        }
        stage('Test') {
            steps {
                sh 'docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$WORKSPACE":/w -w /w python:3.11-slim sh -c "pip install -q -r requirements.txt pytest && pytest -q -p no:cacheprovider"'
            }
        }
        stage('Build image (trains model)') {
            steps {
                sh 'docker build -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest --build-arg GIT_SHA=${GIT_COMMIT} .'
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER} || true
                    docker run -d --name ${CONTAINER} --restart unless-stopped -p 8000:8000 ${IMAGE}:latest
                    for i in $(seq 1 30); do
                        curl -fs http://localhost:8000/metrics > reports/new_metrics.json && break
                        sleep 2
                    done
                    test -s reports/new_metrics.json
                    cat reports/new_metrics.json
                '''
            }
        }
        stage('Push to Docker Hub') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                        sh '''
                            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                            docker tag ${IMAGE}:latest ${DH_USER}/${HUB_REPO}:latest
                            docker tag ${IMAGE}:latest ${DH_USER}/${HUB_REPO}:${BUILD_NUMBER}
                            docker push ${DH_USER}/${HUB_REPO}:latest
                            docker push ${DH_USER}/${HUB_REPO}:${BUILD_NUMBER}
                        '''
                    }
                }
            }
        }
    }
    post {
        success {
            withCredentials([usernamePassword(credentialsId: 'gmail-smtp', usernameVariable: 'SMTP_USER', passwordVariable: 'SMTP_PASS')]) {
                sh 'python3 send_email.py SUCCESS'
            }
        }
        failure {
            withCredentials([usernamePassword(credentialsId: 'gmail-smtp', usernameVariable: 'SMTP_USER', passwordVariable: 'SMTP_PASS')]) {
                sh 'python3 send_email.py FAILED'
            }
        }
    }
}
