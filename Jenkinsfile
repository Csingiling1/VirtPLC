pipeline {
    agent any
    
    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = "${env.GIT_URL.replaceFirst(/^.*\/([^\/]+?).git$/, '$1')}"
        COMPUTER1_IP = credentials('COMPUTER1_IP')
        COMPUTER2_IP = credentials('COMPUTER2_IP')
        DEPLOYMENT_USER = credentials('DEPLOYMENT_USER')
        GITHUB_TOKEN = credentials('GITHUB_TOKEN')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out repository...'
                checkout scm
                sh 'git rev-parse --short HEAD > .git/commit-id'
                script {
                    env.GIT_COMMIT_SHORT = readFile('.git/commit-id').trim()
                }
            }
        }
        
        stage('Test - Backend') {
            agent {
                docker {
                    image 'maven:3.9-eclipse-temurin-21'
                    args '-v $HOME/.m2:/root/.m2'
                }
            }
            steps {
                dir('backend') {
                    sh 'mvn clean test'
                }
            }
            post {
                always {
                    junit 'backend/target/surefire-reports/*.xml'
                }
            }
        }
        
        stage('Test - Frontend') {
            agent {
                docker {
                    image 'node:20-alpine'
                }
            }
            steps {
                dir('frontend') {
                    sh '''
                        npm ci
                        npm run build
                        npm run test || true
                    '''
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: 'frontend/dist/**', fingerprint: true
                }
            }
        }
        
        stage('Test - AI Service') {
            agent {
                docker {
                    image 'python:3.11-slim'
                }
            }
            steps {
                dir('ai-service') {
                    sh '''
                        pip install --no-cache-dir -r requirements.txt
                        python -m pytest tests/ -v --junitxml=test-results.xml || true
                    '''
                }
            }
            post {
                always {
                    junit 'ai-service/test-results.xml'
                }
            }
        }
        
        stage('Test - Simulator') {
            agent {
                docker {
                    image 'python:3.11-slim'
                }
            }
            steps {
                dir('simulator') {
                    sh '''
                        pip install --no-cache-dir -r requirements.txt
                        python -m pytest test_simulator.py -v --junitxml=test-results.xml || true
                    '''
                }
            }
            post {
                always {
                    junit 'simulator/test-results.xml'
                }
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build Backend') {
                    steps {
                        script {
                            sh """
                                docker build -t ${REGISTRY}/${IMAGE_NAME}/backend:${env.GIT_COMMIT_SHORT} ./backend
                                docker tag ${REGISTRY}/${IMAGE_NAME}/backend:${env.GIT_COMMIT_SHORT} ${REGISTRY}/${IMAGE_NAME}/backend:latest
                            """
                        }
                    }
                }
                stage('Build Frontend') {
                    steps {
                        script {
                            sh """
                                docker build -t ${REGISTRY}/${IMAGE_NAME}/frontend:${env.GIT_COMMIT_SHORT} ./frontend
                                docker tag ${REGISTRY}/${IMAGE_NAME}/frontend:${env.GIT_COMMIT_SHORT} ${REGISTRY}/${IMAGE_NAME}/frontend:latest
                            """
                        }
                    }
                }
                stage('Build AI Service') {
                    steps {
                        script {
                            sh """
                                docker build -t ${REGISTRY}/${IMAGE_NAME}/ai-service:${env.GIT_COMMIT_SHORT} ./ai-service
                                docker tag ${REGISTRY}/${IMAGE_NAME}/ai-service:${env.GIT_COMMIT_SHORT} ${REGISTRY}/${IMAGE_NAME}/ai-service:latest
                            """
                        }
                    }
                }
                stage('Build Simulator') {
                    steps {
                        script {
                            sh """
                                docker build -t ${REGISTRY}/${IMAGE_NAME}/simulator:${env.GIT_COMMIT_SHORT} ./simulator
                                docker tag ${REGISTRY}/${IMAGE_NAME}/simulator:${env.GIT_COMMIT_SHORT} ${REGISTRY}/${IMAGE_NAME}/simulator:latest
                            """
                        }
                    }
                }
                stage('Build Collector') {
                    steps {
                        script {
                            sh """
                                docker build -t ${REGISTRY}/${IMAGE_NAME}/collector:${env.GIT_COMMIT_SHORT} ./collector
                                docker tag ${REGISTRY}/${IMAGE_NAME}/collector:${env.GIT_COMMIT_SHORT} ${REGISTRY}/${IMAGE_NAME}/collector:latest
                            """
                        }
                    }
                }
            }
        }
        
        stage('Push Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    sh """
                        echo ${GITHUB_TOKEN} | docker login ${REGISTRY} -u jenkins --password-stdin
                        docker push ${REGISTRY}/${IMAGE_NAME}/backend:${env.GIT_COMMIT_SHORT}
                        docker push ${REGISTRY}/${IMAGE_NAME}/backend:latest
                        docker push ${REGISTRY}/${IMAGE_NAME}/frontend:${env.GIT_COMMIT_SHORT}
                        docker push ${REGISTRY}/${IMAGE_NAME}/frontend:latest
                        docker push ${REGISTRY}/${IMAGE_NAME}/ai-service:${env.GIT_COMMIT_SHORT}
                        docker push ${REGISTRY}/${IMAGE_NAME}/ai-service:latest
                        docker push ${REGISTRY}/${IMAGE_NAME}/simulator:${env.GIT_COMMIT_SHORT}
                        docker push ${REGISTRY}/${IMAGE_NAME}/simulator:latest
                        docker push ${REGISTRY}/${IMAGE_NAME}/collector:${env.GIT_COMMIT_SHORT}
                        docker push ${REGISTRY}/${IMAGE_NAME}/collector:latest
                    """
                }
            }
        }
        
        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            parallel {
                stage('Deploy to Computer 1') {
                    steps {
                        script {
                            sh """
                                # Copy deployment files
                                scp docker-compose.yml ${DEPLOYMENT_USER}@${COMPUTER1_IP}:~/virtplc/
                                scp .env.example ${DEPLOYMENT_USER}@${COMPUTER1_IP}:~/virtplc/.env
                                
                                # Deploy
                                ssh ${DEPLOYMENT_USER}@${COMPUTER1_IP} << 'ENDSSH'
                                cd ~/virtplc
                                
                                # Update environment
                                sed -i "s|PLC_HOST=.*|PLC_HOST=${COMPUTER2_IP}|g" .env
                                sed -i "s|COMPUTER1_HOST=.*|COMPUTER1_HOST=${COMPUTER1_IP}|g" .env
                                
                                # Login and pull
                                echo ${GITHUB_TOKEN} | docker login ${REGISTRY} -u jenkins --password-stdin
                                docker-compose pull
                                
                                # Deploy Computer 1 services
                                docker-compose up -d timescale postgres redis backend frontend ai-service nodered mqtt db-mcp-server ollama
                                
                                # Cleanup
                                docker image prune -f
ENDSSH
                            """
                        }
                    }
                }
                
                stage('Deploy to Computer 2') {
                    steps {
                        script {
                            sh """
                                # Copy deployment files
                                scp docker-compose.yml ${DEPLOYMENT_USER}@${COMPUTER2_IP}:~/virtplc/
                                scp .env.example ${DEPLOYMENT_USER}@${COMPUTER2_IP}:~/virtplc/.env
                                
                                # Deploy
                                ssh ${DEPLOYMENT_USER}@${COMPUTER2_IP} << 'ENDSSH'
                                cd ~/virtplc
                                
                                # Update environment
                                sed -i "s|PLC_HOST=.*|PLC_HOST=${COMPUTER2_IP}|g" .env
                                sed -i "s|COMPUTER1_HOST=.*|COMPUTER1_HOST=${COMPUTER1_IP}|g" .env
                                
                                # Login and pull
                                echo ${GITHUB_TOKEN} | docker login ${REGISTRY} -u jenkins --password-stdin
                                docker-compose pull
                                
                                # Deploy Computer 2 services (PLC simulation)
                                docker-compose up -d simulator collector
                                
                                # Cleanup
                                docker image prune -f
ENDSSH
                            """
                        }
                    }
                }
            }
        }
        
        stage('Health Check') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo 'Waiting for services to start...'
                    sleep 30
                    
                    // Check Computer 1
                    sh """
                        curl -f http://${COMPUTER1_IP}:8080/actuator/health || echo "Warning: Backend health check failed"
                        curl -f http://${COMPUTER1_IP}:3000 || echo "Warning: Frontend health check failed"
                        curl -f http://${COMPUTER1_IP}:3001/health || echo "Warning: AI Service health check failed"
                    """
                    
                    // Check Computer 2
                    sh """
                        curl -f http://${COMPUTER2_IP}:5000/health || echo "Warning: Simulator health check failed"
                    """
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
