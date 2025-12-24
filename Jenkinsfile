pipeline {
    agent {
        label 'mohan'
    }
    parameters {
        string (
            defaultValue: '1.0-1', 
            description: 'Please provide rpm version to build the rpm', 
            name: 'rpm_version'
        )
    }
    environment {
        artifactory_url = "http://44.247.49.164:8082/artifactory"
        repo_name = "rpm.common.packages"
        rpm_src_path = "rpmbuild/RPMS/noarch"
        sonar_url = "http://35.166.123.72:9000/"
    }
    tools {
        jdk 'JDK17'
        //maven 'maven3'
    }
    stages {
        stage('Sonar report') {
            steps {
                withCredentials([string(credentialsId: 'sonar_token', variable: 'SONAR_TOKEN')]) {
                    script{
                        sh """
                            mvn clean verify sonar:sonar \
                                -s settings.xml \
                                -DskipTests \
                                -Dcheckstyle.skip=true \
                                -Dspring-javaformat.skip=true \
                                -Dnohttp.check.skip=true \
                                -Dsonar.projectBaseDir=. \
                                -Dsonar.host.url=$sonar_url \
                                -Dsonar.login=$SONAR_TOKEN 
                            """
                    }
                }
            }
        }
        stage('Build the package') {
            steps {
                script {
                    sh """
                        mvn clean install \
                            -DskipTests \
                            -Dcheckstyle.skip=true \
                            -Dspring-javaformat.skip=true \
                            -Dnohttp.check.skip=true \
                    """
                }
            }
        }
        stage('Build the RPM') {
            steps {
                script {
                    def version = params.rpm_version.split('-')

                    if (version.size() != 2) {
                        error "Invalid rpm_version format. Expected <version>-<release> (e.g. 1.0-1)"
                    }

                    env.APP_VERSION = version[0]
                    env.BUILD_NO    = version[1]

                    sh """
                        rm -rf ${WORKSPACE}/rpmbuild
                        mkdir -p ${WORKSPACE}/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
                        mv ${WORKSPACE}/target/*.jar ${WORKSPACE}/target/petclinic.jar
                        cp ${WORKSPACE}/target/petclinic.jar ${WORKSPACE}/rpmbuild/SOURCES/
                        cp ${WORKSPACE}/rpm_dependencies/{application.properties,petclinic.service} ${WORKSPACE}/rpmbuild/SOURCES/
                        cp ${WORKSPACE}/rpm_dependencies/petclinic.spec ${WORKSPACE}/rpmbuild/SPECS/
                        sed -i "s/^Version:.*/Version: ${APP_VERSION}/" ${WORKSPACE}/rpmbuild/SPECS/petclinic.spec
                        sed -i "s/^Release:.*/Release: ${BUILD_NO}%{?dist}/" ${WORKSPACE}/rpmbuild/SPECS/petclinic.spec
                        rpmbuild -ba ${WORKSPACE}/rpmbuild/SPECS/petclinic.spec \
                            --define "_topdir ${WORKSPACE}/rpmbuild"
                        ls -la ${WORKSPACE}/rpmbuild/RPMS
                    """
                }
            }
        }
        stage('Artifact upload') {
            steps {
                withCredentials([string(credentialsId: 'arti_token', variable: 'ARTI_TOKEN')]) {
                    script{
                        sh '''
                            set -e
                            RPM_FILE=$(ls ${WORKSPACE}/${rpm_src_path}/*.rpm)
                            curl -f \
                            -H "Authorization: Bearer $ARTI_TOKEN" \
                            -X PUT \
                            -T "$RPM_FILE" \
                            "$artifactory_url/$repo_name/$(basename "$RPM_FILE")"
                        '''
                    }
                }
            }
        }
    }
    post {
        always {
            echo '🧹 Cleaning workspace'
            cleanWs()
        }
    }
}
