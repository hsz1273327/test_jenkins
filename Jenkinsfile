pipeline {
  agent none
  environment {
    sendmail = 'yes'
    version = '0.0.2'
  }
  stages {
    stage('Test') {
      when {
        anyOf {
          branch 'test'
          branch 'dev'
          branch 'master'
        }
      }
      agent {
        docker {
          image 'python:3.6'
        }
      }
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          echo 'install requirement'
          sh 'python -m pip install --user -r requirements.txt'
          echo 'start test'
          sh 'python -m coverage run --source=test_drone -m unittest discover -v -s .'
          echo 'send report'
          sh 'python -m coverage html -d report/coverage'
        }
      }
      post {
        success {
          publishHTML([
            allowMissing: true, 
            alwaysLinkToLastBuild: true, 
            keepAll: true, 
            reportDir: 'report/coverage', 
            reportFiles: 'index.html', 
            reportName: 'Coverage Report - Unit Test'
            ])
          emailext body: "${git_url}:${git_branch} test success",
            subject: "${git_url}:${git_branch} test success",
            to: "hsz1273327@gmail.com"
        }
        failure {
          emailext body: "${git_url}:${git_branch} test failure",
            subject: "${git_url}:${git_branch} test failure",
            to: "hsz1273327@gmail.com"
        }
      }
    }
    stage('Release') {
      when {
        branch "release-*"
      }
      agent any
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'docker build -t hsz1273327/test_drone:latest -t hsz1273327/test_drone:'+version+' .'
          sh 'docker login -u hsz1273327 -p hsz881224'
          sh 'docker push hsz1273327/test_drone'
        }
      }
    }
  }
  post{
    success {
      script {
        if (sendmail == 'yes') {
          emailext body: '''pipelie succeed:
          构建名称:${JOB_NAME}
          构建结果:${BUILD_STATUS}
          构建编号：${BUILD_NUMBER}
          GIT 地址：${git_url}
          GIT 分支：${git_branch}
        ''',
          subject: 'Jenkins build ${PROJECT_NAME} succeed', 
          to: 'hsz1273327@gmail.com'
        }
      }
    }
    failure {
      script {
        if (sendmail == 'yes') {
          emailext body: '''pipelie failure:
            构建名称:${JOB_NAME}
            构建结果:${BUILD_STATUS}
            构建编号：${BUILD_NUMBER}
            GIT 地址：${git_url}
            GIT 分支：${git_branch}
            ${BUILD_LOG}''',
            subject: 'Jenkins build ${PROJECT_NAME} is ${currentBuild.result}: ${env.JOB_NAME} #${env.BUILD_NUMBER}',
            to: 'hsz1273327@gmail.com'
        }
      }
    }
  }
}