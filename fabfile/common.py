from fabric.decorators import task
from fabric.operations import get, run, sudo
from fabric.state import env


@task
def gunicorn_logs():
    run("tail -f /var/log/gunicorn/wodify.log")


@task
def celery_logs():
    run("tail -f /var/log/celery/wodify.log")


@task
def git_pull():
    """
    """
    run("cd ~/{}/; git pull".format(env.repo_name))


@task
def build_front():
    """
    """
    run("cd ~/{}/front/; npm install; npm run build;".format(env.repo_name))

@task
def restart():
    run("cd ~/{} && . ./run.sh".format(env.repo_name))
    update_supervisor()
    update_nginx()
@task
def update_supervisor():
    sudo("cp -r ~/{}/configs/supervisor/* /etc/supervisor/conf.d".format(env.repo_name))
    sudo("""supervisorctl reread;
            supervisorctl restart {};
            supervisorctl restart celery;
            supervisorctl update;
            supervisorctl status;
        """.format(env.repo_name))


@task
def update_nginx(first_run=0):
    sudo("cp ~/{0}/configs/nginx/{0}.conf /etc/nginx/sites-available".format(env.repo_name))
    if first_run:
        sudo("ln -s /etc/nginx/sites-available/{0}.conf /etc/nginx/sites-enabled/{0}.conf".format(env.repo_name))
    sudo("service nginx restart")


@task
def restart():
    run("cd ~/{} && . ./run.sh".format(env.repo_name))
    update_supervisor()
    update_nginx()


@task
def first_run():
    sudo("service nginx stop")
    run("mkdir -p ~/letsencrypt;mkdir -p ~/letsencrypt/work;mkdir -p ~/letsencrypt/logs;mkdir -p ~/letsencrypt/cron;")
    sudo("certbot certonly -c ~/{0}/configs/letsencrypt/config.ini -n --config-dir ~/{0}/configs/letsencrypt/ --work-dir ~/letsencrypt/work/ --logs-dir ~/letsencrypt/logs/"
         .format(env.repo_name))
    sudo("chmod -R 775 ~/{0}/configs/letsencrypt/".format(env.repo_name))
    run("openssl dhparam -out ~/{0}/configs/letsencrypt/ssl-dhparams.pem 2048".format(env.repo_name))
    run("chmod 600 ~/{0}/configs/keys/id_rsa;cd ~/{0};git add ./configs/letsencrypt/;git commit -m \"updated keys\";GIT_SSH_COMMAND=\"ssh -i ~/{0}/configs/keys/id_rsa -o StrictHostKeyChecking=no\" git push {1};"
        .format(env.repo_name, env.repository_ssh))
    run("echo \" 0 9 1,15 * * ~/letsencrypt/cron/cronscript.sh\" > ~/letsencrypt/cron/crontab")
    run("""
        echo \"
        sudo service nginx stop;
        certbot renew -n --config-dir ~/{0}/configs/letsencrypt/ --work-dir ~/letsencrypt/work/ --logs-dir ~/letsencrypt/logs/;
        chmod -R 775 ~/{0}/configs/letsencrypt/;
        chmod 600 ~/{0}/configs/keys/id_rsa;
        cd ~/{0};
        git add ./configs/letsencrypt/;
        git commit -m \\\\\"updated ssl-certificates\\\\\";
        GIT_SSH_COMMAND=\\\\\"ssh -i ~/{0}/configs/keys/id_rsa -o StrictHostKeyChecking=no\\\\\" git push {1};
        sudo service nginx start;
        \" > ~/letsencrypt/cron/cronscript.sh
        """
        .format(env.repo_name, env.repository_ssh))
    run("chmod +x ~/letsencrypt/cron/cronscript.sh")
    run("crontab ~/letsencrypt/cron/crontab")
    update_nginx()
