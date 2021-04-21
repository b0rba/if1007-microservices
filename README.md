# IF1007 - Microservices

## Big idea

We have a application called Acaso(aca.so), which is a monolithic and since we all work together there, make sense to do something with it, it is an environment that we are familiar, we have the autonomy to make decision and mold the application, and in the future it is expected to migrate de monolithic to a microservices arcitcherute, so it make sense.

## Opportunities

In Acaso there are some improvement that can be maid, and we list 4 possible services that we could extract:
- Mail Service
- Logging Service
- Payment
- Chat

If we think about feature, the chat is one there is highly needed but is to complex, since there is nothing implemented in the Main application already, same thing with payment.

When we thought about logging, at first was a good idea, but we struggle to find more impact on top of what we already have with the monitoring service on AWS.

Mail Service on the other hand, we had a well define scope, it was simple of extracting from the application compaired to the other. The downs sides were that we need to work on the application to make it ready for the change, we wouldn't use right way on Acaso, and dependeing on that duration, a big part of our work could become absolete.

## Target Opportunity

Based on the previous topic we discussed and decide to move with the Mail Service, it had a consise scope and there was opportunity to explore logging within the application.

## Necessary Resources

We make the Acaso application to be a producer, that send to a priority queue on RabbitMQ, a consumer, that can read from the queue, deserialize, and pass the information to a MailManager that communicate with Sendiblue API.

We will talk about

## Development

We use Scrum to map issues and define sprints. We put everything on Github projects(https://github.com/b0rba/if1007-microservices/projects/1).

The basic MVP features were a basic consumer the could ready from a priority queue, deserialize, pass the payload to the MailManager, that can interpret it and call the Sendinblue Api to send the email correctly.

## Business Logic Discovery

To understand our business logic it is better to explain what kind of email we deal with, currently they are email about the status of a Mentoring, could be the confirmation that you were selected, or that the Mentor will not be able to attend the Mentoring, and all of that has a a mentoring datetime, and we use that datetime to determine the priority of the mail.

The first part is in the producer, Acaso, and publish on queue with a priority equivalent on the urgency, or how close is the mentoring.

We had a consumer that were always listening to the queue, and if there was a mail that had a priority of 200(current day), it was send it immediately, if not, it was send back to the queue. We can see clearly that this is not the best approach, not only create a loop, but if we read instantly the priority logic from the rabbitmq serves nothing.

So we change that, and now the logic is, we can only send 300 email per day, but we can not spend all our emial in the first batch because if a more importante email appear, it would be lost.

So every hour we read 12 mails from the queue, which give the rabbitmq time to sort the payload based on priority, in a way that we consume the most urgent first every time, and at the end of the day, we send the rest of email that we can, also in order.

## Experiment

We have a prometheus monitoring our application, so we can see each payload that is consumed from the queue, and each mail that was successfully sent it or not.

So we produced 400 mocked emails and watched though out the day if the flow was correct.

## Improvements

So what happens if there is a day with a lot of priority mails and we cant send all of them, we have a topic on prometheus about the mails that fails, and we can see the priority, the idea is to notify the manager so he can upgrade the sendinblue data plan or just ignore it. But, this alert is not implemented yet.

We could send a mail from a monitoring that have already passed, in theory the Acaso application will guarantee that this would not happened but, there is no verification on the mail manager side.

If the mail is not send it, because of a simple error, a network error, there is not a backup pipeline to try to resend it, it is lost, but it appears on prometheus.

We create this logic because we can only send 300 mails per day, but when comes the time that we need to upgrade de data plan and we do not have this limit, we basically have to make a new business logic to consume from the queue and send it no the Mail Manager.


---

# Technical Details

## Resources

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [Prometheus](https://prometheus.io/)
- [wait-for-it](https://github.com/vishnubob/wait-for-it)
- [AWS](https://aws.amazon.com/)
- [Dokku](https://dokku.com/) (used only on server)

## External services

- [Sendinblue](https://pt.sendinblue.com/) (email service)

## Architecture

![architecure](microservices_architecture.png)

## Mail Manager

The [mail manager](mail_manager.py) is responsible for receiving the consumer requests and interact with the Sendinblue API. It also provides a method to get the available credits of the account, that indicates how many emails we can send on the actual day.

## Consumer

The [consumer](main.py) is responsible to create two jobs on the process. One is going to run every hoour and send a specific amount of emails according to the environmental variable `SENDINBLUE_MAILS_PER_HOUR`. The other one is going to run at the end of the day, get the amount of available credits on Sendinblue and send emails according to that amount.

## Publisher

The [publisher](main_publisher.py) is responsible to publish messages on the queue. It randomly chooses a template of email to send (between 5 templates) and also randomly create the parameters of that email, for example, the mentor name and the mentoring hour. The main idea of this producer is to have a MVP that proves that the solution is working and also works as a draft for future implementations of publishers.

## Running the project

To run the project you just need to use docker compose. Run:

```bash
docker-compose up
```

### Running the publisher

First, you need to export the correct queue url. If you're running the queue locally with the [docker-compose](docker-compose.yaml), you can just run:

```bash
export QUEUE_SERVICE_URL=amqp://guest:guest@rabbitmq:5672/%2f
```

And to publish, for example, 5 messages, run:

```bash
python main_publisher.py -n 5
```

### RabbitMQ Management

The RabbitMQ service has an UI that provides some monitoring information about the queue. Running locally you can access it in http://localhost:15672

### Prometheus

We use prometheus to track 4 topics.

- `mails_sent` to count how many email requests were succesfully sent;
- `mails_fails` to count how many email requests have failed;
- `payload_template` to count how many emails of each template we have sent (The template id is the label for this topic)
- `payload_priority` to count how many emails of each priority we have sent (The priority is the label for this topic)

Running locally you can access it in http://localhost:9090

## How to deploy

**Prerequisites**

First thing, you need to have [Dokku](https://dokku.com/) installed and configured on your server. Once you have this, you can continue with the following steps:


1. On your server, add the [RabbitMQ plugin](https://github.com/dokku/dokku-rabbitmq) of dokku:

    ```bash
    sudo dokku plugin:install https://github.com/dokku/dokku-rabbitmq.git rabbitmq
    ```

1. Create a RabbitMQ service named rabbitmq:

    ```bash
    dokku rabbitmq:create rabbitmq
    ```

1. Expose the RabbitMQ service so you can access it from outside the server:

    ```bash
    dokku rabbitmq:expose rabbitmq 5672 4369 35197 15672
    ```

1. Now let's setup the prometheus service. Create the app:

    ```bash
    dokku apps:create prometheus
    ```

1. Add a proxy for this service:

    ```bash
    dokku proxy:ports-add prometheus http:80:9090
    ```

1. Set the volume mounts for persistent storage:

    ```bash
    mkdir -p /var/lib/dokku/data/storage/prometheus/{config,data}
    touch /var/lib/dokku/data/storage/prometheus/config/{alert.rules,prometheus.yml}
    chown -R nobody:nogroup /var/lib/dokku/data/storage/prometheus

    dokku storage:mount prometheus /var/lib/dokku/data/storage/prometheus/config:/etc/prometheus
    dokku storage:mount prometheus /var/lib/dokku/data/storage/prometheus/data:/prometheus
    ```
1. Set the prometheus configuration:

    ```bash
    dokku config:set --no-restart prometheus DOKKU_DOCKERFILE_START_CMD="--config.file=/etc/prometheus/prometheus.yml
    --storage.tsdb.path=/prometheus
    --web.console.libraries=/usr/share/prometheus/console_libraries
    --web.console.templates=/usr/share/prometheus/consoles
    --web.enable-lifecycle
    --storage.tsdb.no-lockfile"
    ```

1. Create the configuration file at localtion `/var/lib/dokku/data/storage/prometheus/config/prometheus.yml`:

    ```yml
    # my global config
    global:
      scrape_interval:     15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
      evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
      # scrape_timeout is set to the global default (10s).
    alerting:
      alertmanagers:
      - static_configs:
        - targets:
          - alertmanager:9093
    scrape_configs:
      - job_name: 'prometheus'
        metrics_path: '/metrics'
        static_configs:
          - targets: ['localhost:9090']
      - job_name: 'monitoring'
        metrics_path: '/'
        scrape_interval: 5s
        static_configs:
          - targets: ['<server-ip>:5000']

    ```

    - Replace `<server-ip>` on the target for your real server IP.

1. Pull the docker image:

    ```bash
    sudo docker pull prom/prometheus
    ```

1. Create a tag of that image on dokku:

    ```bash
    sudo docker tag prom/prometheus dokku/prometheus
    ```

1. Deploy the prometheus service:

    ```bash
    dokku tags:deploy prometheus latest
    ```

1. Now let's create the app for the consumer:

    ```bash
    dokku apps:create app
    ```

1. Set the environmental variables:

    ```bash
    dokku config:set app SENDINBLUE_URL='https://api.sendinblue.com/v3' SENDINBLUE_MAILS_PER_HOUR=12 SENDINBLUE_API_KEY='<sendinblue-api-key>' QUEUE_SERVICE_URL='amqp://rabbitmq:<rabbit-mq-password>@<server-ip>:5672/rabbitmq'
    ```

    - You can get the `<sendinblue-api-key>` on your sendinblue dashboard
    - You can check what's the `<rabbit-mq-password>` inside the RabbitMQ url on the attribute dsn when you run the command `dokku rabbitmq:info rabbitmq`

1. Now, on your local machine you need to add the dokku remote to push it using git:

    ```bash
    git remote add dokku dokku@<server-ip>:app
    ```

1. And finally deploy it with:

    ```bash
    git push dokku master
    ```
