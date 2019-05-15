ndoe('DockerEngine'){
    //define properties
    def name = 'heaven'
    def image_name = 'autopi:5000/$name'
    def branch = 'master'
    # 端口号要与dockerfile中定义的一致
    def port = '8093'
    def flower_port = '58089'
    def number = currentBuild.number

    // pull code
    stage 'download code'
    checkout scm

    //build image in specified server
    docker.withServer('tcp://192.168.0.88:5555') {
        stage 'building image'
        docker .build image_name, '--rm .'

        stage 'stop container'
        try {
            sh 'docker stop $name'
            sh 'docker rm $name'
        } catch(error) {}
        try {
            sh 'docker stop $name-celery-beat'
            sh 'docker rm $name-celery-beat'
        } catch(error) {}
        try {
            sh 'docker stop $name-celery-flower'
            sh 'docker rm $name-celery-flower'
        } catch(error) {}

        stage 'start container'
        sh 'docker run --restart=unless-stopped -v /etc/localtime:/etc/localtime:ro --env MODE=TESTING --name $name -d -p $port:$port $image_name'
        sh 'docker run --restart=unless-stopped -v /etc/localtime:/etc/localtime:ro --env MODE=TESTING --name $name-celery-worker -d $image_name celery worker -A tasks.job_task.celery_app -c 2 Q heaven -I INFO -f ./logs/celery_worker.log'
        sh 'docker run --restart=unless-stopped -v /etc/localtime:/etc/localtime:ro --env MODE=TESTING --name $name-celery-beat -d $image_name celery beat -A tasks.job_task.celery_app --pidfile= -I INFO -f ./logs/celery_beat.log'
        sh 'docker run --restart=unless-stopped -v /etc/localtime:/etc/localtime:ro --env MODE=TESTING --name $name-celery-flower -d -p $flower_port:5555 $image_name celery flower -A tasks.job_task.celery_app -I INFO -f ./logs/celery_flower.log'


        stage 'remove old images'
        try{
            sh 'docker rmi $image_name:$number \$(docker images -q -f dangling=true)'
        } catch(error) {}
    }


}